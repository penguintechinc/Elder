"""Marshmallow schemas for Entity model."""

from marshmallow import Schema, fields, validate, validates, ValidationError

from apps.api.models.entity import EntityType


class EntitySchema(Schema):
    """Schema for Entity serialization and validation."""

    id = fields.Int(dump_only=True)
    unique_id = fields.Int(dump_only=True, description="Unique 64-bit identifier for lookups")
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)

    # Type
    entity_type = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in EntityType])
    )

    # Organization relationship
    organization_id = fields.Int(required=True)

    # Ownership
    owner_identity_id = fields.Int(allow_none=True)

    # Type-specific metadata
    metadata = fields.Dict(allow_none=True)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional)
    organization = fields.Nested(
        "OrganizationSchema",
        only=("id", "name"),
        dump_only=True
    )
    owner = fields.Nested(
        "IdentitySchema",
        only=("id", "username", "full_name"),
        dump_only=True
    )

    class Meta:
        """Schema metadata."""
        ordered = True


class EntityCreateSchema(Schema):
    """Schema for creating an entity."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    entity_type = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in EntityType])
    )
    organization_id = fields.Int(required=True)
    owner_identity_id = fields.Int(allow_none=True)
    metadata = fields.Dict(allow_none=True)


class EntityUpdateSchema(Schema):
    """Schema for updating an entity."""

    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    entity_type = fields.Str(validate=validate.OneOf([e.value for e in EntityType]))
    organization_id = fields.Int()
    owner_identity_id = fields.Int(allow_none=True)
    metadata = fields.Dict(allow_none=True)


class EntityListSchema(Schema):
    """Schema for entity list response with pagination."""

    items = fields.Nested(EntitySchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()


class EntityFilterSchema(Schema):
    """Schema for entity filtering parameters."""

    entity_type = fields.Str(validate=validate.OneOf([e.value for e in EntityType]))
    organization_id = fields.Int()
    owner_identity_id = fields.Int()
    name = fields.Str()  # Partial match
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=50, validate=validate.Range(min=1, max=1000))
