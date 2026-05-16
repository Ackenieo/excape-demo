from flask import Flask

from app.api import api_bp
from config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(api_bp, url_prefix="/api")

    return app
