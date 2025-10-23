"""Marshmallow schemas for MetadataField model."""

from marshmallow import Schema, fields, validate, validates, ValidationError

from apps.api.models.metadata import MetadataFieldType


class MetadataFieldSchema(Schema):
    """Schema for MetadataField serialization and validation."""

    id = fields.Int(dump_only=True)

    # Resource association
    resource_type = fields.Str(dump_only=True)
    resource_id = fields.Int(dump_only=True)

    # Field definition
    field_key = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    field_type = fields.Str(
        required=True, validate=validate.OneOf([ft.value for ft in MetadataFieldType])
    )

    # Value (will be decoded from JSON)
    field_value = fields.Raw(dump_only=True)  # Returned as decoded value
    value = fields.Raw(dump_only=True)  # Alias for field_value

    # System metadata flag
    is_system = fields.Bool(dump_only=True)

    # Creator
    created_by_id = fields.Int(dump_only=True)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships
    created_by = fields.Nested(
        "IdentitySchema", only=("id", "username", "full_name"), dump_only=True
    )

    class Meta:
        """Schema metadata."""

        ordered = True


class MetadataFieldCreateSchema(Schema):
    """Schema for creating a metadata field."""

    field_key = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    field_type = fields.Str(
        required=True, validate=validate.OneOf([ft.value for ft in MetadataFieldType])
    )
    value = fields.Raw(required=True)  # Value will be type-checked by model

    @validates("field_key")
    def validate_field_key(self, value):
        """Validate field key format."""
        # Field keys should be alphanumeric with underscores (like variable names)
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", value):
            raise ValidationError(
                "Field key must start with letter or underscore and contain only alphanumeric characters and underscores"
            )


class MetadataFieldUpdateSchema(Schema):
    """Schema for updating a metadata field."""

    field_type = fields.Str(validate=validate.OneOf([ft.value for ft in MetadataFieldType]))
    value = fields.Raw(required=True)


class MetadataFieldListSchema(Schema):
    """Schema for metadata field list response."""

    items = fields.Nested(MetadataFieldSchema, many=True)
    total = fields.Int()


class MetadataDictSchema(Schema):
    """
    Schema for metadata as a simple key-value dictionary.

    Used for simplified responses that just show metadata as a dict.
    """

    metadata = fields.Dict(
        keys=fields.Str(), values=fields.Raw(), dump_only=True
    )
