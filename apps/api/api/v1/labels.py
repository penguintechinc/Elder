"""Labels management API endpoints for Elder using PyDAL with async/await."""

import asyncio
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timezone
from dataclasses import asdict

from apps.api.auth.decorators import login_required
from apps.api.models.dataclasses import (
    IssueLabelDTO,
    CreateLabelRequest,
    UpdateLabelRequest,
    PaginatedResponse,
    from_pydal_row,
    from_pydal_rows,
)
from shared.async_utils import run_in_threadpool

bp = Blueprint("labels", __name__)


@bp.route("", methods=["GET"])
@login_required
async def list_labels():
    """
    List all labels with optional filtering.

    Query Parameters:
        - search: Search in name and description
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)

    Returns:
        200: List of labels with pagination
        400: Invalid parameters

    Example:
        GET /api/v1/labels?search=bug
    """
    db = current_app.db

    # Get pagination params
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 1000)

    # Build query
    def get_labels():
        query = db.issue_labels.id > 0

        # Apply search filter
        if request.args.get("search"):
            search = request.args.get("search")
            search_pattern = f'%{search}%'
            query &= (
                (db.issue_labels.name.like(search_pattern, case_sensitive=False)) |
                (db.issue_labels.description.like(search_pattern, case_sensitive=False))
            )

        # Calculate pagination
        offset = (page - 1) * per_page

        # Get count and rows
        total = db(query).count()
        rows = db(query).select(
            orderby=db.issue_labels.name,
            limitby=(offset, offset + per_page)
        )

        return total, rows

    total, rows = await run_in_threadpool(get_labels)

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert to DTOs
    items = from_pydal_rows(rows, IssueLabelDTO)

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
@login_required
async def create_label():
    """
    Create a new label.

    Request Body:
        {
            "name": "bug",
            "description": "Something isn't working",
            "color": "#d73a4a"
        }

    Returns:
        201: Label created
        400: Invalid request
        409: Label with this name already exists

    Example:
        POST /api/v1/labels
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    def create():
        # Check if label already exists
        existing = db(db.issue_labels.name == data["name"]).select().first()
        if existing:
            return None

        # Create label
        label_id = db.issue_labels.insert(
            name=data["name"],
            description=data.get("description"),
            color=data.get("color", "#cccccc"),
        )
        db.commit()

        return db.issue_labels[label_id]

    label = await run_in_threadpool(create)

    if not label:
        return jsonify({"error": "Label with this name already exists"}), 409

    label_dto = from_pydal_row(label, IssueLabelDTO)
    return jsonify(asdict(label_dto)), 201


@bp.route("/<int:id>", methods=["GET"])
@login_required
async def get_label(id: int):
    """
    Get a single label by ID.

    Path Parameters:
        - id: Label ID

    Returns:
        200: Label details
        404: Label not found

    Example:
        GET /api/v1/labels/1
    """
    db = current_app.db

    label = await run_in_threadpool(lambda: db.issue_labels[id])

    if not label:
        return jsonify({"error": "Label not found"}), 404

    label_dto = from_pydal_row(label, IssueLabelDTO)
    return jsonify(asdict(label_dto)), 200


@bp.route("/<int:id>", methods=["PUT"])
@login_required
async def update_label(id: int):
    """
    Update a label.

    Path Parameters:
        - id: Label ID

    Request Body:
        {
            "name": "critical-bug",
            "color": "#ff0000"
        }

    Returns:
        200: Label updated
        400: Invalid request
        404: Label not found
        409: Label with this name already exists

    Example:
        PUT /api/v1/labels/1
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    def update():
        label = db.issue_labels[id]
        if not label:
            return None, False

        # Check if name is being changed to an existing one
        if "name" in data and data["name"] != label.name:
            existing = db(db.issue_labels.name == data["name"]).select().first()
            if existing:
                return None, True

        # Update fields
        update_dict = {}
        if "name" in data:
            update_dict["name"] = data["name"]
        if "description" in data:
            update_dict["description"] = data["description"]
        if "color" in data:
            update_dict["color"] = data["color"]

        if update_dict:
            db(db.issue_labels.id == id).update(**update_dict)
            db.commit()

        return db.issue_labels[id], False

    label, name_exists = await run_in_threadpool(update)

    if label is None and name_exists:
        return jsonify({"error": "Label with this name already exists"}), 409
    if label is None:
        return jsonify({"error": "Label not found"}), 404

    label_dto = from_pydal_row(label, IssueLabelDTO)
    return jsonify(asdict(label_dto)), 200


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
async def delete_label(id: int):
    """
    Delete a label.

    Path Parameters:
        - id: Label ID

    Returns:
        204: Label deleted
        404: Label not found

    Example:
        DELETE /api/v1/labels/1
    """
    db = current_app.db

    def delete():
        label = db.issue_labels[id]
        if not label:
            return False

        del db.issue_labels[id]
        db.commit()
        return True

    success = await run_in_threadpool(delete)

    if not success:
        return jsonify({"error": "Label not found"}), 404

    return "", 204
