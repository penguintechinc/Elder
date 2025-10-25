"""JWT token handling for Elder authentication using PyDAL."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import wraps

import jwt
from flask import request, current_app, g
from werkzeug.security import check_password_hash
from pydal.objects import Row


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
        "sub": identity.id,
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

        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_header() -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Returns:
        Token string or None
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def get_current_user() -> Optional[Row]:
    """
    Get current authenticated user from request context.

    Returns:
        PyDAL Row representing identity or None
    """
    if hasattr(g, "current_user"):
        return g.current_user

    token = get_token_from_header()
    if not token:
        return None

    payload = verify_token(token)
    if not payload:
        return None

    db = current_app.db
    identity = db.identities[payload["sub"]]

    if identity and identity.is_active:
        g.current_user = identity
        return identity

    return None


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
