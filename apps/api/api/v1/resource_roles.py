"""Resource Role management API endpoints using PyDAL with async/await."""

from dataclasses import asdict

from flask import Blueprint, current_app, g, jsonify, request

from apps.api.auth.decorators import login_required
from apps.api.models.dataclasses import (ResourceRoleDTO, from_pydal_row,
                                         from_pydal_rows)
from shared.async_utils import run_in_threadpool
from shared.licensing import license_required

bp = Blueprint("resource_roles", __name__)


@bp.route("", methods=["GET"])
@login_required
@license_required("enterprise")
async def list_resource_roles():
    """
    List resource role assignments with optional filtering.

    Query Parameters:
        - identity_id: Filter by identity
        - group_id: Filter by group
        - resource_type: Filter by resource type (entity/organization)
        - resource_id: Filter by resource ID
        - role: Filter by role (maintainer/operator/viewer)

    Returns:
        200: List of resource roles
        403: License required

    Example:
        GET /api/v1/resource-roles?resource_type=entity&resource_id=42
        {
            "items": [
                {
                    "id": 1,
                    "identity_id": 5,
                    "resource_type": "entity",
                    "resource_id": 42,
                    "role": "maintainer",
                    "created_at": "2024-10-23T10:00:00Z"
                }
            ],
            "total": 1
        }
    """
    db = current_app.db

    # Build query
    def get_roles():
        query = db.resource_roles.id > 0

        # Apply filters from query params
        if request.args.get("identity_id"):
            identity_id = request.args.get("identity_id", type=int)
            query &= db.resource_roles.identity_id == identity_id

        if request.args.get("group_id"):
            group_id = request.args.get("group_id", type=int)
            query &= db.resource_roles.group_id == group_id

        if request.args.get("resource_type"):
            resource_type = request.args.get("resource_type")
            query &= db.resource_roles.resource_type == resource_type

        if request.args.get("resource_id"):
            resource_id = request.args.get("resource_id", type=int)
            query &= db.resource_roles.resource_id == resource_id

        if request.args.get("role"):
            role = request.args.get("role")
            query &= db.resource_roles.role == role

        roles = db(query).select()
        return roles

    rows = await run_in_threadpool(get_roles)

    # Convert to DTOs
    items = from_pydal_rows(rows, ResourceRoleDTO)

    return (
        jsonify({"items": [asdict(item) for item in items], "total": len(items)}),
        200,
    )


@bp.route("", methods=["POST"])
@login_required
@license_required("enterprise")
async def create_resource_role():
    """
    Grant a resource role to an identity or group.

    Requires maintainer role on the resource to grant roles.

    Request Body:
        {
            "identity_id": 5 (optional),
            "group_id": 3 (optional),
            "resource_type": "entity",
            "resource_id": 42,
            "role": "operator"
        }

    Returns:
        201: Resource role created
        400: Invalid request
        403: License required or insufficient permissions
        409: Role already exists

    Example:
        POST /api/v1/resource-roles
        {
            "identity_id": 5,
            "resource_type": "entity",
            "resource_id": 42,
            "role": "operator"
        }

        Response:
        {
            "id": 1,
            "identity_id": 5,
            "resource_type": "entity",
            "resource_id": 42,
            "role": "operator",
            "created_at": "2024-10-23T10:00:00Z"
        }
    """
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("resource_type"):
        return jsonify({"error": "resource_type is required"}), 400
    if not data.get("role"):
        return jsonify({"error": "role is required"}), 400

    # Must have either identity_id or group_id
    if not data.get("identity_id") and not data.get("group_id"):
        return jsonify({"error": "Either identity_id or group_id is required"}), 400

    resource_type = data["resource_type"]
    resource_id = data.get("resource_id")
    role = data["role"]

    # Check if current user has maintainer role on this resource
    def check_and_create():
        # Superusers can grant any role
        if not g.current_user.is_superuser:
            # Check if current user has maintainer role
            has_maintainer = (
                db(
                    (db.resource_roles.identity_id == g.current_user.id)
                    & (db.resource_roles.resource_type == resource_type)
                    & (db.resource_roles.resource_id == resource_id)
                    & (db.resource_roles.role == "maintainer")
                )
                .select()
                .first()
            )

            if not has_maintainer:
                return (
                    None,
                    "Insufficient permissions - only maintainers can grant resource roles",
                    403,
                )

        # Check if role already exists
        if data.get("identity_id"):
            existing_role = (
                db(
                    (db.resource_roles.identity_id == data["identity_id"])
                    & (db.resource_roles.resource_type == resource_type)
                    & (db.resource_roles.resource_id == resource_id)
                )
                .select()
                .first()
            )
        else:
            existing_role = (
                db(
                    (db.resource_roles.group_id == data["group_id"])
                    & (db.resource_roles.resource_type == resource_type)
                    & (db.resource_roles.resource_id == resource_id)
                )
                .select()
                .first()
            )

        if existing_role:
            return (
                None,
                f"Role already exists for this identity/group on this resource",
                409,
            )

        # Create resource role
        role_id = db.resource_roles.insert(
            identity_id=data.get("identity_id"),
            group_id=data.get("group_id"),
            resource_type=resource_type,
            resource_id=resource_id,
            role=role,
        )
        db.commit()

        return db.resource_roles[role_id], None, None

    result, error, status = await run_in_threadpool(check_and_create)

    if error:
        return jsonify({"error": error}), status

    role_dto = from_pydal_row(result, ResourceRoleDTO)
    return jsonify(asdict(role_dto)), 201


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
@license_required("enterprise")
async def revoke_resource_role(id: int):
    """
    Revoke a resource role.

    Requires maintainer role on the resource to revoke roles.

    Path Parameters:
        - id: Resource role ID

    Returns:
        204: Resource role revoked
        403: License required or insufficient permissions
        404: Resource role not found

    Example:
        DELETE /api/v1/resource-roles/1
    """
    db = current_app.db

    # Check and delete role
    def check_and_delete():
        role = db.resource_roles[id]
        if not role:
            return None, "Resource role not found", 404

        # Check if current user has maintainer role on this resource
        # Superusers can revoke any role
        if not g.current_user.is_superuser:
            has_maintainer = (
                db(
                    (db.resource_roles.identity_id == g.current_user.id)
                    & (db.resource_roles.resource_type == role.resource_type)
                    & (db.resource_roles.resource_id == role.resource_id)
                    & (db.resource_roles.role == "maintainer")
                )
                .select()
                .first()
            )

            if not has_maintainer:
                return (
                    None,
                    "Insufficient permissions - only maintainers can revoke resource roles",
                    403,
                )

        # Delete role
        db(db.resource_roles.id == id).delete()
        db.commit()

        return True, None, None

    result, error, status = await run_in_threadpool(check_and_delete)

    if error:
        return jsonify({"error": error}), status

    return "", 204


