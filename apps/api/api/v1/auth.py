"""Authentication API endpoints using PyDAL with async/await."""

import asyncio
from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from dataclasses import asdict

from apps.api.models.dataclasses import (
    IdentityDTO,
    LoginRequest,
    RegisterRequest,
    AuditLogDTO,
    from_pydal_row,
)
from apps.api.auth import generate_token, verify_password, login_required
from apps.api.auth.jwt_handler import verify_token
from shared.async_utils import run_in_threadpool

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
async def register():
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
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("username"):
        return jsonify({"error": "username is required"}), 400
    if not data.get("password"):
        return jsonify({"error": "password is required"}), 400
    if not data.get("email"):
        return jsonify({"error": "email is required"}), 400

    # Validate username length
    if len(data["username"]) < 3 or len(data["username"]) > 255:
        return jsonify({"error": "username must be between 3 and 255 characters"}), 400

    # Validate password length
    if len(data["password"]) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400

    # Check if username or email already exists and create user
    def create_user():
        # Check if username already exists
        existing = db(db.identities.username == data["username"]).select().first()
        if existing:
            return None, "Username already exists", 400

        # Check if email already exists
        existing_email = db(db.identities.email == data["email"]).select().first()
        if existing_email:
            return None, "Email already exists", 400

        # Create new identity
        identity_id = db.identities.insert(
            username=data["username"],
            email=data["email"],
            full_name=data.get("full_name"),
            identity_type="human",
            auth_provider="local",
            password_hash=generate_password_hash(data["password"]),
            is_active=True,
            is_superuser=False,
            mfa_enabled=False,
        )
        db.commit()

        # Get created identity
        identity = db.identities[identity_id]

        # Create audit log
        _create_audit_log_sync(
            db=db,
            identity_id=identity.id,
            action="create",
            resource_type="identity",
            resource_id=identity.id,
        )

        return identity, None, None

    identity, error, status = await run_in_threadpool(create_user)

    if error:
        return jsonify({"error": error}), status

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": identity.id,
            "username": identity.username,
            "email": identity.email,
        },
    }), 201


@bp.route("/login", methods=["POST"])
async def login():
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
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("username"):
        return jsonify({"error": "username is required"}), 400
    if not data.get("password"):
        return jsonify({"error": "password is required"}), 400

    # Find user and verify password
    def authenticate():
        identity = db(db.identities.username == data["username"]).select().first()

        if not identity:
            return None, "Invalid username or password", 401

        # Verify password using the identity row
        if not verify_password(identity, data["password"]):
            # Create failed login audit log
            _create_audit_log_sync(
                db=db,
                identity_id=identity.id,
                action="login",
                resource_type="auth",
                success=False,
            )
            return None, "Invalid username or password", 401

        # Check if account is active
        if not identity.is_active:
            return None, "Account is inactive", 401

        # Update last login
        db(db.identities.id == identity.id).update(
            last_login_at=datetime.now(timezone.utc)
        )
        db.commit()

        # Refresh identity data after update
        identity = db.identities[identity.id]

        # Create successful login audit log
        _create_audit_log_sync(
            db=db,
            identity_id=identity.id,
            action="login",
            resource_type="auth",
            success=True,
        )

        return identity, None, None

    identity, error, status = await run_in_threadpool(authenticate)

    if error:
        return jsonify({"error": error}), status

    # Generate tokens
    access_token = generate_token(identity, "access")
    refresh_token = generate_token(identity, "refresh")

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
async def logout():
    """
    Logout current user.

    Returns:
        200: Logout successful
    """
    db = current_app.db

    # Create logout audit log
    await run_in_threadpool(lambda: _create_audit_log_sync(
        db=db,
        identity_id=g.current_user.id,
        action="logout",
        resource_type="auth",
    ))

    return jsonify({"message": "Logged out successfully"}), 200


@bp.route("/me", methods=["GET"])
@login_required
async def get_current_user_info():
    """
    Get current authenticated user information.

    Returns:
        200: User information
    """
    db = current_app.db

    # Fetch fresh user data from database
    identity = await run_in_threadpool(lambda: db.identities[g.current_user.id])

    if not identity:
        return jsonify({"error": "User not found"}), 404

    identity_dto = from_pydal_row(identity, IdentityDTO)
    return jsonify(asdict(identity_dto)), 200


@bp.route("/change-password", methods=["POST"])
@login_required
async def change_password():
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
    db = current_app.db

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    if not data.get("current_password"):
        return jsonify({"error": "current_password is required"}), 400
    if not data.get("new_password"):
        return jsonify({"error": "new_password is required"}), 400

    # Validate new password length
    if len(data["new_password"]) < 8:
        return jsonify({"error": "new_password must be at least 8 characters"}), 400

    # Verify current password and update
    def update_password():
        identity = db.identities[g.current_user.id]

        if not identity:
            return None, "User not found", 404

        # Verify current password
        if not verify_password(identity, data["current_password"]):
            return None, "Current password is incorrect", 401

        # Update password
        db(db.identities.id == identity.id).update(
            password_hash=generate_password_hash(data["new_password"])
        )
        db.commit()

        # Create audit log
        _create_audit_log_sync(
            db=db,
            identity_id=identity.id,
            action="update",
            resource_type="identity",
            resource_id=identity.id,
            changes={"action": "password_change"},
        )

        return True, None, None

    result, error, status = await run_in_threadpool(update_password)

    if error:
        return jsonify({"error": error}), status

    return jsonify({"message": "Password changed successfully"}), 200


@bp.route("/refresh", methods=["POST"])
async def refresh_token_endpoint():
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
    db = current_app.db

    data = request.get_json() or {}
    refresh_token_str = data.get("refresh_token")

    if not refresh_token_str:
        return jsonify({"error": "Refresh token required"}), 400

    # Verify refresh token
    payload = verify_token(refresh_token_str)

    if not payload or payload.get("type") != "refresh":
        return jsonify({"error": "Invalid refresh token"}), 401

    # Get identity
    identity = await run_in_threadpool(lambda: db.identities[payload["sub"]])

    if not identity or not identity.is_active:
        return jsonify({"error": "User not found or inactive"}), 401

    # Generate new access token
    access_token = generate_token(identity, "access")

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
    }), 200


def _create_audit_log_sync(
    db,
    identity_id: int,
    action: str,
    resource_type: str,
    resource_id: int = None,
    success: bool = True,
    changes: dict = None,
):
    """
    Helper to create audit log entries (synchronous, call from threadpool).

    Args:
        db: PyDAL database instance
        identity_id: ID of identity performing action
        action: Audit action type (create, update, delete, login, logout, etc.)
        resource_type: Type of resource (identity, auth, entity, etc.)
        resource_id: ID of affected resource
        success: Whether action succeeded
        changes: Dict of changes made
    """
    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")[:512]

    # Convert boolean to string for PyDAL
    success_str = "true" if success else "false"

    db.audit_logs.insert(
        identity_id=identity_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=changes,  # PyDAL uses 'details' not 'changes'
        ip_address=ip_address,
        user_agent=user_agent,
        success=success_str,
    )
    db.commit()
