import os
from openai import OpenAI
from flask import current_app
import re

def init_openai():
    """
    Inicializa a chave da API da OpenAI a partir das configurações da aplicação.
    """
    print("Inicializando OpenAI...")

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
    prompt = f"""
    Você é um assistente especializado em converter perguntas em linguagem natural para queries SQL em MySQL, usando o schema de banco de dados fornecido. Siga o processo abaixo para cada interação:

    ### Processo de Conversão
        1. **Entendimento Inicial**: 
            - Reformule a pergunta em suas palavras.
            - Identifique o contexto e o propósito da pergunta.
            - Mapeie o que você sabe e o que precisa descobrir.
        
        2. **Análise e Solução**:
            - Decomponha a pergunta em partes principais.
            - Identifique requisitos e restrições.
            - Considere diferentes abordagens e selecione a mais adequada.
        
        3. **Geração da Query**:
            - Com base no schema, desenvolva uma query SQL válida.
            - Enquadre a query no bloco ```sql * ```.

    ### Detalhes Importantes
        - Sua solução deve ser funcional e precisa, considerando o schema.
        - Mantenha um "monólogo interno" para estruturar seu pensamento, expressando cada etapa antes de chegar à resposta final.
        - O pensamento deve ser fluido e explorar a complexidade da questão.
        - É muito importante que você entenda o schema das tabelas antes de gerar a consulta.
        - Entenda qual agrupamento de dados e ideal para você responder a pergunta.
        - É muito importante que na sua resposta tenha uma consulta sql válida! Baseada no schema das tabelas.
        - É muito importante que a query esteja entre ```sql * ```.
        - Quanto houver os termos: 'cortesia', 'cortesias' a questão se refere ao 'caixa_tipos': 'Concessionária' e 'os_tipos' : 'Cortesia Concessionária', 'Cortesia Funcionário'.
        - O termos 'usados', 'carros usados' faz referência ao departamento 'veiculos usados'.
        - O termos 'novos', 'carros novos' faz referência ao departamento 'veiculos novos'.
        - O termo 'retorno' faz referência a serviços que tevem algum problema e o cliente voltou reclamando! Exemplo o filme instalado soltou!
        - O termo 'prestação de serviços' referece a 'os_tipos': 'Prestação de Serviços'.
        - O termo 'Venda Normal' referece a 'os_tipos': 'Venda Normal'.
        - O termo 'Financiamento' referece a 'os_tipos': 'Financiamento'.
        - O termo 'Nota Fiscal Manual' referece a 'os_tipos': 'Nota Fiscal Manual'.
        - O termo 'plotter' referece a 'estoques': 'PLOTTER', que representa os filmes produzidos dentro da empresa, quando falo produzidos, quero dizer que temos bobinas de filmes que cortamos para instalar no carro do cliente que vendemos o serviço!
        - O termo 'cluster' quer dizer grupo de concessionarias próximas! Existe a tabela 'clusters' que tem a relação 1:N com a tabela 'concessionarias'.
        - O pagamento de uma 'os' significa que uma 'os' tem um ou mais registros na tabela 'caixas', esta tem uma relação N:1 com a tabela 'os'.
        - Um serviço é executado usando um ou mais produtos! A tabela 'servico_produtos' é a tabela pivot entre as tabelas 'servicos' e 'produtos'.

    ### Estrutura da Resposta
        1. **Certifique-se de que a query**:
            - Responde completamente à pergunta.
            - Seja clara, precisa e válida.
            - Certifique as as colunas existam nas tabelas, considerando o schema das tabelas antes de gerar a query.
            - Esteja corretamente formatada entre ```sql * ```.
    
    ### Schema das Tabelas: 
        {schema}

    **Exemplo de Resposta:**
        ```sql
        SELECT f.nome AS vendedor_nome, s.nome AS servico_nome, COUNT(osv.servico_id) AS quantidade_vendida, 
        SUM(osv.valor_venda - osv.valor_original) AS lucro
        FROM os
        JOIN os_servicos osv ON os.id = osv.os_id
        JOIN servicos s ON osv.servico_id = s.id
        JOIN funcionarios f ON os.vendedor_id = f.id
        JOIN departamentos d ON os.departamento_id = d.id
        WHERE d.nome = 'oficina' AND os.paga = 1 
        AND os.data_pagamento BETWEEN '2024-12-01' AND '2024-12-31'
        GROUP BY vendedor_nome, servico_nome
        ORDER BY quantidade_vendida DESC;
        ```
    """

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
        query = extrair_query_sql(content)
        if query: 
            return query
        else: 
            return "Nenhuma query válida foi extraída da resposta."
            
    except Exception as e:
        current_app.logger.error(str(e))
        return str(e)