"""Services management API endpoints for Elder using PyDAL with async/await and shared helpers."""

from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, request

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.dataclasses import (PaginatedResponse, ServiceDTO,
                                         from_pydal_row, from_pydal_rows)
from apps.api.utils.api_responses import ApiResponse
from apps.api.utils.pydal_helpers import PaginationParams
from apps.api.utils.validation_helpers import (
    validate_json_body, validate_organization_and_get_tenant,
    validate_required_fields, validate_resource_exists)
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

    # Get pagination params using helper
    pagination = PaginationParams.from_request()

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
            query &= db.services.deployment_method == request.args.get(
                "deployment_method"
            )

        if request.args.get("status"):
            query &= db.services.status == request.args.get("status")

        if request.args.get("search"):
            search = request.args.get("search")
            search_pattern = f"%{search}%"
            query &= (db.services.name.ilike(search_pattern)) | (
                db.services.description.ilike(search_pattern)
            )

        # Get count and rows
        total = db(query).count()
        rows = db(query).select(
            orderby=~db.services.created_at,
            limitby=(pagination.offset, pagination.offset + pagination.per_page),
        )

        return total, rows

    total, rows = await run_in_threadpool(get_services)

    # Calculate total pages using helper
    pages = pagination.calculate_pages(total)

    # Convert to DTOs
    items = from_pydal_rows(rows, ServiceDTO)

    # Create paginated response
    response = PaginatedResponse(
        items=[asdict(item) for item in items],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
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
        JSON object with service fields (see docstring in original)

    Returns:
        201: Service created
        400: Invalid request
        403: Insufficient permissions

    Example:
        POST /api/v1/services
    """
    db = current_app.db

    # Validate JSON body
    data = request.get_json()
    if error := validate_json_body(data):
        return error

    # Validate required fields
    if error := validate_required_fields(data, ["name", "organization_id"]):
        return error

    # Get organization to derive tenant_id using helper
    org, tenant_id, error = await validate_organization_and_get_tenant(
        data["organization_id"]
    )
    if error:
        return error

    # Validate poc_identity_id if provided
    if data.get("poc_identity_id"):

        def get_identity():
            return db.identities[data["poc_identity_id"]]

        identity = await run_in_threadpool(get_identity)
        if not identity:
            return ApiResponse.not_found("POC identity", data["poc_identity_id"])

    def create():
        # Create service
        service_id = db.services.insert(
            name=data["name"],
            description=data.get("description"),
            organization_id=data["organization_id"],
            tenant_id=tenant_id,
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
    return ApiResponse.created(asdict(service_dto))


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

    # Validate resource exists using helper
    service, error = await validate_resource_exists(db.services, id, "Service")
    if error:
        return error

    service_dto = from_pydal_row(service, ServiceDTO)
    return ApiResponse.success(asdict(service_dto))


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
        JSON object with fields to update

    Returns:
        200: Service updated
        400: Invalid request
        403: Insufficient permissions
        404: Service not found

    Example:
        PUT /api/v1/services/1
    """
    db = current_app.db

    # Validate JSON body
    data = request.get_json()
    if error := validate_json_body(data):
        return error

    # If organization is being changed, validate and get tenant
    org_tenant_id = None
    if "organization_id" in data:
        org, org_tenant_id, error = await validate_organization_and_get_tenant(
            data["organization_id"]
        )
        if error:
            return error

    # Validate poc_identity_id if provided
    if "poc_identity_id" in data and data["poc_identity_id"]:

        def get_identity():
            return db.identities[data["poc_identity_id"]]

        identity = await run_in_threadpool(get_identity)
        if not identity:
            return ApiResponse.not_found("POC identity", data["poc_identity_id"])

    def update():
        service = db.services[id]
        if not service:
            return None

        # Update fields
        update_dict = {}
        updateable_fields = [
            "name",
            "description",
            "domains",
            "paths",
            "poc_identity_id",
            "language",
            "deployment_method",
            "deployment_type",
            "is_public",
            "port",
            "health_endpoint",
            "repository_url",
            "documentation_url",
            "sla_uptime",
            "sla_response_time_ms",
            "notes",
            "tags",
            "status",
        ]

        for field in updateable_fields:
            if field in data:
                update_dict[field] = data[field]

        if "organization_id" in data:
            update_dict["organization_id"] = data["organization_id"]
            update_dict["tenant_id"] = org_tenant_id

        if update_dict:
            db(db.services.id == id).update(**update_dict)
            db.commit()

        return db.services[id]

    service = await run_in_threadpool(update)

    if not service:
        return ApiResponse.not_found("Service", id)

    service_dto = from_pydal_row(service, ServiceDTO)
    return ApiResponse.success(asdict(service_dto))


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

    # Validate resource exists using helper
    service, error = await validate_resource_exists(db.services, id, "Service")
    if error:
        return error

    def delete():
        del db.services[id]
        db.commit()

    await run_in_threadpool(delete)

    return ApiResponse.no_content()
