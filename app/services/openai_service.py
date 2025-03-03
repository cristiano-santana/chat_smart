import yaml
import re
from openai import OpenAI
from flask import current_app

def init_openai():
    """
    Inicializa a chave da API da OpenAI a partir das configurações da aplicação.
    """
    print("Inicializando OpenAI...")

def upload_file_yaml(file_path, file_name, schema):
    # Lendo o arquivo YAML
    with open(file_path, "r") as file:
        yaml_content = file.read()

    # Converter o dicionário para string YAML
    schema_yaml = yaml.dump(schema, default_flow_style=False, allow_unicode=True)

    # Ajustar indentação para se alinhar ao nível correto no YAML original
    schema_yaml = "\n".join(["            " + line if line else line for line in schema_yaml.splitlines()])

    # Substituir {schema} no conteúdo do YAML
    yaml_content = yaml_content.replace("{schema}", schema_yaml)

    # Converter o conteúdo para um dicionário Python
    config = yaml.safe_load(yaml_content)

    return config[file_name]

def extract_query_from_text(resposta, pergunta):
    """
    Extrai o bloco de código SQL de um texto com explicações.

    Args:
        resposta (str): Resposta do modelo que contém as queries SQL dentro de blocos de código.
        pergunta (str): Pergunta do usuario.

    Returns:
        str: A primeira query SQL extraída do bloco de código.
             Retorna `None` se nenhuma query for encontrada.
    """
    pattern = r"```sql\s*\n?(.*?)```"
    matches = re.findall(pattern, resposta, flags=re.DOTALL | re.IGNORECASE)
    
    if matches:
        consulta_sql = matches[0].strip()
        current_app.logger.info(f"PERGUNTA: {pergunta}")
        current_app.logger.info(f"RESPOSTA: {resposta}")
        current_app.logger.info(f"QUERY: {consulta_sql}.")
        return consulta_sql
    else:
        current_app.logger.error(f"Nenhuma query SQL encontrada na resposta do modelo: {resposta}.")
        return None

def extract_all_queries_from_the_text(resposta, pergunta):
    """
    Extrai todos os blocos de código SQL de um texto com explicações.

    Args:
        resposta (str): Resposta do modelo que contém as queries SQL dentro de blocos de código.
        pergunta (str): Pergunta do usuario.

    Returns:
        list: Lista de queries SQL extraídas dos blocos de código.
              Retorna lista vazia se nenhuma query for encontrada.
    """
    pattern = r"```sql\s*\n?(.*?)```"
    matches = re.findall(pattern, resposta, flags=re.DOTALL | re.IGNORECASE)
    
    if matches:
        consultas_sql = [match.strip() for match in matches]
        current_app.logger.info(f"PERGUNTA: {pergunta}")
        current_app.logger.info(f"RESPOSTA: {resposta}")
        current_app.logger.info(f"QUERIES: {consultas_sql}.")
        return consultas_sql
    else:
        current_app.logger.error(f"Nenhuma query SQL encontrada na resposta do modelo: {resposta}.")
        return []

def translate_texts_queries(schema, pergunta):
    """
    Converte uma pergunta em linguagem natural para uma query SQL utilizando a API da OpenAI.

    Args:
        schema (str): O schema do banco de dados em texto.
        pergunta (str): A pergunta em linguagem natural.

    Returns:
        str: A query SQL gerada ou uma mensagem de erro.
    """
    # Prompt para a API da OpenAI
    prompt = upload_file_yaml("./prompts/query_builder.yaml", "query_builder", schema)

    try:
        # Inicializa a chave da API da OpenAI a partir das configurações da aplicação.
        client = OpenAI( api_key = current_app.config['OPENAI_API_KEY'])
        # Utilizando a interface atualizada da API ChatCompletion
        response = client.chat.completions.create(
            model="gpt-4o",  # ou outro modelo disponível
            messages=[
                {"role": "assistant", "content": prompt},
                {"role": "user", "content": f"""Args: pergunta (str): A pergunta em linguagem natural. pergunta: {pergunta}"""},
            ],
            temperature=1,  # Para respostas mais determinísticas
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extrair apenas o conteúdo da mensagem
        content = response.choices[0].message.content

        # Extrai o bloco de código SQL de um texto com explicações.
        queries = extract_all_queries_from_the_text(content, pergunta)
        if queries: 
            return queries
        else: 
            return "Nenhuma query válida foi extraída da resposta."
            
    except Exception as e:
        current_app.logger.error(str(e))
        return str(e)