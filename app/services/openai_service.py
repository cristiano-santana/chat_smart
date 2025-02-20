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

def extrair_query_sql(texto):
    """
    Extrai o bloco de código SQL de um texto com explicações.

    Args:
        texto (str): Texto que contém a query SQL dentro de blocos de código.

    Returns:
        str: A primeira query SQL extraída do bloco de código.
             Retorna `None` se nenhuma query for encontrada.
    """
    pattern = r"```sql\s*\n?(.*?)```"
    matches = re.findall(pattern, texto, flags=re.DOTALL | re.IGNORECASE)
    
    if matches:
        consulta_sql = matches[0].strip()
        if consulta_sql.upper().startswith("SELECT"):
            current_app.logger.info(f"query: {consulta_sql} extraída do texto.")
            return consulta_sql
        else:
            current_app.logger.error("A query extraída não é uma SELECT.")
            return None
    else:
        current_app.logger.error("Nenhuma query SQL encontrada no texto.")
        return None

def extrair_todas_queries_sql(texto):
    """
    Extrai todos os blocos de código SQL de um texto com explicações.

    Args:
        texto (str): Texto que contém as queries SQL dentro de blocos de código.

    Returns:
        list: Lista de queries SQL extraídas dos blocos de código.
              Retorna lista vazia se nenhuma query for encontrada.
    """
    pattern = r"```sql\s*\n?(.*?)```"
    matches = re.findall(pattern, texto, flags=re.DOTALL | re.IGNORECASE)
    
    if matches:
        consultas_sql = [match.strip() for match in matches]
        current_app.logger.info(f"{len(consultas_sql)} queries extraídas do texto.")
        return consultas_sql
    else:
        current_app.logger.error("Nenhuma query SQL encontrada no texto.")
        return []

def traduzir_para_query(schema, pergunta):
    """
    Converte uma pergunta em linguagem natural para uma query SQL utilizando a API da OpenAI.

    Args:
        schema (str): O schema do banco de dados em texto.
        pergunta (str): A pergunta em linguagem natural.

    Returns:
        str: A query SQL gerada ou uma mensagem de erro.
    """
    # Prompt para a API da OpenAI
    prompt = upload_file_yaml("./prompts/prompt_revisado.yaml", "prompt_revisado", schema)

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
        queries = extrair_todas_queries_sql(content)
        if queries: 
            return queries
        else: 
            return "Nenhuma query válida foi extraída da resposta."
            
    except Exception as e:
        current_app.logger.error(str(e))
        return str(e)