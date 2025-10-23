"""Identity and User management API endpoints."""

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from apps.api.models import Identity, IdentityGroup, IdentityGroupMembership
from apps.api.schemas.identity import (
    IdentitySchema,
    IdentityCreateSchema,
    IdentityUpdateSchema,
    IdentityListSchema,
    IdentityGroupSchema,
    IdentityGroupCreateSchema,
    IdentityGroupUpdateSchema,
)
from apps.api.auth import login_required, permission_required
from shared.database import db
from shared.api_utils import (
    paginate,
    get_pagination_params,
    validate_request,
    make_error_response,
    get_or_404,
    handle_validation_error,
)

bp = Blueprint("identities", __name__)


@bp.route("", methods=["GET"])
@login_required
@permission_required("view_users")
def list_identities():
    """
    List all identities with pagination.

    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 1000)
        - identity_type: Filter by type (human/service_account)
        - is_active: Filter by active status

    Returns:
        200: List of identities
    """
    pagination_params = get_pagination_params()

    # Build query
    query = Identity.query

    # Apply filters
    identity_type = request.args.get("identity_type")
    if identity_type:
        from apps.api.models.identity import IdentityType
        try:
            type_enum = IdentityType(identity_type)
            query = query.filter(Identity.identity_type == type_enum)
        except ValueError:
            return make_error_response(f"Invalid identity_type: {identity_type}", 400)

    is_active = request.args.get("is_active")
    if is_active is not None:
        query = query.filter(Identity.is_active == (is_active.lower() == "true"))

    # Order by username
    query = query.order_by(Identity.username)

    # Paginate
    items, pagination = paginate(
        query,
        page=pagination_params["page"],
        per_page=pagination_params["per_page"],
    )

    # Serialize
    schema = IdentitySchema(many=True)
    list_schema = IdentityListSchema()

    result = list_schema.dump({
        "items": schema.dump(items),
        **pagination,
    })

    return jsonify(result), 200


