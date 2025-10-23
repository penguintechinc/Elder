"""Resource Role management API endpoints."""

from flask import Blueprint, jsonify, request, g
from marshmallow import ValidationError

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.resource_role import (
    ResourceRole,
    ResourceType,
    ResourceRoleType,
)
from apps.api.schemas.resource_role import (
    ResourceRoleSchema,
    ResourceRoleCreateSchema,
    ResourceRoleFilterSchema,
    ResourceRoleListSchema,
)
from shared.api_utils import get_or_404, make_error_response
from shared.database import db
from shared.licensing import license_required

bp = Blueprint("resource_roles", __name__)


@bp.route("", methods=["GET"])
@login_required
@license_required("enterprise")
def list_resource_roles():
    """
    List resource role assignments with optional filtering.

    Query Parameters:
        - identity_id: Filter by identity
        - resource_type: Filter by resource type (entity/organization)
        - resource_id: Filter by resource ID
        - role_type: Filter by role type (maintainer/operator/viewer)

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
                    "role_type": "maintainer",
                    "created_at": "2024-10-23T10:00:00Z"
                }
            ],
            "total": 1
        }
    """
    # Validate query parameters
    filter_schema = ResourceRoleFilterSchema()
    try:
        filters = filter_schema.load(request.args)
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Build query
    query = db.session.query(ResourceRole)

    # Apply filters
    if "identity_id" in filters:
        query = query.filter_by(identity_id=filters["identity_id"])
    if "resource_type" in filters:
        query = query.filter_by(resource_type=ResourceType(filters["resource_type"]))
    if "resource_id" in filters:
        query = query.filter_by(resource_id=filters["resource_id"])
    if "role_type" in filters:
        query = query.filter_by(role_type=ResourceRoleType(filters["role_type"]))

    # Execute query
    roles = query.all()

    # Serialize response
    list_schema = ResourceRoleListSchema()
    return jsonify(list_schema.dump({"items": roles, "total": len(roles)})), 200


@bp.route("", methods=["POST"])
@login_required
@license_required("enterprise")
def create_resource_role():
    """
    Grant a resource role to an identity.

    Requires maintainer role on the resource to grant roles.

    Request Body:
        {
            "identity_id": 5,
            "resource_type": "entity",
            "resource_id": 42,
            "role_type": "operator"
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
            "role_type": "operator"
        }

        Response:
        {
            "id": 1,
            "identity_id": 5,
            "resource_type": "entity",
            "resource_id": 42,
            "role_type": "operator",
            "granted_by_id": 1,
            "created_at": "2024-10-23T10:00:00Z"
        }
    """
    # Validate request
    create_schema = ResourceRoleCreateSchema()
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return make_error_response(str(e.messages), 400)

    # Check if current user has maintainer role on this resource
    resource_type_enum = ResourceType(data["resource_type"])
    resource_id = data["resource_id"]

    # Superusers can grant any role
    if not g.current_user.is_superuser:
        has_maintainer = ResourceRole.check_permission(
            identity_id=g.current_user.id,
            resource_type=resource_type_enum,
            resource_id=resource_id,
            required_role=ResourceRoleType.MAINTAINER,
        )

        if not has_maintainer:
            return (
                jsonify(
                    {
                        "error": "Insufficient permissions",
                        "message": "Only maintainers can grant resource roles",
                    }
                ),
                403,
            )

    # Check if role already exists
    existing_role = ResourceRole.get_user_role(
        identity_id=data["identity_id"],
        resource_type=resource_type_enum,
        resource_id=resource_id,
    )

    if existing_role:
        return (
            jsonify(
                {
                    "error": "Role already exists",
                    "message": f"Identity {data['identity_id']} already has {existing_role.role_type.value} role on this resource",
                    "existing_role_id": existing_role.id,
                }
            ),
            409,
        )

    # Create resource role
    role = ResourceRole(
        identity_id=data["identity_id"],
        resource_type=resource_type_enum,
        resource_id=resource_id,
        role_type=ResourceRoleType(data["role_type"]),
        granted_by_id=g.current_user.id,
    )

    db.session.add(role)
    db.session.commit()

    # Serialize response
    schema = ResourceRoleSchema()
    return jsonify(schema.dump(role)), 201


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
@license_required("enterprise")
def revoke_resource_role(id: int):
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
    role = get_or_404(ResourceRole, id)

    # Check if current user has maintainer role on this resource
    # Superusers can revoke any role
    if not g.current_user.is_superuser:
        has_maintainer = ResourceRole.check_permission(
            identity_id=g.current_user.id,
            resource_type=role.resource_type,
            resource_id=role.resource_id,
            required_role=ResourceRoleType.MAINTAINER,
        )

        if not has_maintainer:
            return (
                jsonify(
                    {
                        "error": "Insufficient permissions",
                        "message": "Only maintainers can revoke resource roles",
                    }
                ),
                403,
            )

    # Delete role
    db.session.delete(role)
    db.session.commit()

    return "", 204


@bp.route("/entities/<int:id>/roles", methods=["GET"])
@login_required
@license_required("enterprise")
def list_entity_roles(id: int):
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
                    "identity": {"id": 5, "username": "john"},
                    "role_type": "maintainer"
                }
            ],
            "total": 1
        }
    """
    from apps.api.models import Entity

    entity = get_or_404(Entity, id)

    # Get all roles for this entity
    roles = ResourceRole.get_users_with_role(ResourceType.ENTITY, entity.id)

    # Serialize response
    list_schema = ResourceRoleListSchema()
    return jsonify(list_schema.dump({"items": roles, "total": len(roles)})), 200


@bp.route("/organizations/<int:id>/roles", methods=["GET"])
@login_required
@license_required("enterprise")
def list_organization_roles(id: int):
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
                    "identity": {"id": 3, "username": "jane"},
                    "role_type": "operator"
                }
            ],
            "total": 1
        }
    """
    from apps.api.models import Organization

    org = get_or_404(Organization, id)

    # Get all roles for this organization
    roles = ResourceRole.get_users_with_role(ResourceType.ORGANIZATION, org.id)

    # Serialize response
    list_schema = ResourceRoleListSchema()
    return jsonify(list_schema.dump({"items": roles, "total": len(roles)})), 200


@bp.route("/identities/<int:id>/resource-roles", methods=["GET"])
@login_required
@license_required("enterprise")
def list_identity_resource_roles(id: int):
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
                    "role_type": "maintainer"
                },
                {
                    "id": 2,
                    "resource_type": "organization",
                    "resource_id": 1,
                    "role_type": "operator"
                }
            ],
            "total": 2
        }
    """
    from apps.api.models import Identity

    identity = get_or_404(Identity, id)

    # Get all roles for this identity
    roles = db.session.query(ResourceRole).filter_by(identity_id=identity.id).all()

    # Serialize response
    list_schema = ResourceRoleListSchema()
    return jsonify(list_schema.dump({"items": roles, "total": len(roles)})), 200
