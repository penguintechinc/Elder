"""Marshmallow schemas for Organization model."""

from marshmallow import Schema, fields, validate, validates, ValidationError


class OrganizationSchema(Schema):
    """Schema for Organization serialization and validation."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)

    # Hierarchical relationship
    parent_id = fields.Int(allow_none=True)

    # LDAP/SAML integration
    ldap_dn = fields.Str(allow_none=True, validate=validate.Length(max=512))
    saml_group = fields.Str(allow_none=True, validate=validate.Length(max=255))

    # Ownership
    owner_identity_id = fields.Int(allow_none=True)
    owner_group_id = fields.Int(allow_none=True)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional, for detailed responses)
    parent = fields.Nested("OrganizationSchema", only=("id", "name"), dump_only=True)
    children = fields.Nested("OrganizationSchema", many=True, only=("id", "name"), dump_only=True)

    class Meta:
        """Schema metadata."""
        ordered = True


class OrganizationCreateSchema(Schema):
    """Schema for creating an organization."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    parent_id = fields.Int(allow_none=True)
    ldap_dn = fields.Str(allow_none=True, validate=validate.Length(max=512))
    saml_group = fields.Str(allow_none=True, validate=validate.Length(max=255))
    owner_identity_id = fields.Int(allow_none=True)
    owner_group_id = fields.Int(allow_none=True)


class OrganizationUpdateSchema(Schema):
    """Schema for updating an organization."""

    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    parent_id = fields.Int(allow_none=True)
    ldap_dn = fields.Str(allow_none=True, validate=validate.Length(max=512))
    saml_group = fields.Str(allow_none=True, validate=validate.Length(max=255))
    owner_identity_id = fields.Int(allow_none=True)
    owner_group_id = fields.Int(allow_none=True)


class OrganizationListSchema(Schema):
    """Schema for organization list response with pagination."""

    items = fields.Nested(OrganizationSchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()
