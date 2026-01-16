"""
Elder Pydantic 2 Base Models

This module provides foundational Pydantic 2 models for Elder applications,
with configuration standards for validation, serialization, and ORM integration.

Models:
    - ElderBaseModel: Base model with common Elder configuration
    - ImmutableModel: Immutable model for DTOs and responses
    - RequestModel: Model for API request validation with injection protection
    - ConfigurableModel: Flexible model with dynamic field support
"""

# flake8: noqa: E501


from typing import Any, Dict, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound="ElderBaseModel")


class ElderBaseModel(BaseModel):
    """
    Base Pydantic 2 model for Elder applications with standard configuration.

    Configuration includes:
    - validate_assignment: Validate field values when assigned
    - populate_by_name: Accept both field names and aliases during validation
    - use_enum_values: Serialize enum values as their actual values
    - from_attributes: Allow conversion from ORM objects and dataclasses
    - strict: Allow type coercion for common conversions (not strict mode)

    Methods:
        to_dict: Convert model to dictionary with control over None/unset values
        from_pydal_row: Convert PyDAL Row objects to model instances
    """

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
        strict=False,
    )

    def to_dict(
        self, exclude_none: bool = False, exclude_unset: bool = False, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that were not explicitly set
            **kwargs: Additional arguments passed to model_dump()

        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(
            exclude_none=exclude_none, exclude_unset=exclude_unset, **kwargs
        )

    @classmethod
    def from_pydal_row(cls: type[T], row: Any) -> T:
        """
        Convert a PyDAL Row object to a model instance.

        PyDAL Row objects represent database records with attribute access.
        This method safely converts None values and handles the row's dict representation.

        Args:
            row: PyDAL Row object from database query

        Returns:
            Model instance with data from the row

        Raises:
            ValidationError: If row data fails model validation

        Example:
            >>> from pydal import DAL
            >>> db = DAL('sqlite:memory:')
            >>> # ... assume table and row exist
            >>> model = MyModel.from_pydal_row(row)
        """
        # Convert PyDAL row to dictionary, handling None values
        row_dict = dict(row) if hasattr(row, "__iter__") else row.as_dict()
        # Filter out None values that may cause validation issues
        cleaned_dict = {
            k: v for k, v in row_dict.items() if v is not None or k in cls.model_fields
        }
        return cls(**cleaned_dict)


class ImmutableModel(ElderBaseModel):
    """
    Immutable Pydantic 2 model for data transfer objects and API responses.

    Once created, instances of this model cannot be modified, ensuring data
    integrity for DTOs and response objects. Inherits all configuration from
    ElderBaseModel and adds frozen=True constraint.

    Use Cases:
        - API response models
        - Data transfer objects (DTOs)
        - Cached/computed results
        - External API representations

    Example:
        >>> class UserResponse(ImmutableModel):
        ...     id: str
        ...     name: str
        ...     email: str
        >>> user = UserResponse(id="123", name="John", email="john@example.com")
        >>> user.name = "Jane"  # Raises ValidationError
    """

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
        strict=False,
        frozen=True,  # Immutable - prevents field assignment
        extra="forbid",  # Reject unknown fields for data integrity
    )


class RequestModel(ElderBaseModel):
    """
    Pydantic 2 model for API request validation with security hardening.

    Configuration includes all ElderBaseModel settings plus:
    - extra="forbid": Rejects unknown fields to prevent injection attacks
      and data pollution from client submissions

    Use this model for all incoming API requests to ensure strict validation
    and prevent clients from submitting unexpected fields that could bypass
    business logic or expose internal fields.

    Use Cases:
        - Request body validation
        - Query parameter validation
        - Form data validation
        - Any client-submitted data

    Example:
        >>> class CreateUserRequest(RequestModel):
        ...     name: str
        ...     email: str
        >>> # This will raise ValidationError due to unknown 'admin' field
        >>> CreateUserRequest(name="John", email="john@example.com", admin=True)
    """

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
        strict=False,
        extra="forbid",  # Reject unknown fields for security
    )


class ConfigurableModel(ElderBaseModel):
    """
    Flexible Pydantic 2 model with dynamic field support.

    Configuration includes all ElderBaseModel settings plus:
    - extra="allow": Accepts and stores additional fields beyond the schema
      definition, storing them in the model's __pydantic_extra__ dictionary

    Use this model for schemas that need to support dynamic or extension fields,
    such as configuration objects, flexible metadata structures, or extensible
    APIs that may receive additional fields from plugins or integrations.

    Use Cases:
        - Configuration objects with extension fields
        - Plugin/extension metadata
        - Flexible schema support
        - Dynamic field storage
        - Vendor-specific extensions

    Extra fields are accessible via model_extra property or direct iteration
    over model fields. When serializing with to_dict(), extra fields are
    included in the output.

    Example:
        >>> class Config(ConfigurableModel):
        ...     name: str
        ...     version: str
        >>> config = Config(name="app", version="1.0", custom_field="value")
        >>> config.custom_field  # Accessible via model_extra
        'value'
        >>> config.to_dict()
        {'name': 'app', 'version': '1.0', 'custom_field': 'value'}
    """

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
        strict=False,
        extra="allow",  # Allow and store extra fields
    )

    def to_dict(
        self, exclude_none: bool = False, exclude_unset: bool = False, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Convert model instance to dictionary, including extra fields.

        Overrides parent to_dict() to ensure extra fields (stored in
        __pydantic_extra__) are included in the output.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that were not explicitly set
            **kwargs: Additional arguments passed to model_dump()

        Returns:
            Dictionary representation including both defined and extra fields
        """
        result = self.model_dump(
            exclude_none=exclude_none, exclude_unset=exclude_unset, **kwargs
        )
        # Merge extra fields if present
        if self.__pydantic_extra__:
            result.update(self.__pydantic_extra__)
        return result
