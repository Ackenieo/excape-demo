import os


class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = APP_ENV != "production"
    TESTING = os.getenv("TESTING", "0") == "1"
    SECRET_KEY = os.getenv("SECRET_KEY", "npc-escape-dev-key")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/npc_escape")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    RATE_LIMIT = os.getenv("RATE_LIMIT", "60/minute")
