"""Marshmallow schemas for Elder API."""

from apps.api.schemas.organization import OrganizationSchema
from apps.api.schemas.entity import EntitySchema
from apps.api.schemas.dependency import DependencySchema
from apps.api.schemas.identity import IdentitySchema, IdentityGroupSchema
from apps.api.schemas.rbac import RoleSchema, PermissionSchema

__all__ = [
    "OrganizationSchema",
    "EntitySchema",
    "DependencySchema",
    "IdentitySchema",
    "IdentityGroupSchema",
    "RoleSchema",
    "PermissionSchema",
]
