"""Marshmallow schemas for Issue models."""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime, timezone

from apps.api.models.issue import IssueStatus, IssuePriority, IssueLinkType


class IssueLabelSchema(Schema):
    """Schema for IssueLabel serialization and validation."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    color = fields.Str(validate=validate.Regexp(r"^#[0-9A-Fa-f]{6}$"))  # Hex color
    description = fields.Str(allow_none=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        """Schema metadata."""

        ordered = True


class IssueCommentSchema(Schema):
    """Schema for IssueComment serialization and validation."""

    id = fields.Int(dump_only=True)
    issue_id = fields.Int(dump_only=True)
    author_id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=validate.Length(min=1))

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships
    author = fields.Nested(
        "IdentitySchema", only=("id", "username", "full_name"), dump_only=True
    )

    class Meta:
        """Schema metadata."""

        ordered = True


class IssueEntityLinkSchema(Schema):
    """Schema for IssueEntityLink serialization and validation."""

    id = fields.Int(dump_only=True)
    issue_id = fields.Int(dump_only=True)
    entity_id = fields.Int(required=True)
    link_type = fields.Str(
        required=True, validate=validate.OneOf([lt.value for lt in IssueLinkType])
    )

    created_at = fields.DateTime(dump_only=True)

    # Nested relationships
    entity = fields.Nested(
        "EntitySchema", only=("id", "name", "entity_type"), dump_only=True
    )

    class Meta:
        """Schema metadata."""

        ordered = True


class IssueSchema(Schema):
    """Schema for Issue serialization and validation."""

    id = fields.Int(dump_only=True)

    # Resource association
    resource_type = fields.Str(required=True, validate=validate.OneOf(["entity", "organization"]))
    resource_id = fields.Int(required=True)

    # Core fields
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)

    # Status and priority
    status = fields.Str(validate=validate.OneOf([s.value for s in IssueStatus]))
    priority = fields.Str(validate=validate.OneOf([p.value for p in IssuePriority]))

    # User relationships
    created_by_id = fields.Int(dump_only=True)
    assigned_to_id = fields.Int(allow_none=True)

    # Dates
    due_date = fields.DateTime(allow_none=True)
    closed_at = fields.DateTime(dump_only=True)
    closed_by_id = fields.Int(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships
    created_by = fields.Nested(
        "IdentitySchema", only=("id", "username", "full_name"), dump_only=True
    )
    assigned_to = fields.Nested(
        "IdentitySchema", only=("id", "username", "full_name"), dump_only=True
    )
    closed_by = fields.Nested(
        "IdentitySchema", only=("id", "username", "full_name"), dump_only=True
    )

    labels = fields.Nested(IssueLabelSchema, many=True, dump_only=True)
    comments = fields.Nested(IssueCommentSchema, many=True, dump_only=True)
    entity_links = fields.Nested(IssueEntityLinkSchema, many=True, dump_only=True)

    class Meta:
        """Schema metadata."""

        ordered = True


class IssueCreateSchema(Schema):
    """Schema for creating an issue."""

    resource_type = fields.Str(required=True, validate=validate.OneOf(["entity", "organization"]))
    resource_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    priority = fields.Str(
        missing="medium", validate=validate.OneOf([p.value for p in IssuePriority])
    )
    assigned_to_id = fields.Int(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    label_ids = fields.List(fields.Int(), missing=list)


class IssueUpdateSchema(Schema):
    """Schema for updating an issue."""

    title = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf([s.value for s in IssueStatus]))
    priority = fields.Str(validate=validate.OneOf([p.value for p in IssuePriority]))
    assigned_to_id = fields.Int(allow_none=True)
    due_date = fields.DateTime(allow_none=True)


class IssueFilterSchema(Schema):
    """Schema for issue filtering parameters."""

    resource_type = fields.Str(validate=validate.OneOf(["entity", "organization"]))
    resource_id = fields.Int()
    status = fields.Str(validate=validate.OneOf([s.value for s in IssueStatus]))
    priority = fields.Str(validate=validate.OneOf([p.value for p in IssuePriority]))
    assigned_to_id = fields.Int()
    created_by_id = fields.Int()
    label_id = fields.Int()
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=50, validate=validate.Range(min=1, max=1000))


class IssueListSchema(Schema):
    """Schema for issue list response with pagination."""

    items = fields.Nested(IssueSchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()


class IssueCommentCreateSchema(Schema):
    """Schema for creating an issue comment."""

    content = fields.Str(required=True, validate=validate.Length(min=1))


class IssueLabelCreateSchema(Schema):
    """Schema for creating an issue label."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    color = fields.Str(
        missing="#808080", validate=validate.Regexp(r"^#[0-9A-Fa-f]{6}$")
    )
    description = fields.Str(allow_none=True)


class IssueEntityLinkCreateSchema(Schema):
    """Schema for creating an entity link."""

    entity_id = fields.Int(required=True)
    link_type = fields.Str(
        missing="related", validate=validate.OneOf([lt.value for lt in IssueLinkType])
    )
