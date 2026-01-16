"""Flask integration for Pydantic 2 validation."""

# flake8: noqa: E501


import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar

from flask import Response, jsonify, request
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ValidationErrorResponse:
    """Standardized validation error response for Flask."""

    @staticmethod
    def from_pydantic_error(error: ValidationError) -> Tuple[Dict[str, Any], int]:
        """
        Convert Pydantic ValidationError to Flask response tuple.

        Args:
            error: Pydantic ValidationError instance

        Returns:
            Tuple of (error dict, status code)
        """
        # Log validation errors for debugging
        from flask import current_app, has_app_context

        if has_app_context() and current_app:
            current_app.logger.error(f"Validation error: {error.errors()}")

        validation_errors = []
        for err in error.errors():
            validation_errors.append(
                {
                    "field": ".".join(str(x) for x in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
            )

        return {
            "error": "Validation failed",
            "validation_errors": validation_errors,
        }, 400


def validate_body(model_class: Type[T]) -> T:
    """
    Validate request body against Pydantic model.

    Args:
        model_class: Pydantic model class to validate against

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    data = request.get_json()
    return model_class.model_validate(data)


def validate_query_params(model_class: Type[T]) -> T:
    """
    Validate query parameters against Pydantic model.

    Args:
        model_class: Pydantic model class to validate against

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    data = request.args.to_dict()
    return model_class.model_validate(data)


def validated_request(
    body_model: Optional[Type[BaseModel]] = None,
    query_model: Optional[Type[BaseModel]] = None,
) -> Callable:
    """
    Decorator that validates request body and/or query parameters.

    Injects validated models as 'body' and/or 'query' keyword arguments.

    Args:
        body_model: Optional Pydantic model for request body validation
        query_model: Optional Pydantic model for query parameter validation

    Returns:
        Decorated function with validation

    Example:
        @app.route('/users', methods=['POST'])
        @validated_request(body_model=CreateUserRequest, query_model=PaginationParams)
        def create_user(body: CreateUserRequest, query: PaginationParams):
            return {"user": body.model_dump(), "page": query.page}
    """

    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    if body_model:
                        kwargs["body"] = validate_body(body_model)
                    if query_model:
                        kwargs["query"] = validate_query_params(query_model)

                    return await func(*args, **kwargs)
                except ValidationError as e:
                    return ValidationErrorResponse.from_pydantic_error(e)

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    if body_model:
                        kwargs["body"] = validate_body(body_model)
                    if query_model:
                        kwargs["query"] = validate_query_params(query_model)

                    return func(*args, **kwargs)
                except ValidationError as e:
                    return ValidationErrorResponse.from_pydantic_error(e)

            return sync_wrapper

    return decorator


def model_response(
    model: BaseModel, status_code: int = 200, exclude_none: bool = True
) -> Tuple[Response, int]:
    """
    Convert Pydantic model to Flask JSON response.

    Args:
        model: Pydantic model instance to serialize
        status_code: HTTP status code (default: 200)
        exclude_none: Whether to exclude None values from output (default: True)

    Returns:
        Tuple of (Flask Response, status code)

    Example:
        @app.route('/users/<int:user_id>')
        def get_user(user_id: int):
            user = UserResponse(id=user_id, name="Alice", email="alice@example.com")
            return model_response(user)
    """
    from flask import has_app_context

    data = model.model_dump(exclude_none=exclude_none)

    # If we're in an app context, use jsonify for proper Flask Response
    if has_app_context():
        return jsonify(data), status_code

    # Otherwise, create a mock Response for testing
    response = Response()
    response.set_data(__import__("json").dumps(data))
    response.headers["Content-Type"] = "application/json"
    return response, status_code
