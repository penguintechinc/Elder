"""Configuration management for Elder application."""

import os
from typing import Any, Dict
from decouple import config
from datetime import timedelta


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-in-production")
    DEBUG = config("DEBUG", default=False, cast=bool)
    TESTING = config("TESTING", default=False, cast=bool)

    # Application
    APP_NAME = "Elder"
    APP_VERSION = config("APP_VERSION", default="0.1.0")

    # Database (PyDAL - use individual components or DATABASE_URL)
    # Note: PyDAL uses 'postgres://' not 'postgresql://'
    DATABASE_URL = config(
        "DATABASE_URL",
        default=None,  # Let connection.py build from DB_TYPE, DB_HOST, etc.
    )
    SQLALCHEMY_MAX_OVERFLOW = config("SQLALCHEMY_MAX_OVERFLOW", default=20, cast=int)

    # Redis
    REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
    REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)
    REDIS_SSL = config("REDIS_SSL", default=False, cast=bool)

    # Session
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "elder:session:"

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF token
    BCRYPT_LOG_ROUNDS = 12

    # JWT
    JWT_SECRET_KEY = config("JWT_SECRET_KEY", default=None)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)  # Extended to 4 hours for development
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = "HS256"

    # CORS
    CORS_ORIGINS = config("CORS_ORIGINS", default="*")
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]

    # Rate Limiting
    RATELIMIT_ENABLED = config("RATELIMIT_ENABLED", default=True, cast=bool)
    RATELIMIT_DEFAULT = config("RATELIMIT_DEFAULT", default="100/hour")
    RATELIMIT_STORAGE_URL = REDIS_URL

    # SAML Authentication
    SAML_ENABLED = config("SAML_ENABLED", default=False, cast=bool)
    SAML_METADATA_URL = config("SAML_METADATA_URL", default=None)
    SAML_ENTITY_ID = config("SAML_ENTITY_ID", default="elder")
    SAML_ACS_URL = config("SAML_ACS_URL", default="http://localhost:5000/api/v1/auth/saml/acs")

    # OAuth2 Authentication
    OAUTH2_ENABLED = config("OAUTH2_ENABLED", default=False, cast=bool)
    OAUTH2_CLIENT_ID = config("OAUTH2_CLIENT_ID", default=None)
    OAUTH2_CLIENT_SECRET = config("OAUTH2_CLIENT_SECRET", default=None)
    OAUTH2_AUTHORIZE_URL = config("OAUTH2_AUTHORIZE_URL", default=None)
    OAUTH2_TOKEN_URL = config("OAUTH2_TOKEN_URL", default=None)
    OAUTH2_USERINFO_URL = config("OAUTH2_USERINFO_URL", default=None)

    # LDAP
    LDAP_ENABLED = config("LDAP_ENABLED", default=False, cast=bool)
    LDAP_HOST = config("LDAP_HOST", default="localhost")
    LDAP_PORT = config("LDAP_PORT", default=389, cast=int)
    LDAP_USE_SSL = config("LDAP_USE_SSL", default=False, cast=bool)
    LDAP_BASE_DN = config("LDAP_BASE_DN", default="")
    LDAP_BIND_DN = config("LDAP_BIND_DN", default=None)
    LDAP_BIND_PASSWORD = config("LDAP_BIND_PASSWORD", default=None)

    # gRPC
    GRPC_ENABLED = config("GRPC_ENABLED", default=True, cast=bool)
    GRPC_PORT = config("GRPC_PORT", default=50051, cast=int)
    GRPC_MAX_WORKERS = config("GRPC_MAX_WORKERS", default=10, cast=int)

    # License Server
    LICENSE_KEY = config("LICENSE_KEY", default=None)
    LICENSE_SERVER_URL = config("LICENSE_SERVER_URL", default="https://license.penguintech.io")
    PRODUCT_NAME = "elder"

    # Logging
    LOG_LEVEL = config("LOG_LEVEL", default="INFO")
    LOG_FORMAT = config("LOG_FORMAT", default="json")  # json or text
    SYSLOG_ENABLED = config("SYSLOG_ENABLED", default=False, cast=bool)
    SYSLOG_HOST = config("SYSLOG_HOST", default="localhost")
    SYSLOG_PORT = config("SYSLOG_PORT", default=514, cast=int)

    # Prometheus Metrics
    METRICS_ENABLED = config("METRICS_ENABLED", default=True, cast=bool)

    # API
    API_PREFIX = "/api/v1"
    API_PAGINATION_DEFAULT = config("API_PAGINATION_DEFAULT", default=50, cast=int)
    API_PAGINATION_MAX = config("API_PAGINATION_MAX", default=1000, cast=int)

    # WebSocket
    WEBSOCKET_ENABLED = config("WEBSOCKET_ENABLED", default=True, cast=bool)

    @staticmethod
    def init_app(app: Any) -> None:
        """Initialize application with configuration."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Override with stricter settings
    WTF_CSRF_ENABLED = True
    BCRYPT_LOG_ROUNDS = 13

    @staticmethod
    def init_app(app: Any) -> None:
        """Initialize production application."""
        Config.init_app(app)

        # Production-specific initialization
        import logging
        from logging.handlers import SysLogHandler

        if app.config.get("SYSLOG_ENABLED"):
            syslog_handler = SysLogHandler(
                address=(app.config["SYSLOG_HOST"], app.config["SYSLOG_PORT"])
            )
            syslog_handler.setLevel(logging.WARNING)
            app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    WTF_CSRF_ENABLED = False

    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False

    # Disable license validation for tests
    LICENSE_KEY = "PENG-TEST-TEST-TEST-TEST-TEST"


# Configuration dictionary
config_by_name: Dict[str, type] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: str = None) -> type:
    """
    Get configuration by name.

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    return config_by_name.get(config_name, DevelopmentConfig)
