"""Entity API endpoints - Full CRUD operations."""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from apps.api.models import Entity
from apps.api.schemas.entity import (
    EntitySchema,
    EntityCreateSchema,
    EntityUpdateSchema,
    EntityListSchema,
    EntityFilterSchema,
)
from shared.database import db
from shared.api_utils import (
    paginate,
    validate_request,
    make_error_response,
    apply_filters,
    get_or_404,
    handle_validation_error,
)

bp = Blueprint("entities", __name__)


@bp.route("", methods=["GET"])
def list_entities():
    """
    List all entities with pagination and filtering.

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 1000)
        - entity_type: Filter by entity type
        - organization_id: Filter by organization ID
        - owner_identity_id: Filter by owner identity ID
        - name: Filter by name (partial match)

    Returns:
        200: List of entities with pagination metadata
    """
    # Validate query parameters
    try:
        filter_data = EntityFilterSchema().load(request.args)
    except ValidationError as e:
        return handle_validation_error(e)

    # Build base query
    query = Entity.query

    # Apply filters
    filters = {
        "entity_type": filter_data.get("entity_type"),
        "organization_id": filter_data.get("organization_id"),
        "owner_identity_id": filter_data.get("owner_identity_id"),
        "name": filter_data.get("name"),
    }
    query = apply_filters(query, Entity, filters)

    # Order by name
    query = query.order_by(Entity.name)

    # Paginate
    items, pagination = paginate(
        query,
        page=filter_data["page"],
        per_page=filter_data["per_page"],
    )

    # Serialize
    schema = EntitySchema(many=True)
    list_schema = EntityListSchema()

    result = list_schema.dump({
        "items": schema.dump(items),
        **pagination,
    })

    return jsonify(result), 200


@bp.route("", methods=["POST"])
def create_entity():
    """
    Create a new entity.

    Request Body:
        JSON object with entity fields (see EntityCreateSchema)

    Returns:
        201: Created entity
        400: Validation error
    """
    try:
        data = validate_request(EntityCreateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Convert entity_type string to enum
    from apps.api.models.entity import EntityType
    data["entity_type"] = EntityType(data["entity_type"])

    # Create entity
    entity = Entity(**data)
    db.session.add(entity)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    schema = EntitySchema()
    return jsonify(schema.dump(entity)), 201


@bp.route("/<int:id>", methods=["GET"])
def get_entity(id: int):
    """
    Get a single entity by ID.

    Path Parameters:
        - id: Entity ID

    Returns:
        200: Entity details
        404: Entity not found
    """
    entity = get_or_404(Entity, id)

    schema = EntitySchema()
    return jsonify(schema.dump(entity)), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
def update_entity(id: int):
    """
    Update an entity (full edit support).

    Path Parameters:
        - id: Entity ID

    Request Body:
        JSON object with fields to update (see EntityUpdateSchema)

    Returns:
        200: Updated entity
        400: Validation error
        404: Entity not found
    """
    entity = get_or_404(Entity, id)

    try:
        data = validate_request(EntityUpdateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Convert entity_type string to enum if provided
    if "entity_type" in data:
        from apps.api.models.entity import EntityType
        data["entity_type"] = EntityType(data["entity_type"])

    # Update fields
    for key, value in data.items():
        setattr(entity, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    schema = EntitySchema()
    return jsonify(schema.dump(entity)), 200


@bp.route("/<int:id>", methods=["DELETE"])
def delete_entity(id: int):
    """
    Delete an entity.

    Path Parameters:
        - id: Entity ID

    Returns:
        204: Entity deleted
        404: Entity not found
        400: Cannot delete entity with dependencies
    """
    entity = get_or_404(Entity, id)

    # Check for dependencies
    total_deps = len(entity.outgoing_dependencies) + len(entity.incoming_dependencies)
    if total_deps > 0:
        return make_error_response(
            f"Cannot delete entity with {total_deps} dependencies. Remove dependencies first.",
            400,
        )

    try:
        db.session.delete(entity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return "", 204


@bp.route("/<int:id>/dependencies", methods=["GET"])
def get_entity_dependencies(id: int):
    """
    Get all dependencies for an entity.

    Path Parameters:
        - id: Entity ID

    Query Parameters:
        - direction: 'outgoing' (depends on), 'incoming' (depended by), or 'all' (default)
        - depth: Maximum depth for recursive dependencies (default: 1, -1 for unlimited)

    Returns:
        200: Dependencies information
        404: Entity not found
    """
    entity = get_or_404(Entity, id)

    direction = request.args.get("direction", "all")
    depth = request.args.get("depth", 1, type=int)

    result = {
        "entity_id": entity.id,
        "entity_name": entity.name,
    }

    if direction in ("outgoing", "all"):
        # Entities this entity depends on
        if depth == 1:
            outgoing = entity.outgoing_dependencies
        else:
            # Get recursive dependencies
            deps = entity.get_all_dependencies(depth=depth)
            outgoing = [Entity.query.get(d.id) for d in deps if d]

        from apps.api.schemas.dependency import DependencySchema
        result["depends_on"] = DependencySchema(many=True).dump(outgoing)

    if direction in ("incoming", "all"):
        # Entities that depend on this entity
        if depth == 1:
            incoming = entity.incoming_dependencies
        else:
            # Get recursive dependents
            deps = entity.get_all_dependents(depth=depth)
            incoming = [Entity.query.get(d.id) for d in deps if d]

        from apps.api.schemas.dependency import DependencySchema
        result["depended_by"] = DependencySchema(many=True).dump(incoming)

    return jsonify(result), 200


@bp.route("/<int:id>/metadata", methods=["PATCH"])
def update_entity_metadata(id: int):
    """
    Update entity metadata (for type-specific fields).

    Path Parameters:
        - id: Entity ID

    Request Body:
        JSON object with metadata fields to update

    Returns:
        200: Updated entity
        404: Entity not found
    """
    entity = get_or_404(Entity, id)

    data = request.get_json() or {}

    if not isinstance(data, dict):
        return make_error_response("Metadata must be a JSON object", 400)

    # Update metadata fields
    if entity.metadata is None:
        entity.metadata = {}

    entity.metadata.update(data)

    try:
        # Mark as modified for SQLAlchemy to detect change
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(entity, "metadata")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    schema = EntitySchema()
    return jsonify(schema.dump(entity)), 200
