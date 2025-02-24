import mysql.connector
from mysql.connector import Error
from flask import current_app
import re

def executar_query(query, params=None):
    # Apenas permitir queries SELECT para segurança
    # if not re.match(r'^SELECT\b', query, re.IGNORECASE):
    #     return "Somente queries SELECT são permitidas para segurança."

    # Verificar se a query contém comandos indesejados
    # Como DELETE, UPDATE, DROP, etc.
    unsafe_patterns = [
        r'\bDELETE\b',
        r'\bUPDATE\b',
        r'\bDROP\b',
        r'\bINSERT\b',
        r'\bALTER\b',
        r'\bTRUNCATE\b',
        r'\bGRANT\b',
        r'\bREVOKE\b',
    ]

    for pattern in unsafe_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return f"Comando SQL não permitido detectado na query: '{pattern.strip(r'\b')}'"
    
    # Inicializar a variável antes do try
    connection = None

    try:
        connection = mysql.connector.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            database=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD']
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            return resultados
    except Error as e:
        current_app.logger.error(f"Erro ao executar a query: {e}")
        return f"Erro ao executar a query: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()