"""Software tracking management API endpoints for Elder using PyDAL with async/await and shared helpers."""

from dataclasses import asdict

from flask import Blueprint, Response, current_app, jsonify, request

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.dataclasses import (
    PaginatedResponse,
    SBOMComponentDTO,
    from_pydal_rows,
)
from apps.api.services.sbom.exporters import CycloneDXExporter, SPDXExporter
from apps.api.utils.api_responses import ApiResponse
from apps.api.utils.pydal_helpers import PaginationParams
from apps.api.utils.validation_helpers import (
    validate_enum_value,
    validate_json_body,
    validate_organization_and_get_tenant,
    validate_required_fields,
    validate_resource_exists,
)
from shared.async_utils import run_in_threadpool

bp = Blueprint("software", __name__)

# Valid software types
VALID_SOFTWARE_TYPES = [
    "saas",
    "paas",
    "iaas",
    "productivity",
    "software",
    "administrative",
    "security",
    "development",
    "monitoring",
    "database",
    "communication",
    "other",
]


@bp.route("", methods=["GET"])
@login_required
async def list_software():
    """List software with optional filtering."""
    db = current_app.db
    pagination = PaginationParams.from_request()

    def get_software():
        query = db.software.id > 0

        if request.args.get("organization_id"):
            query &= db.software.organization_id == request.args.get(
                "organization_id", type=int
            )
        if request.args.get("software_type"):
            query &= db.software.software_type == request.args.get("software_type")
        if request.args.get("is_active") is not None:
            is_active = request.args.get("is_active", "").lower() == "true"
            query &= db.software.is_active == is_active
        if request.args.get("search"):
            search = f"%{request.args.get('search')}%"
            query &= (db.software.name.ilike(search)) | (
                db.software.description.ilike(search)
            )

        total = db(query).count()
        rows = db(query).select(
            orderby=~db.software.created_at,
            limitby=(pagination.offset, pagination.offset + pagination.per_page),
        )
        return total, rows

    total, rows = await run_in_threadpool(get_software)
    pages = pagination.calculate_pages(total)

    response = PaginatedResponse(
        items=[row.as_dict() for row in rows],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=pages,
    )

    return jsonify(asdict(response)), 200


