"""Organization API endpoints."""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from apps.api.models import Organization
from apps.api.schemas.organization import (
    OrganizationSchema,
    OrganizationCreateSchema,
    OrganizationUpdateSchema,
    OrganizationListSchema,
)
from shared.database import db
from shared.api_utils import (
    paginate,
    get_pagination_params,
    validate_request,
    make_error_response,
    make_success_response,
    apply_filters,
    get_or_404,
    handle_validation_error,
)

bp = Blueprint("organizations", __name__)


@bp.route("", methods=["GET"])
def list_organizations():
    """
    List all organizations with pagination and filtering.

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 1000)
        - parent_id: Filter by parent organization ID
        - name: Filter by name (partial match)

    Returns:
        200: List of organizations with pagination metadata
    """
    # Get pagination params
    pagination_params = get_pagination_params()

    # Build base query (disable relationship loading to avoid serialization issues)
    from sqlalchemy.orm import lazyload
    query = db.session.query(Organization).options(
        lazyload(Organization.parent),
        lazyload(Organization.children),
        lazyload(Organization.owner),
        lazyload(Organization.owner_group),
        lazyload(Organization.entities)
    )

    # Apply filters
    filters = {}
    if request.args.get("parent_id"):
        filters["parent_id"] = request.args.get("parent_id", type=int)
    if request.args.get("name"):
        filters["name"] = request.args.get("name")

    query = apply_filters(query, Organization, filters)

    # Order by name
    query = query.order_by(Organization.name)

    # Paginate
    items, pagination = paginate(
        query,
        page=pagination_params["page"],
        per_page=pagination_params["per_page"],
    )

    # Serialize (exclude nested relationships to avoid serialization issues)
    schema = OrganizationSchema(many=True, exclude=("parent", "children"))
    list_schema = OrganizationListSchema()

    result = list_schema.dump({
        "items": schema.dump(items),
        **pagination,
    })

    return jsonify(result), 200


