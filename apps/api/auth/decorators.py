"""Authentication and authorization decorators."""

from functools import wraps
from flask import jsonify, g, request
from typing import Callable, List, Optional

from apps.api.auth.jwt_handler import get_current_user
from apps.api.models import Identity, Permission


def login_required(f: Callable) -> Callable:
    """
    Decorator to require authentication for an endpoint.

    Usage:
        @bp.route('/protected')
        @login_required
        def protected_route():
            return jsonify({"user": g.current_user.username})
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not user:
            return jsonify({"error": "Authentication required"}), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def permission_required(permission_name: str) -> Callable:
    """
    Decorator to require specific permission for an endpoint.

    Args:
        permission_name: Name of required permission (e.g., 'create_entity')

    Usage:
        @bp.route('/entities', methods=['POST'])
        @permission_required('create_entity')
        def create_entity():
            # Create entity logic
            pass
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({"error": "Authentication required"}), 401

            # Superusers have all permissions
            if user.is_superuser:
                g.current_user = user
                return f(*args, **kwargs)

            # Check if user has required permission
            has_permission = _check_user_permission(user, permission_name)

            if not has_permission:
                return (
                    jsonify(
                        {
                            "error": "Insufficient permissions",
                            "required_permission": permission_name,
                        }
                    ),
                    403,
                )

            g.current_user = user
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def permissions_required(permission_names: List[str], require_all: bool = True) -> Callable:
    """
    Decorator to require multiple permissions.

    Args:
        permission_names: List of permission names
        require_all: If True, require all permissions; if False, require any one

    Usage:
        @bp.route('/admin/config', methods=['POST'])
        @permissions_required(['edit_config', 'manage_users'])
        def update_config():
            pass
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({"error": "Authentication required"}), 401

            # Superusers have all permissions
            if user.is_superuser:
                g.current_user = user
                return f(*args, **kwargs)

            # Check permissions
            checks = [_check_user_permission(user, perm) for perm in permission_names]

            if require_all:
                has_permission = all(checks)
            else:
                has_permission = any(checks)

            if not has_permission:
                return (
                    jsonify(
                        {
                            "error": "Insufficient permissions",
                            "required_permissions": permission_names,
                            "require_all": require_all,
                        }
                    ),
                    403,
                )

            g.current_user = user
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def org_permission_required(permission_name: str, org_id_param: str = "id") -> Callable:
    """
    Decorator to check organization-scoped permissions.

    Args:
        permission_name: Name of required permission
        org_id_param: Name of route parameter containing organization ID

    Usage:
        @bp.route('/organizations/<int:id>/entities', methods=['POST'])
        @org_permission_required('create_entity', org_id_param='id')
        def create_org_entity(id):
            # Create entity in organization
            pass
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({"error": "Authentication required"}), 401

            # Superusers have all permissions
            if user.is_superuser:
                g.current_user = user
                return f(*args, **kwargs)

            # Get organization ID from route params
            org_id = kwargs.get(org_id_param)

            if not org_id:
                return jsonify({"error": "Organization ID required"}), 400

            # Check if user has permission for this organization
            has_permission = _check_org_permission(user, permission_name, org_id)

            if not has_permission:
                return (
                    jsonify(
                        {
                            "error": "Insufficient permissions for this organization",
                            "required_permission": permission_name,
                            "organization_id": org_id,
                        }
                    ),
                    403,
                )

            g.current_user = user
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def _check_user_permission(user: Identity, permission_name: str) -> bool:
    """
    Check if user has a specific permission (global or org-scoped).

    Args:
        user: Identity instance
        permission_name: Permission name to check

    Returns:
        True if user has permission
    """
    # Get all user roles
    for user_role in user.roles:
        # Check if any role has the permission
        if user_role.role.has_permission(permission_name):
            return True

    return False


