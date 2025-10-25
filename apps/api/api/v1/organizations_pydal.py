"""Organization Units (OUs) API endpoints using PyDAL with async/await."""

import asyncio
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
from dataclasses import asdict

from apps.api.models.dataclasses import (
    OrganizationDTO,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    PaginatedResponse,
    from_pydal_row,
    from_pydal_rows,
)
from shared.async_utils import run_in_threadpool

bp = Blueprint("organizations", __name__)


@bp.route("", methods=["GET"])
async def list_organizations():
    """
    List all Organization Units (OUs) with pagination and filtering.

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 1000)
        - parent_id: Filter by parent OU ID
        - name: Filter by name (partial match)

    Returns:
        200: List of Organization Units with pagination metadata
    """
    db = current_app.db

    # Get pagination params
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 1000)

    # Build query
    query = db.organizations.id > 0

    # Apply filters
    if request.args.get("parent_id"):
        parent_id = request.args.get("parent_id", type=int)
        query &= (db.organizations.parent_id == parent_id)

    if request.args.get("name"):
        name = request.args.get("name")
        query &= (db.organizations.name.contains(name))

    # Calculate pagination
    offset = (page - 1) * per_page

    # Use asyncio TaskGroup for concurrent queries (Python 3.12)
    async with asyncio.TaskGroup() as tg:
        count_task = tg.create_task(
            run_in_threadpool(lambda: db(query).count())
        )
        rows_task = tg.create_task(
            run_in_threadpool(lambda: db(query).select(
                orderby=db.organizations.name,
                limitby=(offset, offset + per_page)
            ))
        )

    total = count_task.result()
    rows = rows_task.result()

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert PyDAL rows to DTOs
    items = from_pydal_rows(rows, OrganizationDTO)

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
async def create_organization():
    """
    Create a new Organization Unit (OU).

    Request Body:
        JSON object with Organization Unit fields

    Returns:
        201: Created Organization Unit
        400: Validation error
    """
    db = current_app.db
    data = request.get_json() or {}

    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    # Create request DTO
    create_req = CreateOrganizationRequest(
        name=data.get('name'),
        description=data.get('description'),
        parent_id=data.get('parent_id'),
        ldap_dn=data.get('ldap_dn'),
        saml_group=data.get('saml_group'),
        owner_identity_id=data.get('owner_identity_id'),
        owner_group_id=data.get('owner_group_id'),
    )

    # Insert organization in thread pool
    try:
        org_id = await run_in_threadpool(
            lambda: db.organizations.insert(**asdict(create_req))
        )
        await run_in_threadpool(lambda: db.commit())

        # Fetch created org
        org_row = await run_in_threadpool(lambda: db.organizations[org_id])
        org_dto = from_pydal_row(org_row, OrganizationDTO)

        return jsonify(asdict(org_dto)), 201

    except Exception as e:
        await run_in_threadpool(lambda: db.rollback())
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@bp.route("/<int:id>", methods=["GET"])
async def get_organization(id: int):
    """
    Get a single Organization Unit (OU) by ID.

    Path Parameters:
        - id: Organization Unit ID

    Returns:
        200: Organization Unit details
        404: Organization Unit not found
    """
    db = current_app.db

    org_row = await run_in_threadpool(lambda: db.organizations[id])
    if not org_row:
        return jsonify({'error': 'Organization Unit not found'}), 404

    org_dto = from_pydal_row(org_row, OrganizationDTO)
    return jsonify(asdict(org_dto)), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
async def update_organization(id: int):
    """
    Update an Organization Unit (OU).

    Path Parameters:
        - id: Organization Unit ID

    Request Body:
        JSON object with fields to update

    Returns:
        200: Updated Organization Unit
        404: Organization Unit not found
    """
    db = current_app.db

    org_row = await run_in_threadpool(lambda: db.organizations[id])
    if not org_row:
        return jsonify({'error': 'Organization Unit not found'}), 404

    data = request.get_json() or {}

    # Build update DTO with only provided fields
    update_fields = {}
    for field in ['name', 'description', 'parent_id', 'ldap_dn', 'saml_group', 'owner_identity_id', 'owner_group_id']:
        if field in data:
            update_fields[field] = data[field]

    if update_fields:
        try:
            await run_in_threadpool(
                lambda: db(db.organizations.id == id).update(**update_fields)
            )
            await run_in_threadpool(lambda: db.commit())

            # Fetch updated org
            org_row = await run_in_threadpool(lambda: db.organizations[id])
            org_dto = from_pydal_row(org_row, OrganizationDTO)
            return jsonify(asdict(org_dto)), 200

        except Exception as e:
            await run_in_threadpool(lambda: db.rollback())
            return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'error': 'No fields to update'}), 400


@bp.route("/<int:id>", methods=["DELETE"])
async def delete_organization(id: int):
    """
    Delete an Organization Unit (OU).

    Path Parameters:
        - id: Organization Unit ID

    Returns:
        204: Organization Unit deleted
        404: Organization Unit not found
        400: Cannot delete OU with child OUs
    """
    db = current_app.db

    org_row = await run_in_threadpool(lambda: db.organizations[id])
    if not org_row:
        return jsonify({'error': 'Organization Unit not found'}), 404

    # Check if OU has children (concurrent check in TaskGroup)
    children_count = await run_in_threadpool(
        lambda: db(db.organizations.parent_id == id).count()
    )

    if children_count > 0:
        return jsonify({'error': 'Cannot delete Organization Unit with child OUs'}), 400

    try:
        await run_in_threadpool(lambda: db.organizations.__delitem__(id))
        await run_in_threadpool(lambda: db.commit())
        return '', 204

    except Exception as e:
        await run_in_threadpool(lambda: db.rollback())
        return jsonify({'error': f'Database error: {str(e)}'}), 500
