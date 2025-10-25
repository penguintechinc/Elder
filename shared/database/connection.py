"""Database connection and session management using PyDAL."""

from contextlib import contextmanager
from typing import Generator

from flask import Flask
from pydal import DAL, Field

# Global PyDAL instance
db = None


def init_db(app: Flask) -> None:
    """
    Initialize database with Flask application.

    Args:
        app: Flask application instance

    Environment Variables:
        DATABASE_URL: Full database URI (takes precedence if set)
        DB_TYPE: Database type (postgresql, mysql, sqlite, etc.) - default: postgresql
        DB_HOST: Database host - default: localhost
        DB_PORT: Database port - default: 5432 for PostgreSQL
        DB_NAME: Database name - default: elder
        DB_USER: Database username - default: elder
        DB_PASSWORD: Database password - default: elder
        DB_POOL_SIZE: Connection pool size - default: 10

    Supported Database URIs (PyDAL):
        - PostgreSQL: postgres://user:pass@host:port/db (NOTE: 'postgres' not 'postgresql')
        - MySQL: mysql://user:pass@host/db?set_encoding=utf8mb4
        - SQLite: sqlite://storage.sqlite
        - MSSQL: mssql3://user:pass@host/db (2005+), mssql4://user:pass@host/db (2012+)
        - Oracle: oracle://user/pass@db
        - MongoDB: mongodb://user:pass@host/db
        - Google Cloud SQL: google:sql://project:instance/database
        - And more: FireBird, DB2, Ingres, Sybase, Informix, Teradata, Cubrid, SAPDB

        Full list: https://py4web.com/_documentation/static/en/chapter-07.html
    """
    global db
    import os

    # Build database URL from environment variables or use full DATABASE_URL
    database_url = app.config.get("DATABASE_URL") or os.getenv("DATABASE_URL")

    if not database_url:
        # Build from individual components
        db_type = app.config.get("DB_TYPE") or os.getenv("DB_TYPE", "postgres")
        db_host = app.config.get("DB_HOST") or os.getenv("DB_HOST", "localhost")
        db_port = app.config.get("DB_PORT") or os.getenv("DB_PORT", "5432")
        db_name = app.config.get("DB_NAME") or os.getenv("DB_NAME", "elder")
        db_user = app.config.get("DB_USER") or os.getenv("DB_USER", "elder")
        db_password = app.config.get("DB_PASSWORD") or os.getenv("DB_PASSWORD", "elder")

        # Normalize DB_TYPE to PyDAL format
        db_type = db_type.lower()

        # Handle all PyDAL-supported database types
        # Reference: https://py4web.com/_documentation/static/en/chapter-07.html
        if db_type == "sqlite":
            # SQLite - file-based database
            database_url = f"sqlite://{db_name}.sqlite"

        elif db_type in ["mysql", "mariadb"]:
            # MySQL/MariaDB - with UTF8MB4 encoding
            database_url = f"mysql://{db_user}:{db_password}@{db_host}/{db_name}?set_encoding=utf8mb4"

        elif db_type in ["postgresql", "postgres"]:
            # PostgreSQL - PyDAL uses 'postgres://' not 'postgresql://'
            database_url = f"postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        elif db_type in ["mssql", "mssql3", "mssql4"]:
            # Microsoft SQL Server - mssql (legacy), mssql3 (2005+), mssql4 (2012+)
            # Default to mssql4 for modern SQL Server
            adapter = "mssql4" if db_type == "mssql" else db_type
            database_url = f"{adapter}://{db_user}:{db_password}@{db_host}/{db_name}"

        elif db_type == "oracle":
            # Oracle - special format with user/password
            database_url = f"oracle://{db_user}/{db_password}@{db_name}"

        elif db_type == "mongodb":
            # MongoDB - NoSQL database
            database_url = f"mongodb://{db_user}:{db_password}@{db_host}/{db_name}"

        elif db_type == "firebird":
            # FireBird database
            database_url = f"firebird://{db_user}:{db_password}@{db_host}/{db_name}"

        elif db_type == "db2":
            # IBM DB2
            database_url = f"db2://{db_user}:{db_password}@{db_name}"

        elif db_type == "ingres":
            # Ingres database
            database_url = f"ingres://{db_user}:{db_password}@{db_host}/{db_name}"

        elif db_type == "sybase":
            # Sybase database
            database_url = f"sybase://{db_user}:{db_password}@{db_host}/{db_name}"

        elif db_type == "informix":
            # Informix database
            database_url = f"informix://{db_user}:{db_password}@{db_name}"

        elif db_type == "teradata":
            # Teradata - uses DSN format
            # Format: teradata://DSN=dsn;UID=user;PWD=pass;DATABASE=test
            database_url = f"teradata://DSN={db_host};UID={db_user};PWD={db_password};DATABASE={db_name}"

        elif db_type == "cubrid":
            # CUBRID database
            database_url = f"cubrid://{db_user}:{db_password}@{db_host}/{db_name}"

        elif db_type == "sapdb":
            # SAP DB (MaxDB)
            database_url = f"sapdb://{db_user}:{db_password}@{db_host}/{db_name}"

        elif db_type == "imap":
            # IMAP (email storage) - special use case
            database_url = f"imap://{db_user}:{db_password}@{db_host}:{db_port}"

        elif db_type in ["google:sql", "googlesql"]:
            # Google Cloud SQL
            # Format: google:sql://project:instance/database
            # Use DB_HOST as project:instance format
            database_url = f"google:sql://{db_host}/{db_name}"

        elif db_type in ["google:datastore", "googledatastore"]:
            # Google Cloud Datastore (NoSQL)
            database_url = "google:datastore"

        elif db_type in ["google:datastore+ndb", "googledatastore+ndb"]:
            # Google Cloud Datastore with NDB
            database_url = "google:datastore+ndb"

        else:
            # Generic format for any other PyDAL-supported database
            # This allows for future database support without code changes
            database_url = f"{db_type}://{db_user}:{db_password}@{db_host}/{db_name}"

    # Get connection pool size
    pool_size = app.config.get("DB_POOL_SIZE") or int(os.getenv("DB_POOL_SIZE", "10"))

    # Initialize PyDAL with connection pooling
    # NOTE: pool_size=0 disables pooling, giving each thread its own connection
    # This is important for thread safety with async/threadpool execution
    db = DAL(
        database_url,
        folder=app.instance_path if hasattr(app, 'instance_path') else 'databases',
        migrate=True,
        fake_migrate_all=False,
        lazy_tables=False,
        pool_size=0,  # Disable pooling for thread safety
    )

    # Store db instance in app context
    app.db = db

    # Define all tables
    _define_tables(db)

    # Initialize default data
    with app.app_context():
        _init_default_data(db)


