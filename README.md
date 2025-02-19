# Chat SQL Bot

Um chatbot que converte perguntas em linguagem natural para queries SQL no MySQL, utilizando a API da OpenAI.

## Características

- Tradução de linguagem natural para queries SQL.
- Integração com banco de dados MySQL.
- Interface web simples com Flask.
- Limitação de requisições para segurança.
- Apenas queries SELECT são permitidas.

## Leia
- https://medium.com/everyday-ai/every-ai-engineer-should-know-these-15-python-libraries-in-2025-b83726ecc86d
- https://medium.com/@jagadeesan.ganesh/mastering-llm-ai-agents-building-and-using-ai-agents-in-python-with-real-world-use-cases-c578eb640e35

## Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/seu_usuario/meu_chatbot.git
cd meu_chatbot
```

### 2. Configurar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
OPENAI_API_KEY=your_openai_api_key
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=seu_db
SECRET_KEY=uma_chave_secreta
```

### 5. Configurar Usuário do MySQL

Crie um usuário no MySQL com privilégios de leitura:

```sql
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT SELECT ON seu_db.clientes TO 'bot_user'@'localhost';
GRANT SELECT ON seu_db.pedidos TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;
```

### 6. Executar a Aplicação

```bash
python run.py
```

Acesse via navegador em `http://127.0.0.1:5000/`.

## Testes

Para executar os testes, rode:

```bash
python -m unittest discover tests
```

## Segurança

- Apenas queries SELECT são permitidas.
- Utilize um usuário do MySQL com privilégios limitados.
- Limitação de requisições para prevenir abusos.
- Logs de atividades implementados para monitoramento.

## Contribuição

Sinta-se à vontade para abrir issues e pull requests!

## Licença

MIT License
```

### 9.2. Comentários e Docstrings no Código

Adicione comentários e docstrings para explicar o funcionamento das funções e módulos.

**Exemplo:**

**`app/services/openai_service.py`**

```python
import openai
from flask import current_app

def init_openai():
    """
    Inicializa a chave da API da OpenAI a partir das configurações da aplicação.
    """
    openai.api_key = current_app.config['OPENAI_API_KEY']

def traduzir_para_query(schema, pergunta):
    """
    Converte uma pergunta em linguagem natural para uma query SQL utilizando a API da OpenAI.

    Args:
        schema (str): O schema do banco de dados em texto.
        pergunta (str): A pergunta em linguagem natural.

    Returns:
        str: A query SQL gerada ou uma mensagem de erro.
    """
    prompt = f"""
    Você é um assistente que converte perguntas em linguagem natural para queries SQL do MySQL, usando o seguinte schema do banco de dados:

    {schema}

    Pergunta: {pergunta}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você converte perguntas em linguagem natural para queries SQL do MySQL."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        query = response['choices'][0]['message']['content'].strip()
        return query
    except Exception as e:
        current_app.logger.error(f"Erro na tradução para query: {e}")
        return f"Erro na tradução da pergunta: {str(e)}"
```

## Considerações Finais

Seguindo essas etapas, você terá um chatbot funcional que traduz perguntas em linguagem natural para queries SQL no MySQL, utilizando a API da OpenAI. A estrutura apresentada facilita a manutenção e a escalabilidade do projeto, permitindo adicionar novas funcionalidades no futuro.

### Próximos Passos

1. **Validação da Query Gerada:** Antes de executar, validar se a query está correta e segura.
2. **Interface de Usuário Avançada:** Melhorar a interface web com feedback visual e validações no frontend.
3. **Autenticação e Autorização:** Implementar mecanismos de login para controlar o acesso ao chatbot.
4. **Cache de Respostas:** Implementar um sistema de cache para perguntas frequentes, melhorando a performance.
5. **Monitoramento de Erros:** Integrar ferramentas como Sentry para monitoramento de erros em produção.

Se tiver dúvidas ou precisar de ajuda em alguma das etapas, sinta-se à vontade para perguntar!