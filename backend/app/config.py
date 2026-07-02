"""
Flask Application Configuration
Loads settings from environment variables with sensible defaults.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv(
        "SECRET_KEY", "dev-secret-key-change-in-production-32b"
    )
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, '..', 'instance', 'expense_tracker.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY", "dev-jwt-secret-key-change-in-production-32b"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_HOURS", "1"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_DAYS", "30"))
    )

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    PROPAGATE_EXCEPTIONS = True

    JWT_BLOCKLIST_ENABLED = os.getenv("JWT_BLOCKLIST_ENABLED", "true").lower() == "true"

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    DEBUG = True
    SECRET_KEY = "test-secret-key-for-pytest-suite-32bytes"
    JWT_SECRET_KEY = "test-jwt-secret-key-for-pytest-suite-32b"


class ProductionConfig(Config):
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, '..', 'instance', 'expense_tracker.db')}",
    )

    @classmethod
    def _init_uri(cls):
        uri = cls.SQLALCHEMY_DATABASE_URI
        if uri and uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        cls.SQLALCHEMY_DATABASE_URI = uri

ProductionConfig._init_uri()


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
