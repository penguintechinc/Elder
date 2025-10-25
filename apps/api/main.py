"""Main Flask application for Elder."""

import os
import structlog
from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from prometheus_flask_exporter import PrometheusMetrics

from apps.api.config import get_config
from shared.database import init_db, db


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure Flask application.

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    config = get_config(config_name)
    app.config.from_object(config)
    config.init_app(app)

    # Initialize extensions
    _init_extensions(app)

    # Initialize database
    init_db(app)

    # Initialize default admin user
    _init_admin_user(app)

    # Initialize license client
    _init_license_client(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Health check endpoint
    @app.route("/healthz")
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "service": "elder"}), 200

    logger.info(
        "elder_app_created",
        config=config_name,
        debug=app.config["DEBUG"],
        version=app.config["APP_VERSION"],
    )

    return app


def _init_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions.

    Args:
        app: Flask application
    """
    # CORS
    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        methods=app.config["CORS_METHODS"],
        allow_headers=app.config["CORS_ALLOW_HEADERS"],
    )

    # CSRF Protection - Exempt API routes (they use JWT, not cookies)
    csrf = CSRFProtect(app)

    # Exempt API routes from CSRF since they use JWT Bearer tokens
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False

    # Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID."""
        from apps.api.models import Identity

        return Identity.query.get(int(user_id))

    # Prometheus Metrics
    if app.config.get("METRICS_ENABLED"):
        metrics = PrometheusMetrics(app)
        metrics.info("elder_app_info", "Elder Application", version=app.config["APP_VERSION"])

    logger.info("extensions_initialized")


def _init_admin_user(app: Flask) -> None:
    """
    Initialize default admin user if configured.

    Args:
        app: Flask application
    """
    admin_username = app.config.get("ADMIN_USERNAME") or os.getenv("ADMIN_USERNAME")
    admin_password = app.config.get("ADMIN_PASSWORD") or os.getenv("ADMIN_PASSWORD")
    admin_email = app.config.get("ADMIN_EMAIL") or os.getenv("ADMIN_EMAIL", "admin@localhost")

    # Skip if no admin credentials provided
    if not admin_username or not admin_password:
        logger.info("admin_user_skip", reason="no_credentials_provided")
        return

    try:
        from apps.api.models import Identity
        from apps.api.models.identity import IdentityType, AuthProvider
        from werkzeug.security import generate_password_hash

        with app.app_context():
            # Check if admin user already exists
            existing_admin = db.session.query(Identity).filter_by(username=admin_username).first()
            if existing_admin:
                logger.info("admin_user_exists", username=admin_username)
                return

            # Create admin user
            admin_user = Identity(
                username=admin_username,
                email=admin_email,
                full_name="Administrator",
                identity_type=IdentityType.HUMAN,
                auth_provider=AuthProvider.LOCAL,
                password_hash=generate_password_hash(admin_password),
                is_active=True,
                is_superuser=True,
            )

            db.session.add(admin_user)
            db.session.commit()

            logger.info("admin_user_created", username=admin_username, email=admin_email)

    except Exception as e:
        logger.error("admin_user_creation_failed", error=str(e))
        with app.app_context():
            db.session.rollback()


def _init_license_client(app: Flask) -> None:
    """
    Initialize PenguinTech License Server client.

    Args:
        app: Flask application
    """
    from shared.licensing import get_license_client

    try:
        client = get_license_client()
        validation = client.validate()
        logger.info(
            "license_client_initialized",
            tier=validation.tier,
            enterprise_features_enabled=(validation.tier == "enterprise"),
        )
    except Exception as e:
        logger.warning(
            "license_client_init_failed",
            error=str(e),
            fallback="community",
        )


def _register_blueprints(app: Flask) -> None:
    """
    Register Flask blueprints (async and sync).

    Args:
        app: Flask application
    """
    # Import blueprints (async versions where available)
    from apps.api.api.v1 import organizations_pydal, entities, dependencies, graph, auth, identities, lookup, resource_roles, issues, metadata
    from apps.api.web import routes as web

    # Register API v1 blueprints
    api_prefix = app.config["API_PREFIX"]

    # Use async organizations_pydal blueprint (PyDAL + async/await)
    app.register_blueprint(organizations_pydal.bp, url_prefix=f"{api_prefix}/organizations")
    app.register_blueprint(entities.bp, url_prefix=f"{api_prefix}/entities")
    app.register_blueprint(dependencies.bp, url_prefix=f"{api_prefix}/dependencies")
    app.register_blueprint(graph.bp, url_prefix=f"{api_prefix}/graph")
    app.register_blueprint(auth.bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(identities.bp, url_prefix=f"{api_prefix}/identities")

    # Enterprise feature blueprints
    app.register_blueprint(resource_roles.bp, url_prefix=f"{api_prefix}/resource-roles")
    app.register_blueprint(issues.bp, url_prefix=f"{api_prefix}/issues")
    app.register_blueprint(metadata.bp, url_prefix=f"{api_prefix}/metadata")

    # Public lookup endpoint (no /api/v1 prefix for cleaner URLs)
    app.register_blueprint(lookup.bp, url_prefix="/lookup")

    # Web UI blueprint (root routes)
    app.register_blueprint(web.bp, url_prefix="")

    logger.info("blueprints_registered", api_prefix=api_prefix, blueprints=["organizations (async PyDAL)", "entities", "dependencies", "graph", "auth", "identities", "resource_roles", "issues", "metadata", "lookup", "web"])


def _register_error_handlers(app: Flask) -> None:
    """
    Register error handlers.

    Args:
        app: Flask application
    """

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request."""
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized."""
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden."""
        return jsonify({"error": "Forbidden", "message": "Insufficient permissions"}), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found."""
        return jsonify({"error": "Not Found", "message": "Resource not found"}), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Rate Limit Exceeded."""
        return jsonify({"error": "Rate Limit Exceeded", "message": "Too many requests"}), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        logger.error("internal_server_error", error=str(error))
        return jsonify({"error": "Internal Server Error", "message": "An error occurred"}), 500

    logger.info("error_handlers_registered")


if __name__ == "__main__":
    # Create and run application
    app = create_app()
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=app.config["DEBUG"],
    )
