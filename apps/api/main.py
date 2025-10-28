"""Main Flask application for Elder."""

import os
import logging
import structlog
from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from prometheus_flask_exporter import PrometheusMetrics
from asgiref.wsgi import WsgiToAsgi

from apps.api.config import get_config
from shared.database import init_db, db

# Configure standard library logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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

    # Initialize database (includes default admin user creation)
    init_db(app)

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

    # Wrap Flask WSGI app with ASGI adapter for uvicorn
    return WsgiToAsgi(app)


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
    from apps.api.api.v1 import (
        organizations_pydal,
        entities,
        entity_types,
        dependencies,
        graph,
        auth,
        profile,
        identities,
        api_keys,
        users,
        lookup,
        resource_roles,
        issues,
        metadata,
        projects,
        milestones,
        labels,
        organization_tree,
        sync,
        secrets,  # Phase 2: Secrets Management
        keys,  # Phase 3: Keys Management
        iam,  # Phase 4: IAM Integration
        discovery,  # Phase 5: Cloud Auto-Discovery
        webhooks,  # Phase 9: Webhook & Notification System
        search,  # Phase 10: Advanced Search
        backup,  # Phase 10: Backup & Data Management
    )
    from apps.api.web import routes as web

    # Register API v1 blueprints
    api_prefix = app.config["API_PREFIX"]

    # Use async organizations_pydal blueprint (PyDAL + async/await)
    app.register_blueprint(organizations_pydal.bp, url_prefix=f"{api_prefix}/organizations")
    app.register_blueprint(entities.bp, url_prefix=f"{api_prefix}/entities")
    app.register_blueprint(entity_types.bp, url_prefix=f"{api_prefix}/entity-types")
    app.register_blueprint(dependencies.bp, url_prefix=f"{api_prefix}/dependencies")
    app.register_blueprint(graph.bp, url_prefix=f"{api_prefix}/graph")
    app.register_blueprint(auth.bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(profile.bp, url_prefix=f"{api_prefix}/profile")
    app.register_blueprint(identities.bp, url_prefix=f"{api_prefix}/identities")
    app.register_blueprint(api_keys.bp, url_prefix=f"{api_prefix}/api-keys")
    app.register_blueprint(users.bp, url_prefix=f"{api_prefix}/users")

    # Enterprise feature blueprints
    app.register_blueprint(resource_roles.bp, url_prefix=f"{api_prefix}/resource-roles")
    app.register_blueprint(issues.bp, url_prefix=f"{api_prefix}/issues")
    app.register_blueprint(labels.bp, url_prefix=f"{api_prefix}/labels")
    app.register_blueprint(metadata.bp, url_prefix=f"{api_prefix}/metadata")
    app.register_blueprint(projects.bp, url_prefix=f"{api_prefix}/projects")
    app.register_blueprint(milestones.bp, url_prefix=f"{api_prefix}/milestones")
    app.register_blueprint(organization_tree.bp, url_prefix=f"{api_prefix}")
    app.register_blueprint(sync.bp, url_prefix=f"{api_prefix}/sync")

    # v1.2.0 Feature blueprints (stub implementations)
    app.register_blueprint(secrets.bp, url_prefix=f"{api_prefix}/secrets")  # Phase 2
    app.register_blueprint(keys.bp, url_prefix=f"{api_prefix}/keys")  # Phase 3
    app.register_blueprint(iam.bp, url_prefix=f"{api_prefix}/iam")  # Phase 4
    app.register_blueprint(discovery.bp, url_prefix=f"{api_prefix}/discovery")  # Phase 5
    app.register_blueprint(webhooks.bp, url_prefix=f"{api_prefix}/webhooks")  # Phase 9
    app.register_blueprint(search.bp, url_prefix=f"{api_prefix}/search")  # Phase 10
    app.register_blueprint(backup.bp, url_prefix=f"{api_prefix}/backup")  # Phase 10

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
    # Create and run application directly with Flask dev server
    # Note: create_app() returns ASGI app, so we need to unwrap it
    import uvicorn
    asgi_app = create_app()
    uvicorn.run(
        asgi_app,
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
    )
