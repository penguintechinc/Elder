"""Metadata management API endpoints for Elder enterprise features."""

from flask import Blueprint, jsonify, request, g
from marshmallow import ValidationError

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.metadata import MetadataField, MetadataFieldType
from apps.api.schemas.metadata import (
    MetadataFieldSchema,
    MetadataFieldCreateSchema,
    MetadataFieldUpdateSchema,
    MetadataFieldListSchema,
    MetadataDictSchema,
)
from shared.api_utils import get_or_404, make_error_response
from shared.database import db
from shared.licensing import license_required

bp = Blueprint("metadata", __name__)


# ============================================================================
# Entity Metadata Endpoints
# ============================================================================


@bp.route("/entities/<int:id>/metadata", methods=["GET"])
@login_required
@license_required("enterprise")
@resource_role_required("viewer", resource_param="id")
def get_entity_metadata(id: int):
    """
    Get all metadata for an entity.

    Requires viewer role on the entity.

    Path Parameters:
        - id: Entity ID

    Returns:
        200: Metadata as key-value dictionary
        403: License required or insufficient permissions
        404: Entity not found

    Example:
        GET /api/v1/metadata/entities/42/metadata
        {
            "metadata": {
                "hostname": "web-01.example.com",
                "ip_address": "10.0.1.5",
                "last_updated": "2024-10-23T10:00:00Z",
                "is_production": true,
                "cpu_count": 8
            }
        }
    """
    from apps.api.models import Entity

    entity = get_or_404(Entity, id)

    # Get all metadata fields
    fields = db.session.query(MetadataField).filter_by(
        resource_type="entity", resource_id=entity.id
    ).all()

    # Build metadata dictionary
    metadata = {field.field_key: field.get_value() for field in fields}

    return jsonify({"metadata": metadata}), 200


