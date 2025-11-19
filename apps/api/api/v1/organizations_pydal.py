"""Organization Units (OUs) API endpoints using PyDAL with async/await."""

import logging
from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, request

from apps.api.auth.decorators import login_required
from apps.api.logging_config import log_error_and_respond
from apps.api.models.dataclasses import (CreateOrganizationRequest,
                                         OrganizationDTO, PaginatedResponse,
                                         from_pydal_row, from_pydal_rows)
from shared.async_utils import run_in_threadpool

logger = logging.getLogger(__name__)

bp = Blueprint("organizations", __name__)


@bp.route("", methods=["GET"])
@login_required
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
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 1000)

    # Build query
    query = db.organizations.id > 0

    # Apply filters
    if request.args.get("parent_id"):
        parent_id = request.args.get("parent_id", type=int)
        query &= db.organizations.parent_id == parent_id

    # Support both 'name' and 'search' parameters for name filtering
    search_term = request.args.get("name") or request.args.get("search")
    if search_term:
        # Case-insensitive search using PostgreSQL ILIKE
        query &= db.organizations.name.ilike(f"%{search_term}%")

    # Calculate pagination
    offset = (page - 1) * per_page

    # Execute database queries in a single thread pool task to avoid cursor issues
    def get_orgs():
        total = db(query).count()
        rows = db(query).select(
            orderby=db.organizations.name, limitby=(offset, offset + per_page)
        )
        return total, rows

    total, rows = await run_in_threadpool(get_orgs)

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
        pages=pages,
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
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400

    # Create request DTO
    create_req = CreateOrganizationRequest(
        name=data.get("name"),
        description=data.get("description"),
        organization_type=data.get("organization_type", "organization"),
        parent_id=data.get("parent_id"),
        ldap_dn=data.get("ldap_dn"),
        saml_group=data.get("saml_group"),
        owner_identity_id=data.get("owner_identity_id"),
        owner_group_id=data.get("owner_group_id"),
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
        return log_error_and_respond(
            logger, e, "Failed to process request", 500
        )


@bp.route("/<int:id>", methods=["GET"])
@login_required
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
        return jsonify({"error": "Organization Unit not found"}), 404

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
        return jsonify({"error": "Organization Unit not found"}), 404

    data = request.get_json() or {}

    # Build update DTO with only provided fields
    update_fields = {}
    for field in [
        "name",
        "description",
        "organization_type",
        "parent_id",
        "ldap_dn",
        "saml_group",
        "owner_identity_id",
        "owner_group_id",
    ]:
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
            return log_error_and_respond(
            logger, e, "Failed to process request", 500
        )

    return jsonify({"error": "No fields to update"}), 400


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
        return jsonify({"error": "Organization Unit not found"}), 404

    # Check if OU has children (concurrent check in TaskGroup)
    children_count = await run_in_threadpool(
        lambda: db(db.organizations.parent_id == id).count()
    )

    if children_count > 0:
        return jsonify({"error": "Cannot delete Organization Unit with child OUs"}), 400

    try:
        await run_in_threadpool(lambda: db.organizations.__delitem__(id))
        await run_in_threadpool(lambda: db.commit())
        return "", 204

    except Exception as e:
        await run_in_threadpool(lambda: db.rollback())
        return log_error_and_respond(
            logger, e, "Failed to process request", 500
        )


@bp.route("/<int:id>/graph", methods=["GET"])
@login_required
async def get_organization_graph(id: int):
    """
    Get relationship graph for an organization and its nearby entities.

    Path Parameters:
        - id: Organization ID

    Query Parameters:
        - depth: How many hops away to include (default: 3, max: 10)

    Returns:
        200: Graph data with nodes and edges
        404: Organization not found
    """
    db = current_app.db

    # Check if organization exists
    try:
        org_row = await run_in_threadpool(lambda: db.organizations[id])
        if org_row is None:
            return jsonify({"error": "Organization Unit not found"}), 404
    except Exception:
        return jsonify({"error": "Organization Unit not found"}), 404

    # Get depth parameter
    depth = min(request.args.get("depth", 3, type=int), 10)

    # Build graph data
    nodes = []
    edges = []
    visited_orgs = set()
    visited_entities = set()

    # Helper to add organization node
    def add_org_node(org_id):
        if org_id in visited_orgs:
            return
        org = db.organizations[org_id]
        if not org:
            return
        visited_orgs.add(org_id)
        nodes.append(
            {
                "id": f"org-{org_id}",
                "label": org.name,
                "type": "organization",
                "metadata": {
                    "id": org_id,
                    "description": org.description,
                    "parent_id": org.parent_id,
                },
            }
        )
        return org

    # Helper to add entity node
    def add_entity_node(entity_id):
        if entity_id in visited_entities:
            return
        entity = db.entities[entity_id]
        if not entity:
            return
        visited_entities.add(entity_id)
        nodes.append(
            {
                "id": f"entity-{entity_id}",
                "label": entity.name,
                "type": entity.entity_type or "default",
                "metadata": {
                    "id": entity_id,
                    "entity_type": entity.entity_type,
                    "organization_id": entity.organization_id,
                },
            }
        )

    # Add current organization
    add_org_node(id)

    # Get all child organizations recursively (limit to depth * 10)
    def get_children_recursive(parent_id, current_depth=0):
        if current_depth >= depth:
            return []
        children = db(db.organizations.parent_id == parent_id).select()
        all_children = list(children)
        for child in children:
            all_children.extend(get_children_recursive(child.id, current_depth + 1))
        return all_children[: depth * 10]

    all_children = await run_in_threadpool(lambda: get_children_recursive(id))
    for child in all_children:
        add_org_node(child.id)
        if child.parent_id:
            edges.append(
                {
                    "from": f"org-{child.parent_id}",
                    "to": f"org-{child.id}",
                    "label": "parent",
                }
            )

    # Get parent hierarchy up to depth
    current_org = org_row
    for _ in range(depth):
        if current_org and current_org.parent_id:
            parent = db.organizations[current_org.parent_id]
            if parent:
                add_org_node(parent.id)
                edges.append(
                    {
                        "from": f"org-{parent.id}",
                        "to": f"org-{current_org.id}",
                        "label": "parent",
                    }
                )
                current_org = parent
            else:
                break
        else:
            break

    # Get entities for all visited organizations
    org_ids = list(visited_orgs)
    entities = await run_in_threadpool(
        lambda: db(db.entities.organization_id.belongs(org_ids)).select(
            limitby=(0, 100)
        )
    )

    for entity in entities:
        add_entity_node(entity.id)
        edges.append(
            {
                "from": f"org-{entity.organization_id}",
                "to": f"entity-{entity.id}",
                "label": "contains",
            }
        )

    # Get dependencies between entities
    entity_ids = list(visited_entities)
    dependencies = await run_in_threadpool(
        lambda: db(
            (db.dependencies.source_entity_id.belongs(entity_ids))
            & (db.dependencies.target_entity_id.belongs(entity_ids))
        ).select()
    )

    for dep in dependencies:
        edges.append(
            {
                "from": f"entity-{dep.source_entity_id}",
                "to": f"entity-{dep.target_entity_id}",
                "label": dep.dependency_type or "depends",
            }
        )

    return (
        jsonify(
            {
                "nodes": nodes,
                "edges": edges,
                "center_node": f"org-{id}",
                "depth": depth,
            }
        ),
        200,
    )
