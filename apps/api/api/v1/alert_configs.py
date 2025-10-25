"""API endpoints for managing per-organization alert configurations."""

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from apps.api.auth.decorators import login_required, resource_role_required
from apps.api.models.alert_config import AlertConfiguration, AlertDestinationType
from apps.api.models.organization import Organization
from shared.licensing import license_required

bp = Blueprint("alert_configs", __name__)


@bp.route("/organizations/<int:org_id>/alert-configs", methods=["GET"])
@login_required
@license_required("enterprise")
@resource_role_required("viewer", resource_param="org_id", resource_type="organization")
async def get_organization_alert_configs(org_id: int):
    """
    Get all alert configurations for an organization.

    Requires viewer role on the organization.

    Path Parameters:
        - org_id: Organization ID

    Returns:
        200: List of alert configurations
        403: License required or insufficient permissions
        404: Organization not found
    """
    db = current_app.db_session

    # Verify organization exists
    org = db.get(Organization, org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    # Get all alert configurations
    stmt = select(AlertConfiguration).where(
        AlertConfiguration.organization_id == org_id
    ).order_by(AlertConfiguration.created_at.desc())

    result = db.execute(stmt)
    configs = result.scalars().all()

    return jsonify({
        "items": [
            {
                "id": config.id,
                "organization_id": config.organization_id,
                "destination_type": config.destination_type.value,
                "name": config.name,
                "enabled": config.enabled,
                "config": config.config,
                "severity_filter": config.severity_filter,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat(),
            }
            for config in configs
        ],
        "total": len(configs),
    }), 200


@bp.route("/organizations/<int:org_id>/alert-configs", methods=["POST"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="org_id", resource_type="organization")
async def create_organization_alert_config(org_id: int):
    """
    Create a new alert configuration for an organization.

    Requires maintainer role on the organization.

    Path Parameters:
        - org_id: Organization ID

    Request Body:
        {
            "destination_type": "email|webhook|pagerduty|slack",
            "name": "Primary Email Alerts",
            "enabled": 1,
            "config": {
                // Destination-specific configuration
                // Email: {"to": ["email@example.com"], "cc": [], "subject_prefix": "[INCIDENT]"}
                // Webhook: {"url": "https://...", "headers": {}, "method": "POST"}
                // PagerDuty: {"service_key": "xxx", "urgency": "high"}
                // Slack: {"webhook_url": "https://hooks.slack.com/..."}
            },
            "severity_filter": ["high", "critical"] // Optional
        }

    Returns:
        201: Alert configuration created
        400: Invalid request
        403: License required or insufficient permissions
        404: Organization not found
    """
    db = current_app.db_session
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    required_fields = ['destination_type', 'name', 'config']
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Verify organization exists
    org = db.get(Organization, org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    # Validate destination type
    try:
        destination_type = AlertDestinationType(data['destination_type'])
    except ValueError:
        valid_types = [t.value for t in AlertDestinationType]
        return jsonify({"error": f"Invalid destination_type. Must be one of: {', '.join(valid_types)}"}), 400

    # Create alert configuration
    alert_config = AlertConfiguration(
        organization_id=org_id,
        destination_type=destination_type,
        name=data['name'],
        enabled=data.get('enabled', 1),
        config=data['config'],
        severity_filter=data.get('severity_filter'),
    )

    db.add(alert_config)
    db.commit()
    db.refresh(alert_config)

    return jsonify({
        "id": alert_config.id,
        "organization_id": alert_config.organization_id,
        "destination_type": alert_config.destination_type.value,
        "name": alert_config.name,
        "enabled": alert_config.enabled,
        "config": alert_config.config,
        "severity_filter": alert_config.severity_filter,
        "created_at": alert_config.created_at.isoformat(),
        "updated_at": alert_config.updated_at.isoformat(),
    }), 201


@bp.route("/organizations/<int:org_id>/alert-configs/<int:config_id>", methods=["PUT"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="org_id", resource_type="organization")
async def update_organization_alert_config(org_id: int, config_id: int):
    """
    Update an alert configuration.

    Requires maintainer role on the organization.

    Path Parameters:
        - org_id: Organization ID
        - config_id: Alert configuration ID

    Request Body:
        {
            "name": "Updated name",
            "enabled": 0,
            "config": {...},
            "severity_filter": ["critical"]
        }

    Returns:
        200: Alert configuration updated
        400: Invalid request
        403: License required or insufficient permissions
        404: Organization or configuration not found
    """
    db = current_app.db_session
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Get alert configuration
    config = db.get(AlertConfiguration, config_id)
    if not config or config.organization_id != org_id:
        return jsonify({"error": "Alert configuration not found"}), 404

    # Update fields
    if 'name' in data:
        config.name = data['name']
    if 'enabled' in data:
        config.enabled = data['enabled']
    if 'config' in data:
        config.config = data['config']
    if 'severity_filter' in data:
        config.severity_filter = data['severity_filter']

    db.commit()
    db.refresh(config)

    return jsonify({
        "id": config.id,
        "organization_id": config.organization_id,
        "destination_type": config.destination_type.value,
        "name": config.name,
        "enabled": config.enabled,
        "config": config.config,
        "severity_filter": config.severity_filter,
        "created_at": config.created_at.isoformat(),
        "updated_at": config.updated_at.isoformat(),
    }), 200


@bp.route("/organizations/<int:org_id>/alert-configs/<int:config_id>", methods=["DELETE"])
@login_required
@license_required("enterprise")
@resource_role_required("maintainer", resource_param="org_id", resource_type="organization")
async def delete_organization_alert_config(org_id: int, config_id: int):
    """
    Delete an alert configuration.

    Requires maintainer role on the organization.

    Path Parameters:
        - org_id: Organization ID
        - config_id: Alert configuration ID

    Returns:
        204: Alert configuration deleted
        403: License required or insufficient permissions
        404: Organization or configuration not found
    """
    db = current_app.db_session

    # Get alert configuration
    config = db.get(AlertConfiguration, config_id)
    if not config or config.organization_id != org_id:
        return jsonify({"error": "Alert configuration not found"}), 404

    db.delete(config)
    db.commit()

    return '', 204