@bp.route("/entities/<int:id>/metadata", methods=["POST"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="id")
def create_entity_metadata(id: int):
    """
    Create or update a metadata field for an entity.

    Requires maintainer role on the entity.

    Path Parameters:
        - id: Entity ID

    Request Body:
        {
            "field_key": "hostname",
            "field_type": "string",
            "value": "web-01.example.com"
        }

    Returns:
        201: Metadata field created/updated
        400: Invalid request
        403: License required or insufficient permissions
        404: Entity not found

    Example:
        POST /api/v1/metadata/entities/42/metadata
    """
    from apps.api.models import Entity

    entity = get_or_404(Entity, id)

    # Validate request
    create_schema = MetadataFieldCreateSchema()
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Check if system metadata
    existing = db.session.query(MetadataField).filter_by(
        resource_type="entity", resource_id=entity.id, field_key=data["field_key"]
    ).first()

    if existing and existing.is_system:
        return (
            jsonify(
                {
                    "error": "System metadata",
                    "message": "System metadata fields cannot be modified",
                }
            ),
            403,
        )

    # Create or update metadata field
    try:
        field = MetadataField.set_metadata(
            resource_type="entity",
            resource_id=entity.id,
            field_key=data["field_key"],
            field_type=MetadataFieldType(data["field_type"]),
            value=data["value"],
            created_by_id=g.current_user.id,
        )
        db.session.commit()
    except ValueError as e:
        return make_error_response(f"Invalid value: {str(e)}", 400)

    # Serialize response
    schema = MetadataFieldSchema()
    response_data = schema.dump(field)
    response_data["value"] = field.get_value()

    return jsonify(response_data), 201


@bp.route("/entities/<int:id>/metadata/<string:field_key>", methods=["PATCH"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="id")
def update_entity_metadata(id: int, field_key: str):
    """
    Update a metadata field for an entity.

    Requires maintainer role on the entity.

    Path Parameters:
        - id: Entity ID
        - field_key: Metadata field key

    Request Body:
        {
            "value": "web-02.example.com"
        }

    Returns:
        200: Metadata field updated
        400: Invalid request
        403: License required or insufficient permissions
        404: Entity or metadata field not found

    Example:
        PATCH /api/v1/metadata/entities/42/metadata/hostname
    """
    from apps.api.models import Entity

    entity = get_or_404(Entity, id)

    # Get metadata field
    field = db.session.query(MetadataField).filter_by(
        resource_type="entity", resource_id=entity.id, field_key=field_key
    ).first()

    if not field:
        return make_error_response(f"Metadata field '{field_key}' not found", 404)

    # Check if system metadata
    if field.is_system:
        return (
            jsonify(
                {
                    "error": "System metadata",
                    "message": "System metadata fields cannot be modified",
                }
            ),
            403,
        )

    # Validate request
    update_schema = MetadataFieldUpdateSchema()
    try:
        data = update_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Update field
    try:
        if "field_type" in data:
            field.field_type = MetadataFieldType(data["field_type"])
        field.set_value(data["value"])
        db.session.commit()
    except ValueError as e:
        return make_error_response(f"Invalid value: {str(e)}", 400)

    # Serialize response
    schema = MetadataFieldSchema()
    response_data = schema.dump(field)
    response_data["value"] = field.get_value()

    return jsonify(response_data), 200


@bp.route("/entities/<int:id>/metadata/<string:field_key>", methods=["DELETE"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="id")
def delete_entity_metadata(id: int, field_key: str):
    """
    Delete a metadata field from an entity.

    Requires maintainer role on the entity.

    Path Parameters:
        - id: Entity ID
        - field_key: Metadata field key

    Returns:
        204: Metadata field deleted
        403: License required or insufficient permissions
        404: Entity or metadata field not found

    Example:
        DELETE /api/v1/metadata/entities/42/metadata/hostname
    """
    from apps.api.models import Entity

    entity = get_or_404(Entity, id)

    # Get metadata field
    field = db.session.query(MetadataField).filter_by(
        resource_type="entity", resource_id=entity.id, field_key=field_key
    ).first()

    if not field:
        return make_error_response(f"Metadata field '{field_key}' not found", 404)

    # Check if system metadata
    if field.is_system:
        return (
            jsonify(
                {
                    "error": "System metadata",
                    "message": "System metadata fields cannot be deleted",
                }
            ),
            403,
        )

    # Delete field
    db.session.delete(field)
    db.session.commit()

    return "", 204


# ============================================================================
# Organization Metadata Endpoints
# ============================================================================


@bp.route("/organizations/<int:id>/metadata", methods=["GET"])
@login_required
@license_required("enterprise")
@resource_role_required("viewer", resource_param="id")
def get_organization_metadata(id: int):
    """
    Get all metadata for an organization.

    Requires viewer role on the organization.

    Path Parameters:
        - id: Organization ID

    Returns:
        200: Metadata as key-value dictionary
        403: License required or insufficient permissions
        404: Organization not found

    Example:
        GET /api/v1/metadata/organizations/1/metadata
        {
            "metadata": {
                "budget": 1000000,
                "fiscal_year": "2024",
                "cost_center": "CC-1234"
            }
        }
    """
    from apps.api.models import Organization

    org = get_or_404(Organization, id)

    # Get all metadata fields
    fields = db.session.query(MetadataField).filter_by(
        resource_type="organization", resource_id=org.id
    ).all()

    # Build metadata dictionary
    metadata = {field.field_key: field.get_value() for field in fields}

    return jsonify({"metadata": metadata}), 200


@bp.route("/organizations/<int:id>/metadata", methods=["POST"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="id")
def create_organization_metadata(id: int):
    """
    Create or update a metadata field for an organization.

    Requires maintainer role on the organization.

    Path Parameters:
        - id: Organization ID

    Request Body:
        {
            "field_key": "budget",
            "field_type": "number",
            "value": 1000000
        }

    Returns:
        201: Metadata field created/updated
        400: Invalid request
        403: License required or insufficient permissions
        404: Organization not found

    Example:
        POST /api/v1/metadata/organizations/1/metadata
    """
    from apps.api.models import Organization

    org = get_or_404(Organization, id)

    # Validate request
    create_schema = MetadataFieldCreateSchema()
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Check if system metadata
    existing = db.session.query(MetadataField).filter_by(
        resource_type="organization", resource_id=org.id, field_key=data["field_key"]
    ).first()

    if existing and existing.is_system:
        return (
            jsonify(
                {
                    "error": "System metadata",
                    "message": "System metadata fields cannot be modified",
                }
            ),
            403,
        )

    # Create or update metadata field
    try:
        field = MetadataField.set_metadata(
            resource_type="organization",
            resource_id=org.id,
            field_key=data["field_key"],
            field_type=MetadataFieldType(data["field_type"]),
            value=data["value"],
            created_by_id=g.current_user.id,
        )
        db.session.commit()
    except ValueError as e:
        return make_error_response(f"Invalid value: {str(e)}", 400)

    # Serialize response
    schema = MetadataFieldSchema()
    response_data = schema.dump(field)
    response_data["value"] = field.get_value()

    return jsonify(response_data), 201


@bp.route("/organizations/<int:id>/metadata/<string:field_key>", methods=["PATCH"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="id")
def update_organization_metadata(id: int, field_key: str):
    """
    Update a metadata field for an organization.

    Requires maintainer role on the organization.

    Path Parameters:
        - id: Organization ID
        - field_key: Metadata field key

    Request Body:
        {
            "value": 1500000
        }

    Returns:
        200: Metadata field updated
        400: Invalid request
        403: License required or insufficient permissions
        404: Organization or metadata field not found

    Example:
        PATCH /api/v1/metadata/organizations/1/metadata/budget
    """
    from apps.api.models import Organization

    org = get_or_404(Organization, id)

    # Get metadata field
    field = db.session.query(MetadataField).filter_by(
        resource_type="organization", resource_id=org.id, field_key=field_key
    ).first()

    if not field:
        return make_error_response(f"Metadata field '{field_key}' not found", 404)

    # Check if system metadata
    if field.is_system:
        return (
            jsonify(
                {
                    "error": "System metadata",
                    "message": "System metadata fields cannot be modified",
                }
            ),
            403,
        )

    # Validate request
    update_schema = MetadataFieldUpdateSchema()
    try:
        data = update_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Update field
    try:
        if "field_type" in data:
            field.field_type = MetadataFieldType(data["field_type"])
        field.set_value(data["value"])
        db.session.commit()
    except ValueError as e:
        return make_error_response(f"Invalid value: {str(e)}", 400)

    # Serialize response
    schema = MetadataFieldSchema()
    response_data = schema.dump(field)
    response_data["value"] = field.get_value()

    return jsonify(response_data), 200


@bp.route("/organizations/<int:id>/metadata/<string:field_key>", methods=["DELETE"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="id")
def delete_organization_metadata(id: int, field_key: str):
    """
    Delete a metadata field from an organization.

    Requires maintainer role on the organization.

    Path Parameters:
        - id: Organization ID
        - field_key: Metadata field key

    Returns:
        204: Metadata field deleted
        403: License required or insufficient permissions
        404: Organization or metadata field not found

    Example:
        DELETE /api/v1/metadata/organizations/1/metadata/budget
    """
    from apps.api.models import Organization

    org = get_or_404(Organization, id)

    # Get metadata field
    field = db.session.query(MetadataField).filter_by(
        resource_type="organization", resource_id=org.id, field_key=field_key
    ).first()

    if not field:
        return make_error_response(f"Metadata field '{field_key}' not found", 404)

    # Check if system metadata
    if field.is_system:
        return (
            jsonify(
                {
                    "error": "System metadata",
                    "message": "System metadata fields cannot be deleted",
                }
            ),
            403,
        )

    # Delete field
    db.session.delete(field)
    db.session.commit()

    return "", 204