@bp.route("", methods=["POST"])
@login_required
@resource_role_required("viewer")
async def create_software():
    """Create a new software entry."""
    db = current_app.db

    data = request.get_json()
    if error := validate_json_body(data):
        return error

    if error := validate_required_fields(data, ["name", "organization_id"]):
        return error

    if data.get("software_type"):
        if error := validate_enum_value(
            data["software_type"], VALID_SOFTWARE_TYPES, "software_type"
        ):
            return error

    if data.get("purchasing_poc_id"):
        identity, error = await validate_resource_exists(
            db.identities, data["purchasing_poc_id"], "Purchasing POC identity"
        )
        if error:
            return error

    org, tenant_id, error = await validate_organization_and_get_tenant(
        data["organization_id"]
    )
    if error:
        return error

    def create():
        software_id = db.software.insert(
            name=data["name"],
            description=data.get("description"),
            organization_id=data["organization_id"],
            tenant_id=tenant_id,
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
    return ApiResponse.created(software.as_dict())


@bp.route("/<int:id>", methods=["GET"])
@login_required
async def get_software(id: int):
    """Get a single software entry by ID."""
    db = current_app.db

    software, error = await validate_resource_exists(db.software, id, "Software")
    if error:
        return error

    return ApiResponse.success(software.as_dict())


@bp.route("/<int:id>", methods=["PUT"])
@login_required
@resource_role_required("maintainer")
async def update_software(id: int):
    """Update a software entry."""
    db = current_app.db

    data = request.get_json()
    if error := validate_json_body(data):
        return error

    if data.get("software_type"):
        if error := validate_enum_value(
            data["software_type"], VALID_SOFTWARE_TYPES, "software_type"
        ):
            return error

    if data.get("purchasing_poc_id"):
        identity, error = await validate_resource_exists(
            db.identities, data["purchasing_poc_id"], "Purchasing POC identity"
        )
        if error:
            return error

    org_tenant_id = None
    if "organization_id" in data:
        org, org_tenant_id, error = await validate_organization_and_get_tenant(
            data["organization_id"]
        )
        if error:
            return error

    def update():
        software = db.software[id]
        if not software:
            return None

        update_dict = {}
        updateable_fields = [
            "name",
            "description",
            "purchasing_poc_id",
            "license_url",
            "version",
            "business_purpose",
            "software_type",
            "seats",
            "cost_monthly",
            "renewal_date",
            "vendor",
            "support_contact",
            "notes",
            "tags",
            "is_active",
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
        return ApiResponse.not_found("Software", id)

    return ApiResponse.success(software.as_dict())


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
@resource_role_required("maintainer")
async def delete_software(id: int):
    """Delete a software entry."""
    db = current_app.db

    software, error = await validate_resource_exists(db.software, id, "Software")
    if error:
        return error

    def delete():
        del db.software[id]
        db.commit()

    await run_in_threadpool(delete)

    return ApiResponse.no_content()


@bp.route("/<int:id>/sbom", methods=["GET"])
@login_required
async def get_software_sbom(id: int):
    """
    Get SBOM components for a software.

    Path Parameters:
        - id: Software ID

    Returns:
        200: List of SBOM components
        404: Software not found

    Example:
        GET /api/v1/software/1/sbom
    """
    db = current_app.db

    # Validate software exists
    software, error = await validate_resource_exists(db.software, id, "Software")
    if error:
        return error

    def get_components():
        query = (db.sbom_components.parent_type == "software") & (
            db.sbom_components.parent_id == id
        )
        rows = db(query).select(orderby=db.sbom_components.name)
        return rows

    rows = await run_in_threadpool(get_components)

    # Convert to DTOs
    items = from_pydal_rows(rows, SBOMComponentDTO)

    return jsonify([asdict(item) for item in items]), 200


@bp.route("/<int:id>/sbom/export", methods=["GET"])
@login_required
async def export_software_sbom(id: int):
    """
    Export software SBOM in standard format.

    Path Parameters:
        - id: Software ID

    Query Parameters:
        - format: Export format (cyclonedx_json, cyclonedx_xml, spdx) - default: cyclonedx_json

    Returns:
        200: SBOM file content
        400: Invalid format or no components
        404: Software not found

    Example:
        GET /api/v1/software/1/sbom/export?format=cyclonedx_json
        GET /api/v1/software/1/sbom/export?format=cyclonedx_xml
        GET /api/v1/software/1/sbom/export?format=spdx
    """
    db = current_app.db

    # Validate software exists
    software, error = await validate_resource_exists(db.software, id, "Software")
    if error:
        return error

    # Get format parameter
    export_format = request.args.get("format", "cyclonedx_json")
    supported_formats = ["cyclonedx_json", "cyclonedx_xml", "spdx"]

    if export_format not in supported_formats:
        return ApiResponse.error(
            f"Invalid format. Supported: {', '.join(supported_formats)}", 400
        )

    def get_components():
        query = (db.sbom_components.parent_type == "software") & (
            db.sbom_components.parent_id == id
        )
        rows = db(query).select(orderby=db.sbom_components.name)
        # Convert rows to dictionaries
        return [dict(row) for row in rows]

    components = await run_in_threadpool(get_components)

    if not components:
        return ApiResponse.error("No SBOM components found for this software", 400)

    # Build metadata
    metadata = {
        "name": software.name,
        "version": getattr(software, "version", "unknown"),
        "description": software.description,
    }

    # Export based on format
    try:
        if export_format == "cyclonedx_json":
            exporter = CycloneDXExporter()
            content = exporter.export_json(components, metadata)
            mimetype = "application/json"
            filename = f"{software.name.replace(' ', '_')}_sbom_cyclonedx.json"

        elif export_format == "cyclonedx_xml":
            exporter = CycloneDXExporter()
            content = exporter.export_xml(components, metadata)
            mimetype = "application/xml"
            filename = f"{software.name.replace(' ', '_')}_sbom_cyclonedx.xml"

        else:  # spdx
            exporter = SPDXExporter()
            content = exporter.export_json(components, metadata)
            mimetype = "application/json"
            filename = f"{software.name.replace(' ', '_')}_sbom_spdx.json"

        # Return as downloadable file
        return Response(
            content,
            mimetype=mimetype,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        return ApiResponse.error(f"Failed to export SBOM: {str(e)}", 500)
