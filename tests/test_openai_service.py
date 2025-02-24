import unittest
from unittest.mock import patch
from app import create_app
from app.services.openai_service import translate_texts_queries

class TestOpenAIService(unittest.TestCase):
    def setUp(self):
        # Criar uma instância da aplicação para usar no contexto
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Remover o contexto após o teste
        self.app_context.pop()

    @patch('openai.ChatCompletion.create')
    def test_translate_texts_queries(self, mock_create):
        mock_create.return_value = {
            'choices': [
                {'message': {'content': 'SELECT * FROM clientes;'}}
            ]
        }
        schema = """
        Tabela: clientes
        - id (INT, Primary Key)
        - nome (VARCHAR)
        - email (VARCHAR)
        - telefone (VARCHAR)
        """
        pergunta = "Liste todos os clientes."
        query = translate_texts_queries(schema, pergunta)
        self.assertEqual(query, 'SELECT * FROM clientes;')

    @patch('openai.ChatCompletion.create')
    def test_translate_texts_queries_invalid_command(self, mock_create):
        # Simular uma query não-SELECT
        mock_create.return_value = {
            'choices': [
                {'message': {'content': 'DELETE FROM clientes WHERE id=1;'}}
            ]
        }
        schema = """
        Tabela: clientes
        - id (INT, Primary Key)
        - nome (VARCHAR)
        - email (VARCHAR)
        - telefone (VARCHAR)
        """
        pergunta = "Exclua o cliente com ID 1."
        query = translate_texts_queries(schema, pergunta)
        self.assertIn("Erro na tradução da pergunta", query)

if __name__ == '__main__':
    unittest.main()