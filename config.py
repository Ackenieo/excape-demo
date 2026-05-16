import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+pg8000://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Server Configuration
    HOST = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_RUN_PORT', 8888))
    DEBUG = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    # PostgreSQL Configuration
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get(
            'DATABASE_URL',
            'postgresql://malog:malogbot123@127.0.0.1:5433/escape'
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Avatar Upload Configuration
    APP_ROOT = Path(__file__).resolve().parent
    AVATAR_UPLOAD_DIR = os.environ.get(
        "AVATAR_UPLOAD_DIR",
        str(APP_ROOT / "uploads" / "avatars"),
    )
    AVATAR_UPLOAD_PUBLIC_BASE_URL = os.environ.get(
        "AVATAR_UPLOAD_PUBLIC_BASE_URL",
        "https://cdn.example.com",
    ).rstrip("/")
    DEFAULT_PROFILE_AVATAR_URL = os.environ.get("DEFAULT_PROFILE_AVATAR_URL")
    AVATAR_UPLOAD_ALLOWED_HOSTS = [
        host.strip().lower()
        for host in os.environ.get(
            "AVATAR_UPLOAD_ALLOWED_HOSTS",
            "cdn.example.com",
        ).split(",")
        if host.strip()
    ]
    AVATAR_UPLOAD_ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
    AVATAR_UPLOAD_ALLOWED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }
    AVATAR_UPLOAD_MIN_BYTES = int(os.environ.get("AVATAR_UPLOAD_MIN_BYTES", 1024))
    AVATAR_UPLOAD_MAX_BYTES = int(os.environ.get("AVATAR_UPLOAD_MAX_BYTES", 5 * 1024 * 1024))
    AVATAR_UPLOAD_BIZ_TYPE = os.environ.get("AVATAR_UPLOAD_BIZ_TYPE", "profile_avatar")