@bp.route("", methods=["POST"])
def create_organization():
    """
    Create a new organization.

    Request Body:
        JSON object with organization fields (see OrganizationCreateSchema)

    Returns:
        201: Created organization
        400: Validation error
    """
    try:
        data = validate_request(OrganizationCreateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Create organization
    org = Organization(**data)
    db.session.add(org)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    schema = OrganizationSchema()
    return jsonify(schema.dump(org)), 201


@bp.route("/<int:id>", methods=["GET"])
def get_organization(id: int):
    """
    Get a single organization by ID.

    Path Parameters:
        - id: Organization ID

    Returns:
        200: Organization details
        404: Organization not found
    """
    org = get_or_404(Organization, id)

    schema = OrganizationSchema()
    return jsonify(schema.dump(org)), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
def update_organization(id: int):
    """
    Update an organization.

    Path Parameters:
        - id: Organization ID

    Request Body:
        JSON object with fields to update (see OrganizationUpdateSchema)

    Returns:
        200: Updated organization
        400: Validation error
        404: Organization not found
    """
    org = get_or_404(Organization, id)

    try:
        data = validate_request(OrganizationUpdateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Update fields
    for key, value in data.items():
        setattr(org, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    # Serialize and return
    schema = OrganizationSchema()
    return jsonify(schema.dump(org)), 200


@bp.route("/<int:id>", methods=["DELETE"])
def delete_organization(id: int):
    """
    Delete an organization.

    Path Parameters:
        - id: Organization ID

    Returns:
        204: Organization deleted
        404: Organization not found
        400: Cannot delete organization with children
    """
    org = get_or_404(Organization, id)

    # Check if organization has children
    if org.children:
        return make_error_response(
            "Cannot delete organization with child organizations",
            400,
        )

    try:
        db.session.delete(org)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return "", 204


@bp.route("/<int:id>/children", methods=["GET"])
def get_organization_children(id: int):
    """
    Get all child organizations.

    Path Parameters:
        - id: Organization ID

    Query Parameters:
        - recursive: Include all descendants (default: false)

    Returns:
        200: List of child organizations
        404: Organization not found
    """
    org = get_or_404(Organization, id)

    # Get children
    recursive = request.args.get("recursive", "false").lower() == "true"
    if recursive:
        children = org.get_all_children(recursive=True)
    else:
        children = list(org.children)

    # Serialize
    schema = OrganizationSchema(many=True)
    return jsonify(schema.dump(children)), 200


@bp.route("/<int:id>/hierarchy", methods=["GET"])
def get_organization_hierarchy(id: int):
    """
    Get organization hierarchy path from root to this organization.

    Path Parameters:
        - id: Organization ID

    Returns:
        200: List of organizations in hierarchy path
        404: Organization not found
    """
    org = get_or_404(Organization, id)

    # Get hierarchy path
    path = org.get_hierarchy_path()

    # Serialize
    schema = OrganizationSchema(many=True)
    return jsonify({
        "path": schema.dump(path),
        "depth": org.depth,
        "hierarchy_string": org.get_hierarchy_string(),
    }), 200


@bp.route("/<int:id>/graph", methods=["GET"])
def get_organization_graph(id: int):
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
    from apps.api.models import Entity, Dependency

    org = get_or_404(Organization, id)

    # Get depth parameter
    depth = min(request.args.get("depth", 3, type=int), 10)

    # Build graph data
    nodes = []
    edges = []
    visited_orgs = set()
    visited_entities = set()

    # Helper function to add organization node
    def add_org_node(organization):
        if organization.id in visited_orgs:
            return
        visited_orgs.add(organization.id)
        nodes.append({
            "id": f"org-{organization.id}",
            "label": organization.name,
            "type": "organization",
            "metadata": {
                "id": organization.id,
                "description": organization.description,
                "parent_id": organization.parent_id,
            }
        })

    # Helper function to add entity node
    def add_entity_node(entity):
        if entity.id in visited_entities:
            return
        visited_entities.add(entity.id)
        nodes.append({
            "id": f"entity-{entity.id}",
            "label": entity.name,
            "type": entity.entity_type or "default",
            "metadata": {
                "id": entity.id,
                "entity_type": entity.entity_type,
                "organization_id": entity.organization_id,
            }
        })

    # Add current organization
    add_org_node(org)

    # Get all child organizations recursively
    all_children = org.get_all_children(recursive=True)
    for child in all_children[:depth * 10]:  # Limit total orgs
        add_org_node(child)
        # Add edge from parent to child
        if child.parent_id:
            edges.append({
                "from": f"org-{child.parent_id}",
                "to": f"org-{child.id}",
                "label": "parent"
            })

    # Get parent hierarchy up to depth
    current = org
    for _ in range(depth):
        if current.parent:
            add_org_node(current.parent)
            edges.append({
                "from": f"org-{current.parent.id}",
                "to": f"org-{current.id}",
                "label": "parent"
            })
            current = current.parent
        else:
            break

    # Get entities for all visited organizations
    org_ids = list(visited_orgs)
    entities = db.session.query(Entity).filter(
        Entity.organization_id.in_(org_ids)
    ).limit(100).all()  # Limit entities

    for entity in entities:
        add_entity_node(entity)
        # Add edge from organization to entity
        edges.append({
            "from": f"org-{entity.organization_id}",
            "to": f"entity-{entity.id}",
            "label": "contains"
        })

    # Get dependencies between entities
    entity_ids = list(visited_entities)
    dependencies = db.session.query(Dependency).filter(
        Dependency.source_entity_id.in_(entity_ids),
        Dependency.target_entity_id.in_(entity_ids)
    ).all()

    for dep in dependencies:
        edges.append({
            "from": f"entity-{dep.source_entity_id}",
            "to": f"entity-{dep.target_entity_id}",
            "label": dep.dependency_type or "depends"
        })

    return jsonify({
        "nodes": nodes,
        "edges": edges,
        "center_node": f"org-{org.id}",
        "depth": depth,
    }), 200
