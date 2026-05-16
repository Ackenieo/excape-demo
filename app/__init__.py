from flask import Flask
from config import Config
from app.extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Alembic can detect them
    from app import models

    # Register blueprints
    from app.blueprints.level import level_bp
    from app.blueprints.run import run_bp
    from app.blueprints.chat import chat_bp
    from app.blueprints.ranking import ranking_bp
    from app.blueprints.challenge import challenge_bp
    from app.blueprints.profile import profile_bp
    from app.blueprints.custom_npc import custom_npc_bp
    from app.blueprints.upload import upload_bp

    app.register_blueprint(level_bp)
    app.register_blueprint(run_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(challenge_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(custom_npc_bp)
    app.register_blueprint(upload_bp)

    return app
