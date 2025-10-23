"""License validation decorators for Elder enterprise features."""

from functools import wraps
from flask import jsonify, abort
import structlog

from .client import get_license_client

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
        def wrapper(*args, **kwargs):
            client = get_license_client()
            validation = client.validate()

            # Check tier requirement
            if not client.check_tier(required_tier):
                logger.warning(
                    "license_tier_insufficient",
                    required_tier=required_tier,
                    current_tier=validation.tier,
                    endpoint=func.__name__,
                )

                return (
                    jsonify(
                        {
                            "error": "License Required",
                            "message": f"This feature requires a {required_tier} license",
                            "required_tier": required_tier,
                            "current_tier": validation.tier,
                            "upgrade_url": "https://penguintech.io/elder/pricing",
                        }
                    ),
                    403,
                )

            # License check passed
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
        def wrapper(*args, **kwargs):
            client = get_license_client()

            if not client.check_feature(feature_name):
                logger.warning(
                    "feature_not_entitled",
                    feature=feature_name,
                    endpoint=func.__name__,
                )

                return (
                    jsonify(
                        {
                            "error": "Feature Not Available",
                            "message": "This feature is not included in your license",
                            "required_feature": feature_name,
                            "upgrade_url": "https://penguintech.io/elder/pricing",
                        }
                    ),
                    403,
                )

            # Feature check passed
            return func(*args, **kwargs)

        return wrapper

    return decorator
