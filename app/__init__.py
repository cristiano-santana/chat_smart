from flask import Flask
from .config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import TimedRotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configurar Logging
    if not os.path.exists('logs'):
        os.mkdir('logs')

    log_file = 'logs/chat_smart.log'

    # Configuração para gerar um log por dia
    file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=10, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('ChatSQL Bot startup')

    # Inicializar Limiter para Rate Limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)
    
    with app.app_context():
        # Inicializar Serviços
        from .services.openai_service import init_openai
        init_openai()

        # Registrar Rotas
        from .routes import bp
        app.register_blueprint(bp)

    return app