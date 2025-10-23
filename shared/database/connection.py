"""Database connection and session management."""

from contextlib import contextmanager
from typing import Generator, Any

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

# Global SQLAlchemy instance
db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """
    Initialize database with Flask application.

    Args:
        app: Flask application instance
    """
    db.init_app(app)

    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        from apps.api import models  # noqa: F401

        # Create all tables
        db.create_all()

        # Initialize default data if needed
        _init_default_data()


def _init_default_data() -> None:
    """Initialize default data (roles, permissions, admin user)."""
    from apps.api.models import Role, Permission, RolePermission, Identity, UserRole
    from apps.api.models.identity import IdentityType, AuthProvider
    from apps.api.models.rbac import RoleScope
    import os
    from werkzeug.security import generate_password_hash

    # Check if roles already exist
    if Role.query.count() > 0:
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
        role = Role(**role_data)
        db.session.add(role)
        roles[role_data["name"]] = role

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
        perm = Permission(**perm_data)
        db.session.add(perm)
        permissions[perm_data["name"]] = perm

    db.session.flush()  # Flush to get IDs

    # Assign permissions to roles
    role_permissions_map = {
        "super_admin": list(permissions.keys()),  # All permissions
        "org_admin": [
            "create_entity",
            "edit_entity",
            "delete_entity",
            "view_entity",
            "view_organization",
            "create_dependency",
            "delete_dependency",
            "view_dependency",
            "view_users",
            "view_audit_logs",
        ],
        "editor": [
            "create_entity",
            "edit_entity",
            "view_entity",
            "view_organization",
            "create_dependency",
            "view_dependency",
        ],
        "viewer": [
            "view_entity",
            "view_organization",
            "view_dependency",
        ],
    }

    for role_name, perm_names in role_permissions_map.items():
        role = roles[role_name]
        for perm_name in perm_names:
            perm = permissions[perm_name]
            role_perm = RolePermission(role=role, permission=perm)
            db.session.add(role_perm)

    # Create default admin user if specified in environment
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if admin_password:
        admin = Identity(
            username=admin_username,
            email=os.getenv("ADMIN_EMAIL", f"{admin_username}@localhost"),
            full_name="System Administrator",
            identity_type=IdentityType.HUMAN,
            auth_provider=AuthProvider.LOCAL,
            password_hash=generate_password_hash(admin_password),
            is_active=True,
            is_superuser=True,
        )
        db.session.add(admin)
        db.session.flush()

        # Assign super_admin role
        user_role = UserRole(
            identity=admin,
            role=roles["super_admin"],
            scope=RoleScope.GLOBAL,
        )
        db.session.add(user_role)

    db.session.commit()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session context manager.

    Yields:
        Database session

    Example:
        with get_db_session() as session:
            user = session.query(Identity).first()
    """
    session = db.session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
