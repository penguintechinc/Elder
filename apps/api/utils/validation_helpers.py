"""
Common validation utilities for Elder API.

This module provides reusable validation functions for common patterns
like organization/tenant validation, required field checks, etc.
"""

from flask import current_app
from typing import Tuple, Optional, Any
from shared.async_utils import run_in_threadpool
from .api_responses import ApiResponse


async def validate_organization_and_get_tenant(
    org_id: int,
) -> Tuple[Optional[Any], Optional[int], Optional[Tuple[Any, int]]]:
    """
    Validate that an organization exists and has a tenant assigned.

    Args:
        org_id: Organization ID to validate

    Returns:
        Tuple of (organization, tenant_id, error_response)
        - If validation succeeds: (org_row, tenant_id, None)
        - If validation fails: (None, None, (error_json, status_code))

    Usage:
        org, tenant_id, error = await validate_organization_and_get_tenant(org_id)
        if error:
            return error
        # Continue with org and tenant_id

    Example:
        org, tenant_id, error = await validate_organization_and_get_tenant(data["organization_id"])
        if error:
            return error
        # org and tenant_id are now available for use
    """
    db = current_app.db

    def get_org():
        return db.organizations[org_id]

    org = await run_in_threadpool(get_org)

    if not org:
        return None, None, ApiResponse.not_found("Organization", org_id)

    if not org.tenant_id:
        return None, None, ApiResponse.error("Organization must have a tenant", 400)

    return org, org.tenant_id, None


async def validate_tenant_exists(
    tenant_id: int,
) -> Tuple[Optional[Any], Optional[Tuple[Any, int]]]:
    """
    Validate that a tenant exists.

    Args:
        tenant_id: Tenant ID to validate

    Returns:
        Tuple of (tenant, error_response)
        - If validation succeeds: (tenant_row, None)
        - If validation fails: (None, (error_json, status_code))

    Usage:
        tenant, error = await validate_tenant_exists(tenant_id)
        if error:
            return error

    Example:
        tenant, error = await validate_tenant_exists(data["tenant_id"])
        if error:
            return error
    """
    db = current_app.db

    def get_tenant():
        return db.tenants[tenant_id]

    tenant = await run_in_threadpool(get_tenant)

    if not tenant:
        return None, ApiResponse.not_found("Tenant", tenant_id)

    return tenant, None


def validate_required_fields(
    data: dict, required_fields: list
) -> Optional[Tuple[Any, int]]:
    """
    Validate that all required fields are present in the data dict.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Error response tuple if validation fails, None if successful

    Usage:
        error = validate_required_fields(data, ["name", "type"])
        if error:
            return error

    Example:
        error = validate_required_fields(request_data, ["name", "organization_id"])
        if error:
            return error
    """
    for field in required_fields:
        if not data.get(field):
            return ApiResponse.validation_error(field, "is required")
    return None


def validate_json_body(data: Any) -> Optional[Tuple[Any, int]]:
    """
    Validate that request body contains JSON data.

    Args:
        data: Request data to validate (typically from request.get_json())

    Returns:
        Error response tuple if validation fails, None if successful

    Usage:
        data = request.get_json()
        error = validate_json_body(data)
        if error:
            return error

    Example:
        data = request.get_json()
        if error := validate_json_body(data):
            return error
    """
    if not data:
        return ApiResponse.bad_request("Request body must be JSON")
    return None


async def validate_resource_exists(
    table: Any, resource_id: int, resource_type: str = "Resource"
) -> Tuple[Optional[Any], Optional[Tuple[Any, int]]]:
    """
    Validate that a resource exists in a PyDAL table.

    Args:
        table: PyDAL table object
        resource_id: ID of resource to validate
        resource_type: Human-readable name of resource type (for error message)

    Returns:
        Tuple of (resource, error_response)
        - If validation succeeds: (resource_row, None)
        - If validation fails: (None, (error_json, status_code))

    Usage:
        resource, error = await validate_resource_exists(db.entities, entity_id, "Entity")
        if error:
            return error

    Example:
        entity, error = await validate_resource_exists(db.entities, id, "Entity")
        if error:
            return error
    """

    def get_resource():
        return table[resource_id]

    resource = await run_in_threadpool(get_resource)

    if not resource:
        return None, ApiResponse.not_found(resource_type, resource_id)

    return resource, None


def validate_pagination_params(
    page: int, per_page: int, max_per_page: int = 1000
) -> Optional[Tuple[Any, int]]:
    """
    Validate pagination parameters.

    Args:
        page: Page number (must be >= 1)
        per_page: Items per page (must be >= 1 and <= max_per_page)
        max_per_page: Maximum allowed per_page value (default: 1000)

    Returns:
        Error response tuple if validation fails, None if successful

    Usage:
        error = validate_pagination_params(page, per_page)
        if error:
            return error

    Example:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        if error := validate_pagination_params(page, per_page):
            return error
    """
    if page < 1:
        return ApiResponse.bad_request("Page must be >= 1")

    if per_page < 1:
        return ApiResponse.bad_request("per_page must be >= 1")

    if per_page > max_per_page:
        return ApiResponse.bad_request(f"per_page must be <= {max_per_page}")

    return None


def validate_enum_value(
    value: str, allowed_values: list, field_name: str = "value"
) -> Optional[Tuple[Any, int]]:
    """
    Validate that a value is in a list of allowed values (enum validation).

    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Name of field (for error message)

    Returns:
        Error response tuple if validation fails, None if successful

    Usage:
        error = validate_enum_value(status, ["active", "inactive"], "status")
        if error:
            return error

    Example:
        error = validate_enum_value(
            data.get("status"),
            ["active", "inactive", "archived"],
            "status"
        )
        if error:
            return error
    """
    if value not in allowed_values:
        allowed_str = ", ".join(allowed_values)
        return ApiResponse.bad_request(f"{field_name} must be one of: {allowed_str}")
    return None
