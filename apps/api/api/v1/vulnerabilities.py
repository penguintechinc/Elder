"""Vulnerabilities management API endpoints for Elder using PyDAL with async/await and shared helpers."""

from dataclasses import asdict

from flask import Blueprint, current_app, jsonify, request

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.dataclasses import (
    ComponentVulnerabilityDTO,
    PaginatedResponse,
    VulnerabilityDTO,
    from_pydal_row,
    from_pydal_rows,
)
from apps.api.services.sbom.vulnerability.matcher import VulnerabilityMatcher
from apps.api.utils.api_responses import ApiResponse
from apps.api.utils.pydal_helpers import PaginationParams
from apps.api.utils.validation_helpers import (
    validate_json_body,
    validate_resource_exists,
)
from shared.async_utils import run_in_threadpool

bp = Blueprint("vulnerabilities", __name__)


@bp.route("", methods=["GET"])
@login_required
async def list_vulnerabilities():
    """
    List vulnerabilities with optional filtering.

    Query Parameters:
        - severity: Filter by severity (critical, high, medium, low, unknown)
        - cve_id: Filter by CVE ID
        - source: Filter by source (osv, nvd, github_advisory, manual)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)
        - search: Search in CVE ID, title, and description

    Returns:
        200: List of vulnerabilities with pagination
        400: Invalid parameters

    Example:
        GET /api/v1/vulnerabilities?severity=critical
    """
    db = current_app.db

    # Get pagination params using helper
    pagination = PaginationParams.from_request()

    # Build query
    def get_vulnerabilities():
        query = db.vulnerabilities.id > 0

        # Apply filters
        if request.args.get("severity"):
            query &= db.vulnerabilities.severity == request.args.get("severity").upper()

        if request.args.get("cve_id"):
            query &= db.vulnerabilities.cve_id == request.args.get("cve_id").upper()

        if request.args.get("source"):
            query &= db.vulnerabilities.source == request.args.get("source")

        if request.args.get("search"):
            search = request.args.get("search")
            search_pattern = f"%{search}%"
            query &= (
                (db.vulnerabilities.cve_id.ilike(search_pattern))
                | (db.vulnerabilities.title.ilike(search_pattern))
                | (db.vulnerabilities.description.ilike(search_pattern))
            )

        # Get count and rows
        total = db(query).count()
        rows = db(query).select(
            orderby=~db.vulnerabilities.created_at,
            limitby=(pagination.offset, pagination.offset + pagination.per_page),
        )

        return total, rows

    total, rows = await run_in_threadpool(get_vulnerabilities)

    # Calculate total pages using helper
    pages = pagination.calculate_pages(total)

    # Convert to DTOs
    items = from_pydal_rows(rows, VulnerabilityDTO)

    # Create paginated response
    response = PaginatedResponse(
        items=[asdict(item) for item in items],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=pages,
    )

    return jsonify(asdict(response)), 200


@bp.route("/<int:id>", methods=["GET"])
@login_required
async def get_vulnerability(id: int):
    """
    Get a single vulnerability by ID.

    Path Parameters:
        - id: Vulnerability ID

    Returns:
        200: Vulnerability details
        404: Vulnerability not found

    Example:
        GET /api/v1/vulnerabilities/1
    """
    db = current_app.db

    # Validate resource exists using helper
    vulnerability, error = await validate_resource_exists(
        db.vulnerabilities, id, "Vulnerability"
    )
    if error:
        return error

    vulnerability_dto = from_pydal_row(vulnerability, VulnerabilityDTO)
    return ApiResponse.success(asdict(vulnerability_dto))


@bp.route("/sync", methods=["POST"])
@login_required
@resource_role_required("maintainer")
async def sync_vulnerabilities():
    """
    Trigger vulnerability sync from OSV.dev and NVD.

    Syncs vulnerabilities for all SBOM components in the system.
    This is a long-running operation that runs asynchronously.

    Requires maintainer role.

    Request Body:
        - component_ids: Optional list of component IDs to sync (syncs all if not provided)
        - force: Force re-sync even if recently synced (default: false)

    Returns:
        202: Sync initiated
        400: Invalid request
        403: Insufficient permissions

    Example:
        POST /api/v1/vulnerabilities/sync
        {
            "component_ids": [1, 2, 3],
            "force": false
        }
    """
    db = current_app.db

    # Validate JSON body
    data = request.get_json() or {}

    component_ids = data.get("component_ids")
    force = data.get("force", False)

    def get_components():
        query = db.sbom_components.id > 0

        if component_ids:
            query &= db.sbom_components.id.belongs(component_ids)

        # Only sync components with PURL
        query &= db.sbom_components.purl != None  # noqa: E711
        query &= db.sbom_components.purl != ""

        return db(query).select()

    components = await run_in_threadpool(get_components)

    if not components:
        return ApiResponse.error("No components found to sync", 400)

    # Build component list for batch matching
    component_list = []
    for comp in components:
        component_list.append(
            {
                "id": comp.id,
                "purl": comp.purl,
                "package_type": comp.package_type,
                "name": comp.name,
                "version": comp.version,
            }
        )

    # Perform vulnerability matching in background
    # (In production, this would be a background task/worker)
    async def sync_task():
        async with VulnerabilityMatcher() as matcher:
            results = await matcher.match_components_batch(component_list)

            # Sync results to database
            def save_results():
                tenant_id = current_app.config.get("DEFAULT_TENANT_ID", 1)
                total_vulns = 0
                total_links = 0

                for comp_id, vulns in results.items():
                    for vuln in vulns:
                        # Sync vulnerability to DB
                        vuln_id = db.vulnerabilities.insert(
                            tenant_id=tenant_id,
                            cve_id=vuln.cve_id,
                            aliases=vuln.aliases,
                            severity=vuln.severity,
                            cvss_score=vuln.cvss_score,
                            cvss_vector=vuln.cvss_vector,
                            title=vuln.title,
                            description=vuln.description,
                            affected_packages=vuln.affected_packages,
                            fixed_versions=vuln.fixed_versions,
                            references=vuln.references,
                            source=vuln.source,
                            is_active=True,
                        )
                        total_vulns += 1

                        # Check if link exists
                        existing_link = db(
                            (db.component_vulnerabilities.component_id == comp_id)
                            & (db.component_vulnerabilities.vulnerability_id == vuln_id)
                        ).select().first()

                        if not existing_link:
                            # Create component-vulnerability link
                            db.component_vulnerabilities.insert(
                                tenant_id=tenant_id,
                                component_id=comp_id,
                                vulnerability_id=vuln_id,
                                status="open",
                            )
                            total_links += 1

                db.commit()
                return total_vulns, total_links

            total_vulns, total_links = await run_in_threadpool(save_results)

            return {
                "components_scanned": len(component_list),
                "vulnerabilities_found": total_vulns,
                "links_created": total_links,
            }

    # Run sync task
    result = await sync_task()

    return jsonify(result), 202