@bp.route("/entities/<int:id>/roles", methods=["GET"])
@login_required
@license_required("enterprise")
async def list_entity_roles(id: int):
    """
    List all resource roles for an entity.

    Path Parameters:
        - id: Entity ID

    Returns:
        200: List of resource roles for this entity
        403: License required
        404: Entity not found

    Example:
        GET /api/v1/resource-roles/entities/42/roles
        {
            "items": [
                {
                    "id": 1,
                    "identity_id": 5,
                    "role": "maintainer"
                }
            ],
            "total": 1
        }
    """
    db = current_app.db

    def get_entity_roles():
        # Verify entity exists
        entity = db.entities[id]
        if not entity:
            return None, "Entity not found", 404

        # Get all roles for this entity
        roles = db(
            (db.resource_roles.resource_type == "entity")
            & (db.resource_roles.resource_id == id)
        ).select()

        return roles, None, None

    result, error, status = await run_in_threadpool(get_entity_roles)

    if error:
        return jsonify({"error": error}), status

    # Convert to DTOs
    items = from_pydal_rows(result, ResourceRoleDTO)

    return (
        jsonify({"items": [asdict(item) for item in items], "total": len(items)}),
        200,
    )


@bp.route("/organizations/<int:id>/roles", methods=["GET"])
@login_required
@license_required("enterprise")
async def list_organization_roles(id: int):
    """
    List all resource roles for an organization.

    Path Parameters:
        - id: Organization ID

    Returns:
        200: List of resource roles for this organization
        403: License required
        404: Organization not found

    Example:
        GET /api/v1/resource-roles/organizations/1/roles
        {
            "items": [
                {
                    "id": 2,
                    "identity_id": 3,
                    "role": "operator"
                }
            ],
            "total": 1
        }
    """
    db = current_app.db

    def get_org_roles():
        # Verify organization exists
        org = db.organizations[id]
        if not org:
            return None, "Organization not found", 404

        # Get all roles for this organization
        roles = db(
            (db.resource_roles.resource_type == "organization")
            & (db.resource_roles.resource_id == id)
        ).select()

        return roles, None, None

    result, error, status = await run_in_threadpool(get_org_roles)

    if error:
        return jsonify({"error": error}), status

    # Convert to DTOs
    items = from_pydal_rows(result, ResourceRoleDTO)

    return (
        jsonify({"items": [asdict(item) for item in items], "total": len(items)}),
        200,
    )


@bp.route("/identities/<int:id>/resource-roles", methods=["GET"])
@login_required
@license_required("enterprise")
async def list_identity_resource_roles(id: int):
    """
    List all resource roles assigned to an identity.

    Path Parameters:
        - id: Identity ID

    Returns:
        200: List of resource roles for this identity
        403: License required
        404: Identity not found

    Example:
        GET /api/v1/resource-roles/identities/5/resource-roles
        {
            "items": [
                {
                    "id": 1,
                    "resource_type": "entity",
                    "resource_id": 42,
                    "role": "maintainer"
                },
                {
                    "id": 2,
                    "resource_type": "organization",
                    "resource_id": 1,
                    "role": "operator"
                }
            ],
            "total": 2
        }
    """
    db = current_app.db

    def get_identity_roles():
        # Verify identity exists
        identity = db.identities[id]
        if not identity:
            return None, "Identity not found", 404

        # Get all roles for this identity
        roles = db(db.resource_roles.identity_id == id).select()

        return roles, None, None

    result, error, status = await run_in_threadpool(get_identity_roles)

    if error:
        return jsonify({"error": error}), status

    # Convert to DTOs
    items = from_pydal_rows(result, ResourceRoleDTO)

    return (
        jsonify({"items": [asdict(item) for item in items], "total": len(items)}),
        200,
    )
