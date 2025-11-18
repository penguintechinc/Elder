"""Dependency API endpoints using PyDAL with async/await."""

import asyncio
from flask import Blueprint, request, jsonify, current_app
from dataclasses import asdict

from apps.api.models.dataclasses import (
    DependencyDTO,
    PaginatedResponse,
    from_pydal_row,
    from_pydal_rows,
)
from apps.api.auth.decorators import login_required
from shared.async_utils import run_in_threadpool

bp = Blueprint("dependencies", __name__)


@bp.route("", methods=["GET"])
@login_required
async def list_dependencies():
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
    db = current_app.db

    # Get pagination params
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 1000)

    # Build query
    query = db.dependencies.id > 0

    # Apply filters
    if request.args.get("source_entity_id"):
        source_id = request.args.get("source_entity_id", type=int)
        query &= (db.dependencies.source_entity_id == source_id)

    if request.args.get("target_entity_id"):
        target_id = request.args.get("target_entity_id", type=int)
        query &= (db.dependencies.target_entity_id == target_id)

    if request.args.get("dependency_type"):
        dep_type = request.args.get("dependency_type")
        query &= (db.dependencies.dependency_type == dep_type)

    # Calculate pagination
    offset = (page - 1) * per_page

    # Use asyncio TaskGroup for concurrent queries (Python 3.12)
    async with asyncio.TaskGroup() as tg:
        count_task = tg.create_task(
            run_in_threadpool(lambda: db(query).count())
        )
        rows_task = tg.create_task(
            run_in_threadpool(lambda: db(query).select(
                orderby=~db.dependencies.created_at,
                limitby=(offset, offset + per_page)
            ))
        )

    total = count_task.result()
    rows = rows_task.result()

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert PyDAL rows to DTOs
    items = from_pydal_rows(rows, DependencyDTO)

    # Create paginated response
    response = PaginatedResponse(
        items=[asdict(item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )

    return jsonify(asdict(response)), 200


@bp.route("", methods=["POST"])
async def create_dependency():
    """
    Create a new dependency relationship.

    Request Body:
        JSON object with dependency fields

    Returns:
        201: Created dependency
        400: Validation error or invalid entity IDs
        409: Dependency already exists
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("source_entity_id"):
        return jsonify({"error": "source_entity_id is required"}), 400
    if not data.get("target_entity_id"):
        return jsonify({"error": "target_entity_id is required"}), 400
    if not data.get("dependency_type"):
        return jsonify({"error": "dependency_type is required"}), 400

    source_id = data["source_entity_id"]
    target_id = data["target_entity_id"]

    # Prevent self-dependencies
    if source_id == target_id:
        return jsonify({"error": "Cannot create dependency from entity to itself"}), 400

    # Check if entities exist and dependency doesn't already exist
    def validate_and_create():
        # Check if source entity exists
        source = db.entities[source_id]
        if not source:
            return {"error": f"Source entity {source_id} not found"}, 400, None

        # Check if target entity exists
        target = db.entities[target_id]
        if not target:
            return {"error": f"Target entity {target_id} not found"}, 400, None

        # Check if dependency already exists
        existing = db(
            (db.dependencies.source_entity_id == source_id) &
            (db.dependencies.target_entity_id == target_id) &
            (db.dependencies.dependency_type == data["dependency_type"])
        ).select().first()

        if existing:
            return {"error": "Dependency already exists", "dependency_id": existing.id}, 409, None

        # Create dependency
        dep_id = db.dependencies.insert(
            source_entity_id=source_id,
            target_entity_id=target_id,
            dependency_type=data["dependency_type"],
            metadata=data.get("metadata"),
        )
        db.commit()
        return None, None, db.dependencies[dep_id]

    error, status, row = await run_in_threadpool(validate_and_create)

    if error:
        return jsonify(error), status

    dependency_dto = from_pydal_row(row, DependencyDTO)
    return jsonify(asdict(dependency_dto)), 201


@bp.route("/<int:id>", methods=["GET"])
@login_required
async def get_dependency(id: int):
    """
    Get a single dependency by ID.

    Path Parameters:
        - id: Dependency ID

    Returns:
        200: Dependency details
        404: Dependency not found
    """
    db = current_app.db

    row = await run_in_threadpool(lambda: db.dependencies[id])

    if not row:
        return jsonify({"error": "Dependency not found"}), 404

    dependency_dto = from_pydal_row(row, DependencyDTO)
    return jsonify(asdict(dependency_dto)), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
async def update_dependency(id: int):
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
    db = current_app.db

    # Check if dependency exists
    existing = await run_in_threadpool(lambda: db.dependencies[id])
    if not existing:
        return jsonify({"error": "Dependency not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Update dependency
    def update_in_db():
        update_fields = {}
        if "dependency_type" in data:
            update_fields["dependency_type"] = data["dependency_type"]
        if "metadata" in data:
            update_fields["metadata"] = data["metadata"]

        db(db.dependencies.id == id).update(**update_fields)
        db.commit()
        return db.dependencies[id]

    row = await run_in_threadpool(update_in_db)

    dependency_dto = from_pydal_row(row, DependencyDTO)
    return jsonify(asdict(dependency_dto)), 200


@bp.route("/<int:id>", methods=["DELETE"])
async def delete_dependency(id: int):
    """
    Delete a dependency relationship.

    Path Parameters:
        - id: Dependency ID

    Returns:
        204: Dependency deleted
        404: Dependency not found
    """
    db = current_app.db

    # Check if dependency exists
    existing = await run_in_threadpool(lambda: db.dependencies[id])
    if not existing:
        return jsonify({"error": "Dependency not found"}), 404

    # Delete dependency
    await run_in_threadpool(lambda: (
        db(db.dependencies.id == id).delete(),
        db.commit()
    ))

    return "", 204


@bp.route("/bulk", methods=["POST"])
async def create_bulk_dependencies():
    """
    Create multiple dependencies at once.

    Request Body:
        JSON array of dependency objects

    Returns:
        201: Created dependencies
        400: Validation error
    """
    db = current_app.db

    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be an array"}), 400

    if len(data) == 0:
        return jsonify({"error": "At least one dependency required"}), 400

    if len(data) > 100:
        return jsonify({"error": "Maximum 100 dependencies per bulk request"}), 400

    # Validate and create dependencies
    def create_all():
        created_ids = []
        for i, dep_data in enumerate(data):
            # Validate required fields
            if not dep_data.get("source_entity_id"):
                raise ValueError(f"source_entity_id required at index {i}")
            if not dep_data.get("target_entity_id"):
                raise ValueError(f"target_entity_id required at index {i}")
            if not dep_data.get("dependency_type"):
                raise ValueError(f"dependency_type required at index {i}")

            # Create dependency
            dep_id = db.dependencies.insert(
                source_entity_id=dep_data["source_entity_id"],
                target_entity_id=dep_data["target_entity_id"],
                dependency_type=dep_data["dependency_type"],
                metadata=dep_data.get("metadata"),
            )
            created_ids.append(dep_id)

        db.commit()

        # Fetch created dependencies
        return db(db.dependencies.id.belongs(created_ids)).select()

    try:
        rows = await run_in_threadpool(create_all)
        dependencies = from_pydal_rows(rows, DependencyDTO)
        return jsonify([asdict(d) for d in dependencies]), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@bp.route("/bulk", methods=["DELETE"])
async def delete_bulk_dependencies():
    """
    Delete multiple dependencies at once.

    Request Body:
        JSON object with 'ids' array

    Returns:
        200: Number of deleted dependencies
        400: Validation error
    """
    db = current_app.db

    data = request.get_json()
    if not data or "ids" not in data or not isinstance(data["ids"], list):
        return jsonify({"error": "Request must include 'ids' array"}), 400

    ids = data["ids"]

    if len(ids) == 0:
        return jsonify({"error": "At least one ID required"}), 400

    if len(ids) > 100:
        return jsonify({"error": "Maximum 100 dependencies per bulk delete"}), 400

    # Delete dependencies
    def delete_all():
        deleted = db(db.dependencies.id.belongs(ids)).delete()
        db.commit()
        return deleted

    deleted = await run_in_threadpool(delete_all)

    return jsonify({"deleted": deleted, "requested": len(ids)}), 200
