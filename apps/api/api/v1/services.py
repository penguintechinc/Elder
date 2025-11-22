"""Services management API endpoints for Elder using PyDAL with async/await."""

from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, request

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.dataclasses import (
    PaginatedResponse,
    ServiceDTO,
    from_pydal_row,
    from_pydal_rows,
)
from shared.async_utils import run_in_threadpool

bp = Blueprint("services", __name__)


@bp.route("", methods=["GET"])
@login_required
async def list_services():
    """
    List services with optional filtering.

    Query Parameters:
        - organization_id: Filter by organization
        - language: Filter by language (rust, go, python, nodejs, etc.)
        - deployment_method: Filter by deployment method
        - status: Filter by status (active/deprecated/maintenance/inactive)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)
        - search: Search in name and description

    Returns:
        200: List of services with pagination
        400: Invalid parameters

    Example:
        GET /api/v1/services?organization_id=1&status=active
    """
    db = current_app.db

    # Get pagination params
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 1000)

    # Build query
    def get_services():
        query = db.services.id > 0

        # Apply filters
        if request.args.get("organization_id"):
            org_id = request.args.get("organization_id", type=int)
            query &= db.services.organization_id == org_id

        if request.args.get("language"):
            query &= db.services.language == request.args.get("language")

        if request.args.get("deployment_method"):
            query &= db.services.deployment_method == request.args.get("deployment_method")

        if request.args.get("status"):
            query &= db.services.status == request.args.get("status")

        if request.args.get("search"):
            search = request.args.get("search")
            search_pattern = f"%{search}%"
            query &= (db.services.name.ilike(search_pattern)) | (
                db.services.description.ilike(search_pattern)
            )

        # Calculate pagination
        offset = (page - 1) * per_page

        # Get count and rows
        total = db(query).count()
        rows = db(query).select(
            orderby=~db.services.created_at, limitby=(offset, offset + per_page)
        )

        return total, rows

    total, rows = await run_in_threadpool(get_services)

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert to DTOs
    items = from_pydal_rows(rows, ServiceDTO)

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
@login_required
@resource_role_required("viewer")
async def create_service():
    """
    Create a new service.

    Requires viewer role on the resource.

    Request Body:
        {
            "name": "User Authentication Service",
            "description": "Handles user authentication and session management",
            "organization_id": 1,
            "domains": ["auth.example.com"],
            "paths": ["/api/auth"],
            "poc_identity_id": 5,
            "language": "go",
            "deployment_method": "kubernetes",
            "deployment_type": "blue-green",
            "is_public": false,
            "port": 8080,
            "health_endpoint": "/healthz",
            "repository_url": "https://github.com/org/auth-service",
            "documentation_url": "https://docs.example.com/auth",
            "sla_uptime": 99.99,
            "sla_response_time_ms": 200,
            "notes": "Critical service",
            "tags": ["auth", "security"],
            "status": "active"
        }

    Returns:
        201: Service created
        400: Invalid request
        403: Insufficient permissions

    Example:
        POST /api/v1/services
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    if not data.get("organization_id"):
        return jsonify({"error": "organization_id is required"}), 400

    # Get organization to derive tenant_id
    def get_org():
        return db.organizations[data["organization_id"]]

    org = await run_in_threadpool(get_org)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    if not org.tenant_id:
        return jsonify({"error": "Organization must have a tenant"}), 400

    # Validate poc_identity_id if provided
    if data.get("poc_identity_id"):
        def get_identity():
            return db.identities[data["poc_identity_id"]]
        identity = await run_in_threadpool(get_identity)
        if not identity:
            return jsonify({"error": "POC identity not found"}), 404

    def create():
        # Create service
        service_id = db.services.insert(
            name=data["name"],
            description=data.get("description"),
            organization_id=data["organization_id"],
            tenant_id=org.tenant_id,
            domains=data.get("domains", []),
            paths=data.get("paths", []),
            poc_identity_id=data.get("poc_identity_id"),
            language=data.get("language"),
            deployment_method=data.get("deployment_method"),
            deployment_type=data.get("deployment_type"),
            is_public=data.get("is_public", False),
            port=data.get("port"),
            health_endpoint=data.get("health_endpoint"),
            repository_url=data.get("repository_url"),
            documentation_url=data.get("documentation_url"),
            sla_uptime=data.get("sla_uptime"),
            sla_response_time_ms=data.get("sla_response_time_ms"),
            notes=data.get("notes"),
            tags=data.get("tags", []),
            status=data.get("status", "active"),
        )
        db.commit()

        return db.services[service_id]

    service = await run_in_threadpool(create)

    service_dto = from_pydal_row(service, ServiceDTO)
    return jsonify(asdict(service_dto)), 201


@bp.route("/<int:id>", methods=["GET"])
@login_required
async def get_service(id: int):
    """
    Get a single service by ID.

    Path Parameters:
        - id: Service ID

    Returns:
        200: Service details
        404: Service not found

    Example:
        GET /api/v1/services/1
    """
    db = current_app.db

    service = await run_in_threadpool(lambda: db.services[id])

    if not service:
        return jsonify({"error": "Service not found"}), 404

    service_dto = from_pydal_row(service, ServiceDTO)
    return jsonify(asdict(service_dto)), 200


@bp.route("/<int:id>", methods=["PUT"])
@login_required
@resource_role_required("maintainer")
async def update_service(id: int):
    """
    Update a service.

    Requires maintainer role.

    Path Parameters:
        - id: Service ID

    Request Body:
        {
            "name": "Updated Service Name",
            "status": "maintenance"
        }

    Returns:
        200: Service updated
        400: Invalid request
        403: Insufficient permissions
        404: Service not found

    Example:
        PUT /api/v1/services/1
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # If organization is being changed, validate and get tenant
    org_tenant_id = None
    if "organization_id" in data:
        def get_org():
            return db.organizations[data["organization_id"]]
        org = await run_in_threadpool(get_org)
        if not org:
            return jsonify({"error": "Organization not found"}), 404
        if not org.tenant_id:
            return jsonify({"error": "Organization must have a tenant"}), 400
        org_tenant_id = org.tenant_id

    # Validate poc_identity_id if provided
    if "poc_identity_id" in data and data["poc_identity_id"]:
        def get_identity():
            return db.identities[data["poc_identity_id"]]
        identity = await run_in_threadpool(get_identity)
        if not identity:
            return jsonify({"error": "POC identity not found"}), 404

    def update():
        service = db.services[id]
        if not service:
            return None

        # Update fields
        update_dict = {}
        if "name" in data:
            update_dict["name"] = data["name"]
        if "description" in data:
            update_dict["description"] = data["description"]
        if "domains" in data:
            update_dict["domains"] = data["domains"]
        if "paths" in data:
            update_dict["paths"] = data["paths"]
        if "poc_identity_id" in data:
            update_dict["poc_identity_id"] = data["poc_identity_id"]
        if "language" in data:
            update_dict["language"] = data["language"]
        if "deployment_method" in data:
            update_dict["deployment_method"] = data["deployment_method"]
        if "deployment_type" in data:
            update_dict["deployment_type"] = data["deployment_type"]
        if "is_public" in data:
            update_dict["is_public"] = data["is_public"]
        if "port" in data:
            update_dict["port"] = data["port"]
        if "health_endpoint" in data:
            update_dict["health_endpoint"] = data["health_endpoint"]
        if "repository_url" in data:
            update_dict["repository_url"] = data["repository_url"]
        if "documentation_url" in data:
            update_dict["documentation_url"] = data["documentation_url"]
        if "sla_uptime" in data:
            update_dict["sla_uptime"] = data["sla_uptime"]
        if "sla_response_time_ms" in data:
            update_dict["sla_response_time_ms"] = data["sla_response_time_ms"]
        if "notes" in data:
            update_dict["notes"] = data["notes"]
        if "tags" in data:
            update_dict["tags"] = data["tags"]
        if "status" in data:
            update_dict["status"] = data["status"]
        if "organization_id" in data:
            update_dict["organization_id"] = data["organization_id"]
            update_dict["tenant_id"] = org_tenant_id

        if update_dict:
            db(db.services.id == id).update(**update_dict)
            db.commit()

        return db.services[id]

    service = await run_in_threadpool(update)

    if not service:
        return jsonify({"error": "Service not found"}), 404

    service_dto = from_pydal_row(service, ServiceDTO)
    return jsonify(asdict(service_dto)), 200


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
@resource_role_required("maintainer")
async def delete_service(id: int):
    """
    Delete a service.

    Requires maintainer role.

    Path Parameters:
        - id: Service ID

    Returns:
        204: Service deleted
        403: Insufficient permissions
        404: Service not found

    Example:
        DELETE /api/v1/services/1
    """
    db = current_app.db

    def delete():
        service = db.services[id]
        if not service:
            return False

        del db.services[id]
        db.commit()
        return True

    success = await run_in_threadpool(delete)

    if not success:
        return jsonify({"error": "Service not found"}), 404

    return "", 204
