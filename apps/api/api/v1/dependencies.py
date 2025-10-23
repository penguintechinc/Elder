"""Dependency API endpoints - Full CRUD operations for relationship management."""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from apps.api.models import Dependency, Entity
from apps.api.schemas.dependency import (
    DependencySchema,
    DependencyCreateSchema,
    DependencyListSchema,
    DependencyFilterSchema,
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

bp = Blueprint("dependencies", __name__)


@bp.route("", methods=["GET"])
def list_dependencies():
    """
    List all dependencies with pagination and filtering.

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 1000)
        - source_entity_id: Filter by source entity ID
        - target_entity_id: Filter by target entity ID
        - dependency_type: Filter by dependency type

    Returns:
        200: List of dependencies with pagination metadata
    """
    # Validate query parameters
    try:
        filter_data = DependencyFilterSchema().load(request.args)
    except ValidationError as e:
        return handle_validation_error(e)

    # Build base query
    query = Dependency.query

    # Apply filters
    filters = {
        "source_entity_id": filter_data.get("source_entity_id"),
        "target_entity_id": filter_data.get("target_entity_id"),
        "dependency_type": filter_data.get("dependency_type"),
    }
    query = apply_filters(query, Dependency, filters)

    # Order by created_at (newest first)
    query = query.order_by(Dependency.created_at.desc())

    # Paginate
    items, pagination = paginate(
        query,
        page=filter_data["page"],
        per_page=filter_data["per_page"],
    )

    # Serialize
    schema = DependencySchema(many=True)
    list_schema = DependencyListSchema()

    result = list_schema.dump({
        "items": schema.dump(items),
        **pagination,
    })

    return jsonify(result), 200


@bp.route("", methods=["POST"])
def create_dependency():
    """
    Create a new dependency relationship.

    Request Body:
        JSON object with dependency fields (see DependencyCreateSchema)

    Returns:
        201: Created dependency
        400: Validation error or invalid entity IDs
        409: Dependency already exists
    """
    try:
        data = validate_request(DependencyCreateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Validate that source and target entities exist
    source = db.session.get(Entity, data["source_entity_id"])
    target = db.session.get(Entity, data["target_entity_id"])

    if not source:
        return make_error_response(
            f"Source entity {data['source_entity_id']} not found",
            400,
        )

    if not target:
        return make_error_response(
            f"Target entity {data['target_entity_id']} not found",
            400,
        )

    # Prevent self-dependencies
    if data["source_entity_id"] == data["target_entity_id"]:
        return make_error_response(
            "Cannot create dependency from entity to itself",
            400,
        )

    # Check if dependency already exists
    existing = Dependency.query.filter_by(
        source_entity_id=data["source_entity_id"],
        target_entity_id=data["target_entity_id"],
        dependency_type=data["dependency_type"],
    ).first()

    if existing:
        return make_error_response(
            "Dependency already exists",
            409,
            dependency_id=existing.id,
        )

    # Convert dependency_type string to enum
    from apps.api.models.dependency import DependencyType
    data["dependency_type"] = DependencyType(data["dependency_type"])

    # Create dependency
    dependency = Dependency(**data)
    db.session.add(dependency)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    schema = DependencySchema()
    return jsonify(schema.dump(dependency)), 201


@bp.route("/<int:id>", methods=["GET"])
def get_dependency(id: int):
    """
    Get a single dependency by ID.

    Path Parameters:
        - id: Dependency ID

    Returns:
        200: Dependency details
        404: Dependency not found
    """
    dependency = get_or_404(Dependency, id)

    schema = DependencySchema()
    return jsonify(schema.dump(dependency)), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
def update_dependency(id: int):
    """
    Update a dependency (edit relationship type or metadata).

    Path Parameters:
        - id: Dependency ID

    Request Body:
        JSON object with fields to update (dependency_type and/or metadata)

    Returns:
        200: Updated dependency
        400: Validation error
        404: Dependency not found
    """
    dependency = get_or_404(Dependency, id)

    data = request.get_json() or {}

    # Validate dependency_type if provided
    if "dependency_type" in data:
        from apps.api.models.dependency import DependencyType
        try:
            data["dependency_type"] = DependencyType(data["dependency_type"])
        except ValueError:
            return make_error_response(
                f"Invalid dependency_type: {data['dependency_type']}",
                400,
            )

    # Update allowed fields
    for key in ["dependency_type", "metadata"]:
        if key in data:
            setattr(dependency, key, data[key])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    schema = DependencySchema()
    return jsonify(schema.dump(dependency)), 200


@bp.route("/<int:id>", methods=["DELETE"])
def delete_dependency(id: int):
    """
    Delete a dependency relationship.

    Path Parameters:
        - id: Dependency ID

    Returns:
        204: Dependency deleted
        404: Dependency not found
    """
    dependency = get_or_404(Dependency, id)

    try:
        db.session.delete(dependency)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return "", 204


@bp.route("/bulk", methods=["POST"])
def create_bulk_dependencies():
    """
    Create multiple dependencies at once.

    Request Body:
        JSON array of dependency objects

    Returns:
        201: Created dependencies
        400: Validation error
    """
    data = request.get_json() or []

    if not isinstance(data, list):
        return make_error_response("Request body must be an array", 400)

    if len(data) == 0:
        return make_error_response("At least one dependency required", 400)

    if len(data) > 100:
        return make_error_response("Maximum 100 dependencies per bulk request", 400)

    # Validate all dependencies
    from apps.api.models.dependency import DependencyType
    schema = DependencyCreateSchema()
    dependencies = []

    for i, dep_data in enumerate(data):
        try:
            validated = schema.load(dep_data)
            validated["dependency_type"] = DependencyType(validated["dependency_type"])
            dependencies.append(Dependency(**validated))
        except ValidationError as e:
            return make_error_response(
                f"Validation error at index {i}",
                400,
                validation_errors=e.messages,
            )

    # Create all dependencies
    try:
        db.session.add_all(dependencies)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    result_schema = DependencySchema(many=True)
    return jsonify(result_schema.dump(dependencies)), 201


@bp.route("/bulk", methods=["DELETE"])
def delete_bulk_dependencies():
    """
    Delete multiple dependencies at once.

    Request Body:
        JSON object with 'ids' array

    Returns:
        200: Number of deleted dependencies
        400: Validation error
    """
    data = request.get_json() or {}

    if "ids" not in data or not isinstance(data["ids"], list):
        return make_error_response("Request must include 'ids' array", 400)

    ids = data["ids"]

    if len(ids) == 0:
        return make_error_response("At least one ID required", 400)

    if len(ids) > 100:
        return make_error_response("Maximum 100 dependencies per bulk delete", 400)

    try:
        deleted = Dependency.query.filter(Dependency.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return jsonify({"deleted": deleted, "requested": len(ids)}), 200
