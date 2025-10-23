"""Authentication API endpoints."""

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime, timezone

from apps.api.models import Identity, AuditLog
from apps.api.models.identity import IdentityType, AuthProvider
from apps.api.models.audit import AuditAction, AuditResourceType
from apps.api.auth import generate_token, verify_password, get_current_user, login_required
from shared.database import db
from shared.api_utils import make_error_response, handle_validation_error

bp = Blueprint("auth", __name__)


class LoginSchema(Schema):
    """Schema for login request."""

    username = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=1))


class RegisterSchema(Schema):
    """Schema for user registration."""

    username = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=255))
    email = fields.Email(required=True)
    full_name = fields.Str(allow_none=True, validate=validate.Length(max=255))


class ChangePasswordSchema(Schema):
    """Schema for password change."""

    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=255))


@bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user (local authentication).

    Request Body:
        {
            "username": "string",
            "password": "string",
            "email": "string",
            "full_name": "string" (optional)
        }

    Returns:
        201: User created successfully
        400: Validation error or username already exists
    """
    try:
        schema = RegisterSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return handle_validation_error(e)

    # Check if username already exists
    existing = Identity.query.filter_by(username=data["username"]).first()
    if existing:
        return make_error_response("Username already exists", 400)

    # Check if email already exists
    existing_email = Identity.query.filter_by(email=data["email"]).first()
    if existing_email:
        return make_error_response("Email already exists", 400)

    # Create new identity
    identity = Identity(
        username=data["username"],
        email=data["email"],
        full_name=data.get("full_name"),
        identity_type=IdentityType.HUMAN,
        auth_provider=AuthProvider.LOCAL,
        password_hash=generate_password_hash(data["password"]),
        is_active=True,
        is_superuser=False,
    )

    db.session.add(identity)

    try:
        db.session.commit()

        # Create audit log
        _create_audit_log(
            identity_id=identity.id,
            action=AuditAction.CREATE,
            resource_type=AuditResourceType.IDENTITY,
            resource_id=identity.id,
        )

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": identity.id,
                "username": identity.username,
                "email": identity.email,
            },
        }), 201

    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Registration failed: {str(e)}", 500)


@bp.route("/login", methods=["POST"])
def login():
    """
    Login with username and password.

    Request Body:
        {
            "username": "string",
            "password": "string"
        }

    Returns:
        200: Login successful with access and refresh tokens
        401: Invalid credentials
    """
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return handle_validation_error(e)

    # Find user
    identity = Identity.query.filter_by(username=data["username"]).first()

    if not identity or not verify_password(identity, data["password"]):
        # Create failed login audit log (if identity exists)
        if identity:
            _create_audit_log(
                identity_id=identity.id,
                action=AuditAction.LOGIN,
                resource_type=AuditResourceType.AUTH,
                success=False,
            )

        return make_error_response("Invalid username or password", 401)

    # Check if account is active
    if not identity.is_active:
        return make_error_response("Account is inactive", 401)

    # Generate tokens
    access_token = generate_token(identity, "access")
    refresh_token = generate_token(identity, "refresh")

    # Update last login
    identity.last_login_at = datetime.now(timezone.utc).isoformat()
    db.session.commit()

    # Create successful login audit log
    _create_audit_log(
        identity_id=identity.id,
        action=AuditAction.LOGIN,
        resource_type=AuditResourceType.AUTH,
        success=True,
    )

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": {
            "id": identity.id,
            "username": identity.username,
            "email": identity.email,
            "full_name": identity.full_name,
            "is_superuser": identity.is_superuser,
        },
    }), 200


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Logout current user.

    Returns:
        200: Logout successful
    """
    from flask import g

    # Create logout audit log
    _create_audit_log(
        identity_id=g.current_user.id,
        action=AuditAction.LOGOUT,
        resource_type=AuditResourceType.AUTH,
    )

    return jsonify({"message": "Logged out successfully"}), 200


@bp.route("/me", methods=["GET"])
@login_required
def get_current_user_info():
    """
    Get current authenticated user information.

    Returns:
        200: User information
    """
    from flask import g
    from apps.api.schemas.identity import IdentitySchema

    schema = IdentitySchema()
    return jsonify(schema.dump(g.current_user)), 200


@bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """
    Change current user's password.

    Request Body:
        {
            "current_password": "string",
            "new_password": "string"
        }

    Returns:
        200: Password changed successfully
        400: Validation error
        401: Current password incorrect
    """
    from flask import g

    try:
        schema = ChangePasswordSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return handle_validation_error(e)

    identity = g.current_user

    # Verify current password
    if not verify_password(identity, data["current_password"]):
        return make_error_response("Current password is incorrect", 401)

    # Update password
    identity.password_hash = generate_password_hash(data["new_password"])

    try:
        db.session.commit()

        # Create audit log
        _create_audit_log(
            identity_id=identity.id,
            action=AuditAction.UPDATE,
            resource_type=AuditResourceType.IDENTITY,
            resource_id=identity.id,
            changes={"action": "password_change"},
        )

        return jsonify({"message": "Password changed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return make_error_response(f"Failed to change password: {str(e)}", 500)


@bp.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Refresh access token using refresh token.

    Request Body:
        {
            "refresh_token": "string"
        }

    Returns:
        200: New access token
        401: Invalid refresh token
    """
    from apps.api.auth.jwt_handler import verify_token

    data = request.get_json() or {}
    refresh_token_str = data.get("refresh_token")

    if not refresh_token_str:
        return make_error_response("Refresh token required", 400)

    # Verify refresh token
    payload = verify_token(refresh_token_str)

    if not payload or payload.get("type") != "refresh":
        return make_error_response("Invalid refresh token", 401)

    # Get identity
    identity = db.session.get(Identity, payload["sub"])

    if not identity or not identity.is_active:
        return make_error_response("User not found or inactive", 401)

    # Generate new access token
    access_token = generate_token(identity, "access")

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
    }), 200


def _create_audit_log(
    identity_id: int,
    action: AuditAction,
    resource_type: AuditResourceType,
    resource_id: int = None,
    success: bool = True,
    changes: dict = None,
):
    """
    Helper to create audit log entries.

    Args:
        identity_id: ID of identity performing action
        action: Audit action type
        resource_type: Type of resource
        resource_id: ID of affected resource
        success: Whether action succeeded
        changes: Dict of changes made
    """
    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")[:512]

    audit = AuditLog(
        identity_id=identity_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        success="true" if success else "false",
    )

    db.session.add(audit)
    db.session.commit()
