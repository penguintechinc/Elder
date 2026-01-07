"""Async validation utilities for Pydantic with PyDAL."""

from typing import Callable, Any
from pydantic import BaseModel
from shared.async_utils import run_in_threadpool


class AsyncValidator:
    """Registry for async validators that need DB lookups."""

    def __init__(self):
        """Initialize validator registry."""
        self._validators: dict[str, Callable] = {}

    def register(self, field_name: str):
        """Decorator to register async validators.

        Args:
            field_name: Name of the field to validate

        Returns:
            Decorator function
        """

        def decorator(func: Callable):
            self._validators[field_name] = func
            return func

        return decorator

    async def validate_model(
        self, model: BaseModel, db, **context
    ) -> list[dict[str, Any]]:
        """Run all registered validators on a model.

        Args:
            model: Pydantic model instance to validate
            db: PyDAL database instance
            **context: Additional context for validators

        Returns:
            List of error dicts with 'field' and 'message' keys
        """
        errors = []
        for field_name, validator in self._validators.items():
            if hasattr(model, field_name):
                value = getattr(model, field_name)
                try:
                    await validator(db, value, model, **context)
                except ValueError as e:
                    errors.append({"field": field_name, "message": str(e)})
        return errors


async def validate_foreign_key(
    table, value: int, resource_name: str = "Resource"
) -> None:
    """Validate foreign key exists in PyDAL table.

    Args:
        table: PyDAL table to check
        value: Foreign key value to validate
        resource_name: Resource name for error message

    Raises:
        ValueError: If foreign key does not exist
    """

    def _check():
        return table[value] is not None

    exists = await run_in_threadpool(_check)
    if not exists:
        raise ValueError(f"{resource_name} with id {value} does not exist")


async def validate_unique_field(
    table, field_name: str, value: Any, exclude_id: int | None = None
) -> None:
    """Validate field uniqueness in PyDAL table.

    Args:
        table: PyDAL table to check
        field_name: Name of field to check for uniqueness
        value: Value to check
        exclude_id: Optional ID to exclude from check (for updates)

    Raises:
        ValueError: If duplicate value found
    """

    def _check():
        query = table[field_name] == value
        if exclude_id is not None:
            query &= table.id != exclude_id
        return table(query).select().first()

    existing = await run_in_threadpool(_check)
    if existing:
        raise ValueError(f"{field_name} '{value}' already exists")