def _check_org_permission(user: Identity, permission_name: str, org_id: int) -> bool:
    """
    Check if user has permission for a specific organization.

    Args:
        user: Identity instance
        permission_name: Permission name to check
        org_id: Organization ID

    Returns:
        True if user has permission for this organization
    """
    from apps.api.models.rbac import RoleScope

    # Get all user roles
    for user_role in user.roles:
        # Check if role has the permission
        if not user_role.role.has_permission(permission_name):
            continue

        # Check scope
        if user_role.scope == RoleScope.GLOBAL:
            # Global permissions apply everywhere
            return True

        if user_role.scope == RoleScope.ORGANIZATION:
            # Organization-scoped: check if it applies to this org
            if user_role.applies_to_organization(org_id):
                return True

    return False


def resource_role_required(required_role: str, resource_param: str = "id") -> Callable:
    """
    Decorator to check resource-level role requirements.

    Checks if the current user has the required role (maintainer/operator/viewer)
    on the specific resource (entity or organization) being accessed.

    Role hierarchy: viewer < operator < maintainer
    - maintainer: Full CRUD, can manage roles
    - operator: Create/close issues, add comments/labels, read metadata
    - viewer: View, create issues, add comments

    Args:
        required_role: Minimum role required (viewer, operator, maintainer)
        resource_param: Name of route parameter containing resource ID

    Usage:
        @bp.route('/entities/<int:id>/metadata', methods=['POST'])
        @login_required
        @license_required('enterprise')
        @resource_role_required('maintainer', resource_param='id')
        def create_entity_metadata(id):
            # Only maintainers can create metadata
            pass

        @bp.route('/issues', methods=['POST'])
        @login_required
        @license_required('enterprise')
        @resource_role_required('viewer')
        def create_issue():
            # Viewers can create issues
            # Must provide entity_id or organization_id in request body
            pass
    """
    from apps.api.models.resource_role import ResourceRole, ResourceType, ResourceRoleType

    # Map string role names to enum
    role_map = {
        "viewer": ResourceRoleType.VIEWER,
        "operator": ResourceRoleType.OPERATOR,
        "maintainer": ResourceRoleType.MAINTAINER,
    }

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({"error": "Authentication required"}), 401

            # Superusers bypass resource role checks
            if user.is_superuser:
                g.current_user = user
                return f(*args, **kwargs)

            # Get resource ID and type
            resource_id = kwargs.get(resource_param)

            # If not in route params, check request body (for POST/PATCH)
            if not resource_id and request.is_json:
                data = request.get_json()
                if "entity_id" in data:
                    resource_id = data["entity_id"]
                    resource_type = ResourceType.ENTITY
                elif "organization_id" in data:
                    resource_id = data["organization_id"]
                    resource_type = ResourceType.ORGANIZATION
                else:
                    return jsonify({"error": "Resource ID required (entity_id or organization_id)"}), 400
            elif resource_id:
                # Determine resource type from route context
                # Check if we're in an entity or organization route
                if "/entities/" in request.path:
                    resource_type = ResourceType.ENTITY
                elif "/organizations/" in request.path:
                    resource_type = ResourceType.ORGANIZATION
                else:
                    # Can't determine resource type
                    return jsonify({"error": "Unable to determine resource type"}), 400
            else:
                return jsonify({"error": "Resource ID required"}), 400

            # Get required role enum
            required_role_enum = role_map.get(required_role)
            if not required_role_enum:
                return jsonify({"error": f"Invalid role: {required_role}"}), 500

            # Check if user has required role on this resource
            has_role = ResourceRole.check_permission(
                identity_id=user.id,
                resource_type=resource_type,
                resource_id=resource_id,
                required_role=required_role_enum,
            )

            if not has_role:
                return (
                    jsonify(
                        {
                            "error": "Insufficient permissions",
                            "message": f"This action requires '{required_role}' role on this resource",
                            "required_role": required_role,
                            "resource_type": resource_type.value,
                            "resource_id": resource_id,
                        }
                    ),
                    403,
                )

            g.current_user = user
            return f(*args, **kwargs)

        return decorated_function

    return decorator
