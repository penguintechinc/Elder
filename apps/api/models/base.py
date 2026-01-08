"""Base models and mixins for Elder database models."""
# flake8: noqa: E501


from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps."""

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class IDMixin:
    """Mixin for adding auto-incrementing integer primary key."""

    id = Column(Integer, primary_key=True, autoincrement=True)


def to_dict(obj: Any, exclude: list = None) -> Dict[str, Any]:
    """
    Convert SQLAlchemy model instance to dictionary.

    Args:
        obj: SQLAlchemy model instance
        exclude: List of column names to exclude from the result

    Returns:
        Dictionary representation of the model
    """
    exclude = exclude or []
    result = {}

    for column in obj.__table__.columns:
        if column.name in exclude:
            continue

        value = getattr(obj, column.name)

        # Convert datetime objects to ISO format strings
        if isinstance(value, datetime):
            value = value.isoformat()

        result[column.name] = value

    return result
