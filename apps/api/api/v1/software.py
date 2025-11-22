"""Software tracking management API endpoints for Elder using PyDAL with async/await."""

from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, request

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.dataclasses import PaginatedResponse
from shared.async_utils import run_in_threadpool

bp = Blueprint("software", __name__)

# Valid software types
VALID_SOFTWARE_TYPES = [
    "saas", "paas", "iaas", "productivity", "software",
    "administrative", "security", "development", "monitoring",
    "database", "communication", "other"
]


@bp.route("", methods=["GET"])
@login_required
async def list_software():
    """
    List software with optional filtering.

    Query Parameters:
        - organization_id: Filter by organization
        - software_type: Filter by software type
        - is_active: Filter by active status (true/false)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)
        - search: Search in name and description

    Returns:
        200: List of software with pagination
        400: Invalid parameters

    Example:
        GET /api/v1/software?organization_id=1&software_type=saas&is_active=true
    """
    db = current_app.db

    # Get pagination params
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 1000)

    # Build query
    def get_software():
        query = db.software.id > 0

        # Apply filters
        if request.args.get("organization_id"):
            org_id = request.args.get("organization_id", type=int)
            query &= db.software.organization_id == org_id

        if request.args.get("software_type"):
            query &= db.software.software_type == request.args.get("software_type")

        if request.args.get("is_active") is not None:
            is_active = request.args.get("is_active", "").lower() == "true"
            query &= db.software.is_active == is_active

        if request.args.get("search"):
            search = request.args.get("search")
            search_pattern = f"%{search}%"
            query &= (db.software.name.ilike(search_pattern)) | (
                db.software.description.ilike(search_pattern)
            )

        # Calculate pagination
        offset = (page - 1) * per_page

        # Get count and rows
        total = db(query).count()
        rows = db(query).select(
            orderby=~db.software.created_at, limitby=(offset, offset + per_page)
        )

        return total, rows

    total, rows = await run_in_threadpool(get_software)

    # Calculate total pages
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    # Convert rows to dicts
    items = [row.as_dict() for row in rows]

    # Create paginated response
    response = PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )

    return jsonify(asdict(response)), 200


