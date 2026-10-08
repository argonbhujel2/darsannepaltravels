import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url: str) -> str:
    """Make DATABASE_URL work on Vercel / Neon / Heroku with psycopg2."""
    if not url:
        return 'sqlite:///darshan_nepal.db'

    # Heroku/Neon style
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]

    # Force psycopg2 driver (we ship psycopg2-binary, not psycopg v3)
    if url.startswith('postgresql://'):
        url = 'postgresql+psycopg2://' + url[len('postgresql://'):]
    elif url.startswith('postgresql+psycopg://'):
        url = 'postgresql+psycopg2://' + url[len('postgresql+psycopg://'):]

    return url


# Detect serverless (Vercel)
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'darshan-nepal-dev-secret-change-in-production'
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get('DATABASE_URL') or 'sqlite:///darshan_nepal.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production' or IS_VERCEL
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Uploads — Vercel filesystem is read-only except /tmp
    if IS_VERCEL:
        UPLOAD_FOLDER = '/tmp/darshan_uploads'
    else:
        UPLOAD_FOLDER = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads'
        )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif', 'ico', 'svg'}

    # Cloudinary (required for durable media on Vercel)
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"

    # Business defaults
    BUSINESS_NAME = "Darshan Nepal Travel & Tours"
    BUSINESS_ADDRESS = "Urlabari, Koshi Province 56604, Nepal"
    BUSINESS_PHONE = "9801708396"
    BUSINESS_PHONES = ["9801708396", "9801708397", "9841110276"]
    GOOGLE_RATING = 4.8
    REVIEW_COUNT = 27


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
