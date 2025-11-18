"""Entity API endpoints using PyDAL with async/await."""

import asyncio
from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, request

from apps.api.auth.decorators import login_required
from apps.api.models.dataclasses import (EntityDTO, PaginatedResponse,
                                         from_pydal_row, from_pydal_rows)
from shared.async_utils import run_in_threadpool

bp = Blueprint("entities", __name__)


@bp.route("", methods=["GET"])
@login_required
async def list_entities():
    """
    List all entities with pagination and filtering.

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 1000)
        - entity_type: Filter by entity type
        - organization_id: Filter by organization ID
        - name: Filter by name (partial match)
        - is_active: Filter by active status

    Returns:
        200: List of entities with pagination metadata
    """
    db = current_app.db

    # Get pagination params
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 1000)

    # Build query
    query = db.entities.id > 0

    # Apply filters
    if request.args.get("entity_type"):
        entity_type = request.args.get("entity_type")
        query &= db.entities.entity_type == entity_type

    if request.args.get("organization_id"):
        organization_id = request.args.get("organization_id", type=int)
        query &= db.entities.organization_id == organization_id

    if request.args.get("name"):
        name = request.args.get("name")
        query &= db.entities.name.ilike(f"%{name}%")

    if request.args.get("is_active") is not None:
        is_active = request.args.get("is_active", "true").lower() == "true"
        query &= db.entities.is_active == is_active

    # Calculate pagination
    offset = (page - 1) * per_page

    # Use asyncio TaskGroup for concurrent queries (Python 3.12)
    async with asyncio.TaskGroup() as tg:
        count_task = tg.create_task(run_in_threadpool(lambda: db(query).count()))
        rows_task = tg.create_task(
            run_in_threadpool(
                lambda: db(query).select(
                    orderby=db.entities.name, limitby=(offset, offset + per_page)
                )
            )
        )

    total = count_task.result()
    rows = rows_task.result()

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert PyDAL rows to DTOs
    items = from_pydal_rows(rows, EntityDTO)

    # Create paginated response
    response = PaginatedResponse(
        items=[asdict(item) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )

    return jsonify(asdict(response)), 200


@bp.route("", methods=["POST"])
async def create_entity():
    """
    Create a new entity.

    Request Body:
        JSON object with entity fields

    Returns:
        201: Created entity
        400: Validation error
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    if not data.get("entity_type"):
        return jsonify({"error": "entity_type is required"}), 400
    if not data.get("organization_id"):
        return jsonify({"error": "organization_id is required"}), 400

    # Create entity in database
    def create_in_db():
        entity_id = db.entities.insert(
            name=data["name"],
            description=data.get("description"),
            entity_type=data["entity_type"],
            organization_id=data["organization_id"],
            parent_id=data.get("parent_id"),
            attributes=data.get("attributes"),
            tags=data.get("tags", []),
            is_active=data.get("is_active", True),
        )
        db.commit()
        return db.entities[entity_id]

    row = await run_in_threadpool(create_in_db)

    # Convert to DTO
    entity_dto = from_pydal_row(row, EntityDTO)

    return jsonify(asdict(entity_dto)), 201


@bp.route("/<int:id>", methods=["GET"])
@login_required
async def get_entity(id: int):
    """
    Get a single entity by ID.

    Path Parameters:
        - id: Entity ID

    Returns:
        200: Entity details
        404: Entity not found
    """
    db = current_app.db

    row = await run_in_threadpool(lambda: db.entities[id])

    if not row:
        return jsonify({"error": "Entity not found"}), 404

    entity_dto = from_pydal_row(row, EntityDTO)
    return jsonify(asdict(entity_dto)), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
async def update_entity(id: int):
    """
    Update an entity (full edit support).

    Path Parameters:
        - id: Entity ID

    Request Body:
        JSON object with fields to update

    Returns:
        200: Updated entity
        400: Validation error
        404: Entity not found
    """
    db = current_app.db

    # Check if entity exists
    existing = await run_in_threadpool(lambda: db.entities[id])
    if not existing:
        return jsonify({"error": "Entity not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Update entity
    def update_in_db():
        update_fields = {}
        if "name" in data:
            update_fields["name"] = data["name"]
        if "description" in data:
            update_fields["description"] = data["description"]
        if "entity_type" in data:
            update_fields["entity_type"] = data["entity_type"]
        if "organization_id" in data:
            update_fields["organization_id"] = data["organization_id"]
        if "parent_id" in data:
            update_fields["parent_id"] = data["parent_id"]
        if "attributes" in data:
            update_fields["attributes"] = data["attributes"]
        if "tags" in data:
            update_fields["tags"] = data["tags"]
        if "is_active" in data:
            update_fields["is_active"] = data["is_active"]

        db(db.entities.id == id).update(**update_fields)
        db.commit()
        return db.entities[id]

    row = await run_in_threadpool(update_in_db)

    entity_dto = from_pydal_row(row, EntityDTO)
    return jsonify(asdict(entity_dto)), 200


@bp.route("/<int:id>", methods=["DELETE"])
async def delete_entity(id: int):
    """
    Delete an entity.

    Path Parameters:
        - id: Entity ID

    Returns:
        204: Entity deleted
        404: Entity not found
        400: Cannot delete entity with dependencies
    """
    db = current_app.db

    # Check if entity exists
    existing = await run_in_threadpool(lambda: db.entities[id])
    if not existing:
        return jsonify({"error": "Entity not found"}), 404

    # Check for dependencies
    def check_and_delete():
        # Check outgoing dependencies (this entity depends on others)
        outgoing_count = db((db.dependencies.source_entity_id == id)).count()
        # Check incoming dependencies (others depend on this entity)
        incoming_count = db((db.dependencies.target_entity_id == id)).count()

        total_deps = outgoing_count + incoming_count
        if total_deps > 0:
            return {
                "error": f"Cannot delete entity with {total_deps} dependencies. Remove dependencies first."
            }, False

        # Delete entity
        del db.entities[id]
        db.commit()
        return None, True

    result, success = await run_in_threadpool(check_and_delete)

    if not success:
        return jsonify(result), 400

    return "", 204


@bp.route("/<int:id>/dependencies", methods=["GET"])
@login_required
async def get_entity_dependencies(id: int):
    """
    Get all dependencies for an entity.

    Path Parameters:
        - id: Entity ID

    Query Parameters:
        - direction: 'outgoing' (depends on), 'incoming' (depended by), or 'all' (default)

    Returns:
        200: Dependencies information
        404: Entity not found
    """
    db = current_app.db

    # Check if entity exists
    entity = await run_in_threadpool(lambda: db.entities[id])
    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    direction = request.args.get("direction", "all")

    def get_dependencies():
        result = {
            "entity_id": entity.id,
            "entity_name": entity.name,
        }

        if direction in ("outgoing", "all"):
            # Entities this entity depends on
            outgoing = db(db.dependencies.source_entity_id == id).select()
            result["depends_on"] = [
                {
                    "id": dep.id,
                    "target_entity_id": dep.target_entity_id,
                    "dependency_type": dep.dependency_type,
                    "metadata": dep.metadata,
                }
                for dep in outgoing
            ]

        if direction in ("incoming", "all"):
            # Entities that depend on this entity
            incoming = db(db.dependencies.target_entity_id == id).select()
            result["depended_by"] = [
                {
                    "id": dep.id,
                    "source_entity_id": dep.source_entity_id,
                    "dependency_type": dep.dependency_type,
                    "metadata": dep.metadata,
                }
                for dep in incoming
            ]

        return result

    result = await run_in_threadpool(get_dependencies)
    return jsonify(result), 200


@bp.route("/<int:id>/attributes", methods=["PATCH"])
async def update_entity_attributes(id: int):
    """
    Update entity attributes (JSON field for type-specific fields).

    Path Parameters:
        - id: Entity ID

    Request Body:
        JSON object with attribute fields to update

    Returns:
        200: Updated entity
        404: Entity not found
    """
    db = current_app.db

    # Check if entity exists
    existing = await run_in_threadpool(lambda: db.entities[id])
    if not existing:
        return jsonify({"error": "Entity not found"}), 404

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Attributes must be a JSON object"}), 400

    # Update attributes
    def update_attributes():
        current_attrs = existing.attributes or {}
        current_attrs.update(data)

        db(db.entities.id == id).update(attributes=current_attrs)
        db.commit()
        return db.entities[id]

    row = await run_in_threadpool(update_attributes)

    entity_dto = from_pydal_row(row, EntityDTO)
    return jsonify(asdict(entity_dto)), 200
