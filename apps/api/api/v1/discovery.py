"""Cloud Auto-Discovery API endpoints for Elder v1.2.0 (Phase 5)."""

import logging

from flask import Blueprint, current_app, jsonify, request

from apps.api.auth.decorators import admin_required, login_required
from apps.api.logging_config import log_error_and_respond
from apps.api.services.discovery import DiscoveryService

logger = logging.getLogger(__name__)

bp = Blueprint("discovery", __name__)


def get_discovery_service():
    """Get DiscoveryService instance with current database."""
    return DiscoveryService(current_app.db)


# Discovery Jobs endpoints


@bp.route("/jobs", methods=["GET"])
@login_required
def list_discovery_jobs():
    """
    List all discovery jobs.

    Query params:
        - provider: Filter by cloud provider (aws, gcp, azure, kubernetes)
        - enabled: Filter by enabled status
        - organization_id: Filter by organization

    Returns:
        200: List of discovery jobs
    """
    try:
        service = get_discovery_service()

        provider = request.args.get("provider")
        enabled = request.args.get("enabled")
        organization_id = request.args.get("organization_id", type=int)

        # Convert enabled string to boolean
        enabled_bool = None
        if enabled is not None:
            enabled_bool = enabled.lower() == "true"

        jobs = service.list_jobs(
            provider=provider, enabled=enabled_bool, organization_id=organization_id
        )

        return jsonify({"jobs": jobs, "count": len(jobs)}), 200

    except Exception as e:
        return log_error_and_respond(logger, e, "Failed to process request", 500)


@bp.route("/jobs", methods=["POST"])
@admin_required
def create_discovery_job():
    """
    Create a new discovery job.

    Request body:
        {
            "name": "AWS Production Discovery",
            "provider": "aws",
            "config": {
                "region": "us-east-1",
                "access_key_id": "...",
                "secret_access_key": "...",
                "services": ["ec2", "rds", "s3"]
            },
            "organization_id": 1,
            "schedule_interval": 3600,
            "description": "Discover AWS production resources"
        }

    Returns:
        201: Job created
        400: Invalid request
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body required"}), 400

        required = ["name", "provider", "config", "organization_id"]
        missing = [f for f in required if f not in data]
        if missing:
            return (
                jsonify({"error": f'Missing required fields: {", ".join(missing)}'}),
                400,
            )

        service = get_discovery_service()
        job = service.create_job(
            name=data["name"],
            provider=data["provider"],
            config=data["config"],
            organization_id=data["organization_id"],
            schedule_interval=data.get("schedule_interval"),
            description=data.get("description"),
        )

        return jsonify(job), 201

    except Exception as e:
        return log_error_and_respond(logger, e, "Failed to process request", 400)


@bp.route("/jobs/<int:job_id>", methods=["GET"])
@login_required
def get_discovery_job(job_id):
    """
    Get discovery job details.

    Returns:
        200: Job details
        404: Job not found
    """
    try:
        service = get_discovery_service()
        job = service.get_job(job_id)
        return jsonify(job), 200

    except Exception as e:
        if "not found" in str(e).lower():
            return log_error_and_respond(logger, e, "Failed to process request", 404)
        return log_error_and_respond(logger, e, "Failed to process request", 500)


@bp.route("/jobs/<int:job_id>", methods=["PUT"])
@admin_required
def update_discovery_job(job_id):
    """
    Update discovery job configuration.

    Request body (all optional):
        {
            "name": "Updated Name",
            "config": {...},
            "schedule_interval": 7200,
            "description": "Updated description",
            "enabled": false
        }

    Returns:
        200: Job updated
        404: Job not found
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body required"}), 400

        service = get_discovery_service()
        job = service.update_job(
            job_id=job_id,
            name=data.get("name"),
            config=data.get("config"),
            schedule_interval=data.get("schedule_interval"),
            description=data.get("description"),
            enabled=data.get("enabled"),
        )

        return jsonify(job), 200

    except Exception as e:
        if "not found" in str(e).lower():
            return log_error_and_respond(logger, e, "Failed to process request", 404)
        return log_error_and_respond(logger, e, "Failed to process request", 400)


@bp.route("/jobs/<int:job_id>", methods=["DELETE"])
@admin_required
def delete_discovery_job(job_id):
    """
    Delete discovery job.

    Returns:
        200: Job deleted
        404: Job not found
    """
    try:
        service = get_discovery_service()
        result = service.delete_job(job_id)
        return jsonify(result), 200

    except Exception as e:
        if "not found" in str(e).lower():
            return log_error_and_respond(logger, e, "Failed to process request", 404)
        return log_error_and_respond(logger, e, "Failed to process request", 500)


@bp.route("/jobs/<int:job_id>/test", methods=["POST"])
@login_required
def test_discovery_job(job_id):
    """
    Test discovery job connectivity.

    Returns:
        200: Test result
        404: Job not found
    """
    try:
        service = get_discovery_service()
        result = service.test_job(job_id)
        return jsonify(result), 200

    except Exception as e:
        if "not found" in str(e).lower():
            return log_error_and_respond(logger, e, "Failed to process request", 404)
        return log_error_and_respond(logger, e, "Failed to process request", 500)


@bp.route("/jobs/<int:job_id>/run", methods=["POST"])
@admin_required
def run_discovery_job(job_id):
    """
    Manually trigger a discovery job.

    Returns:
        202: Job started
        404: Job not found
    """
    try:
        service = get_discovery_service()
        result = service.run_discovery(job_id)

        status_code = 202 if result.get("success") else 500
        return jsonify(result), status_code

    except Exception as e:
        if "not found" in str(e).lower():
            return log_error_and_respond(logger, e, "Failed to process request", 404)
        return log_error_and_respond(logger, e, "Failed to process request", 500)


@bp.route("/jobs/<int:job_id>/history", methods=["GET"])
@login_required
def get_discovery_job_history(job_id):
    """
    Get discovery job execution history.

    Query params:
        - limit: Number of history entries (default: 50)

    Returns:
        200: Job history
    """
    try:
        service = get_discovery_service()

        limit = request.args.get("limit", 50, type=int)

        history = service.get_discovery_history(job_id=job_id, limit=limit)

        return jsonify({"history": history, "count": len(history)}), 200

    except Exception as e:
        return log_error_and_respond(logger, e, "Failed to process request", 500)


@bp.route("/history", methods=["GET"])
@login_required
def get_all_discovery_history():
    """
    Get all discovery execution history.

    Query params:
        - limit: Number of history entries (default: 50)

    Returns:
        200: Discovery history
    """
    try:
        service = get_discovery_service()

        limit = request.args.get("limit", 50, type=int)

        history = service.get_discovery_history(limit=limit)

        return jsonify({"history": history, "count": len(history)}), 200

    except Exception as e:
        return log_error_and_respond(logger, e, "Failed to process request", 500)
