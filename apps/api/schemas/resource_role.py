"""Marshmallow schemas for ResourceRole model."""

from marshmallow import Schema, fields, validate, validates, ValidationError

from apps.api.models.resource_role import ResourceType, ResourceRoleType


class ResourceRoleSchema(Schema):
    """Schema for ResourceRole serialization and validation."""

    id = fields.Int(dump_only=True)

    # Identity who has this role
    identity_id = fields.Int(required=True)

    # Resource identification
    resource_type = fields.Str(
        required=True, validate=validate.OneOf([rt.value for rt in ResourceType])
    )
    resource_id = fields.Int(required=True)

    # Role type
    role_type = fields.Str(
        required=True, validate=validate.OneOf([rrt.value for rrt in ResourceRoleType])
    )

    # Who granted this role
    granted_by_id = fields.Int(dump_only=True)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional)
    identity = fields.Nested(
        "IdentitySchema", only=("id", "username", "full_name"), dump_only=True
    )
    granted_by = fields.Nested(
        "IdentitySchema", only=("id", "username", "full_name"), dump_only=True
    )

    class Meta:
        """Schema metadata."""

        ordered = True


class ResourceRoleCreateSchema(Schema):
    """Schema for creating a resource role assignment."""

    identity_id = fields.Int(required=True)
    resource_type = fields.Str(
        required=True, validate=validate.OneOf([rt.value for rt in ResourceType])
    )
    resource_id = fields.Int(required=True)
    role_type = fields.Str(
        required=True, validate=validate.OneOf([rrt.value for rrt in ResourceRoleType])
    )


class ResourceRoleFilterSchema(Schema):
    """Schema for resource role filtering parameters."""

    identity_id = fields.Int()
    resource_type = fields.Str(validate=validate.OneOf([rt.value for rt in ResourceType]))
    resource_id = fields.Int()
    role_type = fields.Str(validate=validate.OneOf([rrt.value for rrt in ResourceRoleType]))


class ResourceRoleListSchema(Schema):
    """Schema for resource role list response."""

    items = fields.Nested(ResourceRoleSchema, many=True)
    total = fields.Int()