@bp.route("", methods=["POST"])
@login_required
@resource_role_required("viewer")
async def create_software():
    """
    Create a new software entry.

    Requires viewer role on the resource.

    Request Body:
        {
            "name": "Microsoft 365",
            "description": "Office productivity suite",
            "organization_id": 1,
            "software_type": "saas",
            "vendor": "Microsoft",
            "seats": 100,
            "cost_monthly": 1500.00,
            "renewal_date": "2025-12-31",
            "license_url": "https://portal.office.com",
            "version": "Enterprise E3",
            "business_purpose": "Email and document collaboration",
            "purchasing_poc_id": 5,
            "support_contact": "support@microsoft.com",
            "notes": "Annual subscription",
            "tags": "productivity,email,office",
            "is_active": true
        }

    Returns:
        201: Software created
        400: Invalid request
        403: Insufficient permissions

    Example:
        POST /api/v1/software
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

    # Validate software_type if provided
    if data.get("software_type") and data["software_type"] not in VALID_SOFTWARE_TYPES:
        return jsonify({
            "error": f"Invalid software_type. Must be one of: {', '.join(VALID_SOFTWARE_TYPES)}"
        }), 400

    # Validate purchasing_poc_id if provided
    if data.get("purchasing_poc_id"):
        def check_identity():
            return db.identities[data["purchasing_poc_id"]]

        identity = await run_in_threadpool(check_identity)
        if not identity:
            return jsonify({"error": "Purchasing POC identity not found"}), 404

    # Get organization to derive tenant_id
    def get_org():
        return db.organizations[data["organization_id"]]

    org = await run_in_threadpool(get_org)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    if not org.tenant_id:
        return jsonify({"error": "Organization must have a tenant"}), 400

    def create():
        # Create software entry
        software_id = db.software.insert(
            name=data["name"],
            description=data.get("description"),
            organization_id=data["organization_id"],
            tenant_id=org.tenant_id,
            purchasing_poc_id=data.get("purchasing_poc_id"),
            license_url=data.get("license_url"),
            version=data.get("version"),
            business_purpose=data.get("business_purpose"),
            software_type=data.get("software_type", "other"),
            seats=data.get("seats"),
            cost_monthly=data.get("cost_monthly"),
            renewal_date=data.get("renewal_date"),
            vendor=data.get("vendor"),
            support_contact=data.get("support_contact"),
            notes=data.get("notes"),
            tags=data.get("tags"),
            is_active=data.get("is_active", True),
        )
        db.commit()

        return db.software[software_id]

    software = await run_in_threadpool(create)

    return jsonify(software.as_dict()), 201


@bp.route("/<int:id>", methods=["GET"])
@login_required
async def get_software(id: int):
    """
    Get a single software entry by ID.

    Path Parameters:
        - id: Software ID

    Returns:
        200: Software details
        404: Software not found

    Example:
        GET /api/v1/software/1
    """
    db = current_app.db

    software = await run_in_threadpool(lambda: db.software[id])

    if not software:
        return jsonify({"error": "Software not found"}), 404

    return jsonify(software.as_dict()), 200


@bp.route("/<int:id>", methods=["PUT"])
@login_required
@resource_role_required("maintainer")
async def update_software(id: int):
    """
    Update a software entry.

    Requires maintainer role.

    Path Parameters:
        - id: Software ID

    Request Body:
        {
            "name": "Updated Software Name",
            "seats": 200,
            "cost_monthly": 2500.00,
            "is_active": false
        }

    Returns:
        200: Software updated
        400: Invalid request
        403: Insufficient permissions
        404: Software not found

    Example:
        PUT /api/v1/software/1
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate software_type if provided
    if data.get("software_type") and data["software_type"] not in VALID_SOFTWARE_TYPES:
        return jsonify({
            "error": f"Invalid software_type. Must be one of: {', '.join(VALID_SOFTWARE_TYPES)}"
        }), 400

    # Validate purchasing_poc_id if provided
    if data.get("purchasing_poc_id"):
        def check_identity():
            return db.identities[data["purchasing_poc_id"]]

        identity = await run_in_threadpool(check_identity)
        if not identity:
            return jsonify({"error": "Purchasing POC identity not found"}), 404

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

    def update():
        software = db.software[id]
        if not software:
            return None

        # Update fields
        update_dict = {}
        updateable_fields = [
            "name", "description", "purchasing_poc_id", "license_url",
            "version", "business_purpose", "software_type", "seats",
            "cost_monthly", "renewal_date", "vendor", "support_contact",
            "notes", "tags", "is_active"
        ]

        for field in updateable_fields:
            if field in data:
                update_dict[field] = data[field]

        if "organization_id" in data:
            update_dict["organization_id"] = data["organization_id"]
            update_dict["tenant_id"] = org_tenant_id

        if update_dict:
            db(db.software.id == id).update(**update_dict)
            db.commit()

        return db.software[id]

    software = await run_in_threadpool(update)

    if not software:
        return jsonify({"error": "Software not found"}), 404

    return jsonify(software.as_dict()), 200


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
@resource_role_required("maintainer")
async def delete_software(id: int):
    """
    Delete a software entry.

    Requires maintainer role.

    Path Parameters:
        - id: Software ID

    Returns:
        204: Software deleted
        403: Insufficient permissions
        404: Software not found

    Example:
        DELETE /api/v1/software/1
    """
    db = current_app.db

    def delete():
        software = db.software[id]
        if not software:
            return False

        del db.software[id]
        db.commit()
        return True

    success = await run_in_threadpool(delete)

    if not success:
        return jsonify({"error": "Software not found"}), 404

    return "", 204
