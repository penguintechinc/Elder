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
    """
    global db

    # Get database URL from config
    database_url = app.config.get("DATABASE_URL", "postgresql://elder:elder@localhost:5432/elder")

    # Initialize PyDAL
    db = DAL(
        database_url,
        folder=app.instance_path if hasattr(app, 'instance_path') else 'databases',
        migrate=True,
        fake_migrate_all=False,
        lazy_tables=False,
        pool_size=app.config.get("SQLALCHEMY_POOL_SIZE", 10)
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
        {"name": "create_entity", "resource_type": "entity", "action": "create"},
        {"name": "edit_entity", "resource_type": "entity", "action": "edit"},
        {"name": "delete_entity", "resource_type": "entity", "action": "delete"},
        {"name": "view_entity", "resource_type": "entity", "action": "view"},
        # Organization permissions
        {"name": "create_organization", "resource_type": "organization", "action": "create"},
        {"name": "edit_organization", "resource_type": "organization", "action": "edit"},
        {"name": "delete_organization", "resource_type": "organization", "action": "delete"},
        {"name": "view_organization", "resource_type": "organization", "action": "view"},
        # Dependency permissions
        {"name": "create_dependency", "resource_type": "dependency", "action": "create"},
        {"name": "delete_dependency", "resource_type": "dependency", "action": "delete"},
        {"name": "view_dependency", "resource_type": "dependency", "action": "view"},
        # User management
        {"name": "manage_users", "resource_type": "identity", "action": "manage"},
        {"name": "view_users", "resource_type": "identity", "action": "view"},
        # Role management
        {"name": "manage_roles", "resource_type": "role", "action": "manage"},
        {"name": "view_roles", "resource_type": "role", "action": "view"},
        # Audit logs
        {"name": "view_audit_logs", "resource_type": "audit", "action": "view"},
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