@bp.route("/dashboard", methods=["GET"])
@login_required
async def get_dashboard():
    """
    Get vulnerability dashboard summary statistics.

    Returns:
        200: Dashboard statistics

    Example:
        GET /api/v1/vulnerabilities/dashboard
    """
    db = current_app.db

    def get_stats():
        # Count vulnerabilities by severity
        critical_count = db(db.vulnerabilities.severity == "CRITICAL").count()
        high_count = db(db.vulnerabilities.severity == "HIGH").count()
        medium_count = db(db.vulnerabilities.severity == "MEDIUM").count()
        low_count = db(db.vulnerabilities.severity == "LOW").count()
        unknown_count = db(db.vulnerabilities.severity == "UNKNOWN").count()

        # Count component vulnerabilities by status
        open_count = db(db.component_vulnerabilities.status == "open").count()
        investigating_count = db(
            db.component_vulnerabilities.status == "investigating"
        ).count()
        remediated_count = db(
            db.component_vulnerabilities.status == "remediated"
        ).count()
        false_positive_count = db(
            db.component_vulnerabilities.status == "false_positive"
        ).count()
        accepted_count = db(db.component_vulnerabilities.status == "accepted").count()

        # Count affected components
        affected_components = db(
            (db.component_vulnerabilities.id > 0)
            & (db.component_vulnerabilities.status == "open")
        ).count()

        # Total vulnerabilities
        total_vulns = db(db.vulnerabilities.id > 0).count()

        return {
            "vulnerabilities_by_severity": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "unknown": unknown_count,
            },
            "component_vulnerabilities_by_status": {
                "open": open_count,
                "investigating": investigating_count,
                "remediated": remediated_count,
                "false_positive": false_positive_count,
                "accepted": accepted_count,
            },
            "total_vulnerabilities": total_vulns,
            "affected_components": affected_components,
        }

    stats = await run_in_threadpool(get_stats)

    return ApiResponse.success(stats)


@bp.route("/component-vulnerabilities/<int:id>", methods=["PATCH"])
@login_required
@resource_role_required("maintainer")
async def update_component_vulnerability(id: int):
    """
    Update component-vulnerability link status.

    Requires maintainer role.

    Path Parameters:
        - id: Component vulnerability link ID

    Request Body:
        - status: New status (open, investigating, remediated, false_positive, accepted)
        - remediation_notes: Optional remediation notes
        - remediated_by_id: Optional user ID who remediated

    Returns:
        200: Component vulnerability updated
        400: Invalid request
        403: Insufficient permissions
        404: Component vulnerability not found

    Example:
        PATCH /api/v1/vulnerabilities/component-vulnerabilities/1
        {
            "status": "remediated",
            "remediation_notes": "Updated to version 2.1.0"
        }
    """
    db = current_app.db

    # Validate JSON body
    data = request.get_json()
    if error := validate_json_body(data):
        return error

    # Validate resource exists
    comp_vuln, error = await validate_resource_exists(
        db.component_vulnerabilities, id, "Component Vulnerability"
    )
    if error:
        return error

    def update():
        update_dict = {}

        if "status" in data:
            valid_statuses = [
                "open",
                "investigating",
                "remediated",
                "false_positive",
                "accepted",
            ]
            if data["status"] not in valid_statuses:
                return None, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

            update_dict["status"] = data["status"]

            # Set remediated_at if status is remediated
            if data["status"] == "remediated":
                update_dict["remediated_at"] = request.utcnow

        if "remediation_notes" in data:
            update_dict["remediation_notes"] = data["remediation_notes"]

        if "remediated_by_id" in data:
            update_dict["remediated_by_id"] = data["remediated_by_id"]

        if update_dict:
            db(db.component_vulnerabilities.id == id).update(**update_dict)
            db.commit()

        return db.component_vulnerabilities[id], None

    updated, error_msg = await run_in_threadpool(update)

    if error_msg:
        return ApiResponse.error(error_msg, 400)

    if not updated:
        return ApiResponse.not_found("Component Vulnerability", id)

    comp_vuln_dto = from_pydal_row(updated, ComponentVulnerabilityDTO)
    return ApiResponse.success(asdict(comp_vuln_dto))
