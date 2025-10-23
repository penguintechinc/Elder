"""Marshmallow schemas for RBAC models."""

from marshmallow import Schema, fields, validate

from apps.api.models.rbac import RoleScope


class PermissionSchema(Schema):
    """Schema for Permission serialization."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True, validate=validate.Length(max=512))
    resource_type = fields.Str(required=True, validate=validate.Length(max=50))
    action = fields.Str(required=True, validate=validate.Length(max=50))

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        """Schema metadata."""
        ordered = True


class RoleSchema(Schema):
    """Schema for Role serialization."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True, validate=validate.Length(max=512))

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional)
    permissions = fields.Nested(
        PermissionSchema,
        many=True,
        only=("id", "name", "resource_type", "action"),
        dump_only=True
    )

    class Meta:
        """Schema metadata."""
        ordered = True


class UserRoleSchema(Schema):
    """Schema for UserRole serialization."""

    id = fields.Int(dump_only=True)
    identity_id = fields.Int(required=True)
    role_id = fields.Int(required=True)
    scope = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in RoleScope])
    )
    organization_id = fields.Int(allow_none=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional)
    role = fields.Nested(
        RoleSchema,
        only=("id", "name"),
        dump_only=True
    )
    organization = fields.Nested(
        "OrganizationSchema",
        only=("id", "name"),
        dump_only=True
    )

    class Meta:
        """Schema metadata."""
        ordered = True


class UserRoleAssignSchema(Schema):
    """Schema for assigning roles to users."""

    identity_id = fields.Int(required=True)
    role_id = fields.Int(required=True)
    scope = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in RoleScope])
    )
    organization_id = fields.Int(allow_none=True)
