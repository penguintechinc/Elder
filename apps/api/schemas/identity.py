"""Marshmallow schemas for Identity models."""

from marshmallow import Schema, fields, validate

from apps.api.models.identity import IdentityType, AuthProvider


class IdentitySchema(Schema):
    """Schema for Identity serialization and validation."""

    id = fields.Int(dump_only=True)

    # Type
    identity_type = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in IdentityType])
    )

    # Core fields
    username = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(allow_none=True)
    full_name = fields.Str(allow_none=True, validate=validate.Length(max=255))

    # Authentication
    auth_provider = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in AuthProvider])
    )
    auth_provider_id = fields.Str(allow_none=True, validate=validate.Length(max=255))

    # Status
    is_active = fields.Bool()
    is_superuser = fields.Bool()

    # MFA
    mfa_enabled = fields.Bool()

    # Last activity
    last_login_at = fields.Str(allow_none=True)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional)
    groups = fields.Nested(
        "IdentityGroupSchema",
        many=True,
        only=("id", "name"),
        dump_only=True
    )

    class Meta:
        """Schema metadata."""
        ordered = True
        # Exclude sensitive fields
        exclude = ("password_hash", "mfa_secret")


class IdentityCreateSchema(Schema):
    """Schema for creating an identity."""

    identity_type = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in IdentityType])
    )
    username = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(allow_none=True)
    full_name = fields.Str(allow_none=True, validate=validate.Length(max=255))
    auth_provider = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in AuthProvider])
    )
    password = fields.Str(validate=validate.Length(min=8, max=255), load_only=True)
    is_active = fields.Bool(missing=True)


class IdentityUpdateSchema(Schema):
    """Schema for updating an identity."""

    email = fields.Email(allow_none=True)
    full_name = fields.Str(allow_none=True, validate=validate.Length(max=255))
    is_active = fields.Bool()
    mfa_enabled = fields.Bool()


class IdentityListSchema(Schema):
    """Schema for identity list response with pagination."""

    items = fields.Nested(IdentitySchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()


class IdentityGroupSchema(Schema):
    """Schema for IdentityGroup serialization and validation."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=512))

    # LDAP/SAML
    ldap_dn = fields.Str(allow_none=True, validate=validate.Length(max=512))
    saml_group = fields.Str(allow_none=True, validate=validate.Length(max=255))

    # Status
    is_active = fields.Bool()

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships (optional)
    members = fields.Nested(
        IdentitySchema,
        many=True,
        only=("id", "username", "full_name"),
        dump_only=True
    )

    class Meta:
        """Schema metadata."""
        ordered = True


class IdentityGroupCreateSchema(Schema):
    """Schema for creating an identity group."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=512))
    ldap_dn = fields.Str(allow_none=True, validate=validate.Length(max=512))
    saml_group = fields.Str(allow_none=True, validate=validate.Length(max=255))
    is_active = fields.Bool(missing=True)


class IdentityGroupUpdateSchema(Schema):
    """Schema for updating an identity group."""

    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=512))
    ldap_dn = fields.Str(allow_none=True, validate=validate.Length(max=512))
    saml_group = fields.Str(allow_none=True, validate=validate.Length(max=255))
    is_active = fields.Bool()
