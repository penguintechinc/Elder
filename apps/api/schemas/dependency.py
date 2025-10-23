"""Marshmallow schemas for Dependency model."""

from marshmallow import Schema, fields, validate

from apps.api.models.dependency import DependencyType


class DependencySchema(Schema):
    """Schema for Dependency serialization and validation."""

    id = fields.Int(dump_only=True)

    # Source and target
    source_entity_id = fields.Int(required=True)
    target_entity_id = fields.Int(required=True)

    # Type
    dependency_type = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in DependencyType])
    )

    # Metadata
    metadata = fields.Dict(allow_none=True)

    # Timestamp
    created_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional)
    source_entity = fields.Nested(
        "EntitySchema",
        only=("id", "name", "entity_type"),
        dump_only=True
    )
    target_entity = fields.Nested(
        "EntitySchema",
        only=("id", "name", "entity_type"),
        dump_only=True
    )

    class Meta:
        """Schema metadata."""
        ordered = True


class DependencyCreateSchema(Schema):
    """Schema for creating a dependency."""

    source_entity_id = fields.Int(required=True)
    target_entity_id = fields.Int(required=True)
    dependency_type = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in DependencyType])
    )
    metadata = fields.Dict(allow_none=True)


class DependencyListSchema(Schema):
    """Schema for dependency list response with pagination."""

    items = fields.Nested(DependencySchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()


class DependencyFilterSchema(Schema):
    """Schema for dependency filtering parameters."""

    source_entity_id = fields.Int()
    target_entity_id = fields.Int()
    dependency_type = fields.Str(validate=validate.OneOf([e.value for e in DependencyType]))
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=50, validate=validate.Range(min=1, max=1000))
