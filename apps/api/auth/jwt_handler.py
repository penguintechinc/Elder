"""JWT token handling for Elder authentication using PyDAL."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import wraps
import logging

import jwt
from flask import request, current_app, g
from werkzeug.security import check_password_hash
from pydal.objects import Row

logger = logging.getLogger(__name__)


def generate_token(identity: Row, token_type: str = "access") -> str:
    """
    Generate JWT token for an identity.

    Args:
        identity: Identity model instance
        token_type: 'access' or 'refresh'

    Returns:
        JWT token string
    """
    if token_type == "access":
        expires_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    else:
        expires_delta = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(identity.id),  # JWT spec requires sub to be a string
        "username": identity.username,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }

    secret = current_app.config["JWT_SECRET_KEY"] or current_app.config["SECRET_KEY"]
    algorithm = current_app.config["JWT_ALGORITHM"]

    token = jwt.encode(payload, secret, algorithm=algorithm)
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        secret = current_app.config["JWT_SECRET_KEY"] or current_app.config["SECRET_KEY"]
        algorithm = current_app.config["JWT_ALGORITHM"]

        logger.debug(f"Verifying token with algorithm {algorithm}")
        logger.debug(f"Token (first 20 chars): {token[:20]}...")
        logger.debug(f"Using secret key: {secret[:10]}..." if secret else "No secret key!")

        payload = jwt.decode(token, secret, algorithms=[algorithm])
        logger.debug(f"Token verified successfully. Payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.warning(f"Token expired: {e}")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def get_token_from_header() -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Returns:
        Token string or None
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        logger.debug("No Authorization header found")
        return None

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.debug(f"Invalid Authorization header format: {auth_header}")
        return None

    token = parts[1]
    logger.debug(f"Extracted token from header (first 20 chars): {token[:20]}...")
    return token


def get_current_user() -> Optional[Row]:
    """
    Get current authenticated user from request context.

    Returns:
        PyDAL Row representing identity or None
    """
    logger.debug("=== get_current_user called ===")

    if hasattr(g, "current_user"):
        logger.debug(f"Returning cached user: {g.current_user.username}")
        return g.current_user

    token = get_token_from_header()
    if not token:
        logger.debug("No token found in header, returning None")
        return None

    payload = verify_token(token)
    if not payload:
        logger.debug("Token verification failed, returning None")
        return None

    logger.debug(f"Token verified, looking up user with ID: {payload.get('sub')}")
    db = current_app.db
    user_id = int(payload["sub"])  # Convert string back to integer
    identity = db.identities[user_id]

    if not identity:
        logger.warning(f"User not found in database with ID: {payload.get('sub')}")
        return None

    if not identity.is_active:
        logger.warning(f"User {identity.username} is not active")
        return None

    logger.debug(f"Authentication successful for user: {identity.username}")
    g.current_user = identity
    return identity


def verify_password(identity: Row, password: str) -> bool:
    """
    Verify password for local authentication.

    Args:
        identity: PyDAL Row representing identity
        password: Plain text password

    Returns:
        True if password is correct
    """
    if not identity.password_hash:
        return False

    return check_password_hash(identity.password_hash, password)