def _define_tables(db: DAL) -> None:
    """Define all database tables using PyDAL."""

    # Import table definitions
    from apps.api.models.pydal_models import define_all_tables
    define_all_tables(db)


def _init_default_data(db: DAL) -> None:
    """Initialize default data (roles, permissions, admin user)."""
    import os
    from werkzeug.security import generate_password_hash

    # Check if roles already exist
    if db(db.roles).count() > 0:
        return

    # Create default roles
    roles_data = [
        {"name": "super_admin", "description": "Full system access"},
        {"name": "org_admin", "description": "Full access within organization"},
        {"name": "editor", "description": "Can create and edit entities"},
        {"name": "viewer", "description": "Read-only access"},
    ]

    roles = {}
    for role_data in roles_data:
        role_id = db.roles.insert(**role_data)
        roles[role_data["name"]] = role_id

    # Create default permissions
    permissions_data = [
        # Entity permissions
        {"name": "create_entity", "resource_type": "entity", "action_name": "create"},
        {"name": "edit_entity", "resource_type": "entity", "action_name": "edit"},
        {"name": "delete_entity", "resource_type": "entity", "action_name": "delete"},
        {"name": "view_entity", "resource_type": "entity", "action_name": "view"},
        # Organization permissions
        {"name": "create_organization", "resource_type": "organization", "action_name": "create"},
        {"name": "edit_organization", "resource_type": "organization", "action_name": "edit"},
        {"name": "delete_organization", "resource_type": "organization", "action_name": "delete"},
        {"name": "view_organization", "resource_type": "organization", "action_name": "view"},
        # Dependency permissions
        {"name": "create_dependency", "resource_type": "dependency", "action_name": "create"},
        {"name": "delete_dependency", "resource_type": "dependency", "action_name": "delete"},
        {"name": "view_dependency", "resource_type": "dependency", "action_name": "view"},
        # User management
        {"name": "manage_users", "resource_type": "identity", "action_name": "manage"},
        {"name": "view_users", "resource_type": "identity", "action_name": "view"},
        # Role management
        {"name": "manage_roles", "resource_type": "role", "action_name": "manage"},
        {"name": "view_roles", "resource_type": "role", "action_name": "view"},
        # Audit logs
        {"name": "view_audit_logs", "resource_type": "audit", "action_name": "view"},
    ]

    permissions = {}
    for perm_data in permissions_data:
        perm_id = db.permissions.insert(**perm_data)
        permissions[perm_data["name"]] = perm_id

    # Assign permissions to roles
    role_permissions_map = {
        "super_admin": list(permissions.keys()),  # All permissions
        "org_admin": [
            "create_entity", "edit_entity", "delete_entity", "view_entity",
            "view_organization", "create_dependency", "delete_dependency",
            "view_dependency", "view_users", "view_audit_logs",
        ],
        "editor": [
            "create_entity", "edit_entity", "view_entity",
            "view_organization", "create_dependency", "view_dependency",
        ],
        "viewer": ["view_entity", "view_organization", "view_dependency"],
    }

    for role_name, perm_names in role_permissions_map.items():
        role_id = roles[role_name]
        for perm_name in perm_names:
            perm_id = permissions[perm_name]
            db.role_permissions.insert(role_id=role_id, permission_id=perm_id)

    # Create default admin user if specified in environment
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if admin_password:
        admin_id = db.identities.insert(
            username=admin_username,
            email=os.getenv("ADMIN_EMAIL", f"{admin_username}@localhost"),
            full_name="System Administrator",
            identity_type="human",
            auth_provider="local",
            password_hash=generate_password_hash(admin_password),
            is_active=True,
            is_superuser=True,
        )

        # Assign super_admin role
        db.user_roles.insert(
            identity_id=admin_id,
            role_id=roles["super_admin"],
            scope="global",
        )

    db.commit()


@contextmanager
def get_db_session() -> Generator[DAL, None, None]:
    """
    Get a database session context manager.

    Yields:
        Database session (PyDAL db instance)

    Example:
        with get_db_session() as session:
            user = session(session.identities).select().first()
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
