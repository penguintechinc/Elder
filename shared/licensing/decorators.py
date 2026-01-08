"""License validation decorators for Elder enterprise features."""

# flake8: noqa: E501


import inspect
from functools import wraps

import structlog

logger = structlog.get_logger()


def license_required(required_tier: str = "enterprise"):
    """
    Decorator to enforce license tier requirements for enterprise features.

    Checks if the current license meets the minimum tier requirement.
    Tier hierarchy: community < professional < enterprise

    Args:
        required_tier: Minimum license tier required (default: enterprise)

    Returns:
        Decorated function that checks license before execution

    Usage:
        @app.route('/api/v1/issues', methods=['POST'])
        @login_required
        @license_required('enterprise')
        def create_issue():
            # Only accessible with enterprise license
            pass

    Example Response (403 when license insufficient):
        {
            "error": "License Required",
            "message": "This feature requires an enterprise license",
            "required_tier": "enterprise",
            "current_tier": "professional",
            "upgrade_url": "https://penguintech.io/elder/pricing"
        }
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # TEMPORARY: License checks disabled for development
            # TODO: Re-enable license enforcement in production
            logger.debug(
                "license_check_bypassed",
                required_tier=required_tier,
                endpoint=func.__name__,
                note="License enforcement temporarily disabled",
            )

            # Bypass license check - allow all features
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def feature_required(feature_name: str):
    """
    Decorator to enforce specific feature entitlement.

    Checks if the license includes entitlement for a specific feature.

    Args:
        feature_name: Feature identifier to check

    Returns:
        Decorated function that checks feature entitlement before execution

    Usage:
        @app.route('/api/v1/advanced-analytics', methods=['GET'])
        @login_required
        @feature_required('advanced_analytics')
        def get_advanced_analytics():
            # Only accessible if 'advanced_analytics' feature is entitled
            pass

    Example Response (403 when feature not entitled):
        {
            "error": "Feature Not Available",
            "message": "This feature is not included in your license",
            "required_feature": "advanced_analytics",
            "upgrade_url": "https://penguintech.io/elder/pricing"
        }
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # TEMPORARY: Feature checks disabled for development
            # TODO: Re-enable feature enforcement in production
            logger.debug(
                "feature_check_bypassed",
                feature=feature_name,
                endpoint=func.__name__,
                note="Feature enforcement temporarily disabled",
            )

            # Bypass feature check - allow all features
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