@bp.route("", methods=["POST"])
@login_required
@permission_required("manage_users")
def create_identity():
    """
    Create a new identity/user.

    Request Body:
        See IdentityCreateSchema

    Returns:
        201: Created identity
        400: Validation error
    """
    try:
        data = validate_request(IdentityCreateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Check if username exists
    existing = Identity.query.filter_by(username=data["username"]).first()
    if existing:
        return make_error_response("Username already exists", 400)

    # Convert type strings to enums
    from apps.api.models.identity import IdentityType, AuthProvider
    data["identity_type"] = IdentityType(data["identity_type"])
    data["auth_provider"] = AuthProvider(data["auth_provider"])

    # Hash password if provided (for local auth)
    if "password" in data:
        data["password_hash"] = generate_password_hash(data.pop("password"))

    # Create identity
    identity = Identity(**data)
    db.session.add(identity)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    schema = IdentitySchema()
    return jsonify(schema.dump(identity)), 201


@bp.route("/<int:id>", methods=["GET"])
@login_required
@permission_required("view_users")
def get_identity(id: int):
    """
    Get identity by ID.

    Path Parameters:
        - id: Identity ID

    Returns:
        200: Identity details
        404: Identity not found
    """
    identity = get_or_404(Identity, id)

    schema = IdentitySchema()
    return jsonify(schema.dump(identity)), 200


@bp.route("/<int:id>", methods=["PATCH", "PUT"])
@login_required
@permission_required("manage_users")
def update_identity(id: int):
    """
    Update identity.

    Path Parameters:
        - id: Identity ID

    Request Body:
        See IdentityUpdateSchema

    Returns:
        200: Updated identity
        400: Validation error
        404: Identity not found
    """
    identity = get_or_404(Identity, id)

    try:
        data = validate_request(IdentityUpdateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Update fields
    for key, value in data.items():
        setattr(identity, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    schema = IdentitySchema()
    return jsonify(schema.dump(identity)), 200


@bp.route("/<int:id>", methods=["DELETE"])
@login_required
@permission_required("manage_users")
def delete_identity(id: int):
    """
    Delete identity.

    Path Parameters:
        - id: Identity ID

    Returns:
        204: Identity deleted
        404: Identity not found
        400: Cannot delete own account or superuser
    """
    from flask import g

    identity = get_or_404(Identity, id)

    # Prevent deleting own account
    if identity.id == g.current_user.id:
        return make_error_response("Cannot delete your own account", 400)

    # Prevent deleting superusers (unless caller is also superuser)
    if identity.is_superuser and not g.current_user.is_superuser:
        return make_error_response("Cannot delete superuser account", 403)

    try:
        db.session.delete(identity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return "", 204


# Identity Groups endpoints

@bp.route("/groups", methods=["GET"])
@login_required
@permission_required("view_users")
def list_groups():
    """
    List all identity groups.

    Query Parameters:
        - page: Page number
        - per_page: Items per page

    Returns:
        200: List of groups
    """
    pagination_params = get_pagination_params()

    query = IdentityGroup.query.order_by(IdentityGroup.name)

    items, pagination = paginate(
        query,
        page=pagination_params["page"],
        per_page=pagination_params["per_page"],
    )

    schema = IdentityGroupSchema(many=True)
    return jsonify({
        "items": schema.dump(items),
        **pagination,
    }), 200


@bp.route("/groups", methods=["POST"])
@login_required
@permission_required("manage_users")
def create_group():
    """
    Create a new identity group.

    Request Body:
        See IdentityGroupCreateSchema

    Returns:
        201: Created group
    """
    try:
        data = validate_request(IdentityGroupCreateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    # Check if group name exists
    existing = IdentityGroup.query.filter_by(name=data["name"]).first()
    if existing:
        return make_error_response("Group name already exists", 400)

    group = IdentityGroup(**data)
    db.session.add(group)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    schema = IdentityGroupSchema()
    return jsonify(schema.dump(group)), 201


@bp.route("/groups/<int:id>", methods=["GET"])
@login_required
@permission_required("view_users")
def get_group(id: int):
    """Get identity group by ID."""
    group = get_or_404(IdentityGroup, id)

    schema = IdentityGroupSchema()
    return jsonify(schema.dump(group)), 200


@bp.route("/groups/<int:id>", methods=["PATCH", "PUT"])
@login_required
@permission_required("manage_users")
def update_group(id: int):
    """Update identity group."""
    group = get_or_404(IdentityGroup, id)

    try:
        data = validate_request(IdentityGroupUpdateSchema)
    except ValidationError as e:
        return handle_validation_error(e)

    for key, value in data.items():
        setattr(group, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    schema = IdentityGroupSchema()
    return jsonify(schema.dump(group)), 200


@bp.route("/groups/<int:id>", methods=["DELETE"])
@login_required
@permission_required("manage_users")
def delete_group(id: int):
    """Delete identity group."""
    group = get_or_404(IdentityGroup, id)

    try:
        db.session.delete(group)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return "", 204


@bp.route("/groups/<int:group_id>/members/<int:identity_id>", methods=["POST"])
@login_required
@permission_required("manage_users")
def add_group_member(group_id: int, identity_id: int):
    """
    Add identity to group.

    Path Parameters:
        - group_id: Group ID
        - identity_id: Identity ID

    Returns:
        200: Member added
        400: Already a member
    """
    group = get_or_404(IdentityGroup, group_id)
    identity = get_or_404(Identity, identity_id)

    # Check if already a member
    existing = IdentityGroupMembership.query.filter_by(
        group_id=group_id,
        identity_id=identity_id,
    ).first()

    if existing:
        return make_error_response("Identity is already a member of this group", 400)

    # Add membership
    membership = IdentityGroupMembership(group=group, identity=identity)
    db.session.add(membership)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return jsonify({"message": "Member added successfully"}), 200


@bp.route("/groups/<int:group_id>/members/<int:identity_id>", methods=["DELETE"])
@login_required
@permission_required("manage_users")
def remove_group_member(group_id: int, identity_id: int):
    """
    Remove identity from group.

    Returns:
        204: Member removed
        404: Not a member
    """
    membership = IdentityGroupMembership.query.filter_by(
        group_id=group_id,
        identity_id=identity_id,
    ).first()

    if not membership:
        return make_error_response("Identity is not a member of this group", 404)

    try:
        db.session.delete(membership)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Database error: {str(e)}", 500)

    return "", 204
