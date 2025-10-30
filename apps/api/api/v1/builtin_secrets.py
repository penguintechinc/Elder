"""REST API endpoints for built-in secrets management."""

from flask import Blueprint, request, jsonify
from apps.api.decorators.auth import login_required
from apps.api.services.secrets import BuiltinSecretsClient
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("builtin_secrets", __name__, url_prefix="/api/v1/builtin-secrets")


@bp.route("", methods=["GET"])
@login_required
def list_secrets():
    """List built-in secrets for an organization."""
    try:
        organization_id = request.args.get("organization_id", type=int)
        prefix = request.args.get("prefix")

        if not organization_id:
            return jsonify({"error": "organization_id parameter required"}), 400

        config = {"organization_id": organization_id}
        client = BuiltinSecretsClient(config)

        secrets = client.list_secrets(prefix=prefix)

        return jsonify({"secrets": [s.__dict__ for s in secrets]}), 200

    except Exception as e:
        logger.error(f"List built-in secrets error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route("/<path:secret_path>", methods=["GET"])
@login_required
def get_secret(secret_path):
    """Get a built-in secret by path."""
    try:
        organization_id = request.args.get("organization_id", type=int)

        if not organization_id:
            return jsonify({"error": "organization_id parameter required"}), 400

        config = {"organization_id": organization_id}
        client = BuiltinSecretsClient(config)

        secret = client.get_secret(secret_path)

        # Return masked by default
        return jsonify(secret.__dict__), 200

    except Exception as e:
        logger.error(f"Get built-in secret error: {str(e)}")
        if "not found" in str(e).lower():
            return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 500


@bp.route("", methods=["POST"])
@login_required
def create_secret():
    """Create a new built-in secret."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body required"}), 400

        required_fields = ["name", "value", "organization_id"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        config = {"organization_id": data["organization_id"]}
        client = BuiltinSecretsClient(config)

        metadata = {
            "description": data.get("description", ""),
            "secret_type": data.get("secret_type", "password"),
            "tags": data.get("tags", []),
            "expires_at": data.get("expires_at"),
        }

        secret_metadata = client.create_secret(
            path=data["name"],
            value=data["value"],
            metadata=metadata,
        )

        return jsonify(secret_metadata.__dict__), 201

    except Exception as e:
        logger.error(f"Create built-in secret error: {str(e)}")
        if "already exists" in str(e).lower():
            return jsonify({"error": str(e)}), 409
        return jsonify({"error": str(e)}), 500


@bp.route("/<path:secret_path>", methods=["PUT", "PATCH"])
@login_required
def update_secret(secret_path):
    """Update a built-in secret."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body required"}), 400

        organization_id = request.args.get("organization_id", type=int)

        if not organization_id:
            return jsonify({"error": "organization_id parameter required"}), 400

        if "value" not in data:
            return jsonify({"error": "Missing required field: value"}), 400

        config = {"organization_id": organization_id}
        client = BuiltinSecretsClient(config)

        secret_metadata = client.update_secret(
            path=secret_path,
            value=data["value"],
        )

        return jsonify(secret_metadata.__dict__), 200

    except Exception as e:
        logger.error(f"Update built-in secret error: {str(e)}")
        if "not found" in str(e).lower():
            return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 500


@bp.route("/<path:secret_path>", methods=["DELETE"])
@login_required
def delete_secret(secret_path):
    """Delete a built-in secret."""
    try:
        organization_id = request.args.get("organization_id", type=int)

        if not organization_id:
            return jsonify({"error": "organization_id parameter required"}), 400

        config = {"organization_id": organization_id}
        client = BuiltinSecretsClient(config)

        result = client.delete_secret(path=secret_path, force=False)

        return jsonify({"success": result, "path": secret_path}), 200

    except Exception as e:
        logger.error(f"Delete built-in secret error: {str(e)}")
        if "not found" in str(e).lower():
            return jsonify({"error": str(e)}), 404
        return jsonify({"error": str(e)}), 500


@bp.route("/test-connection", methods=["POST"])
@login_required
def test_connection():
    """Test built-in secrets database connection."""
    try:
        data = request.get_json() or {}
        organization_id = data.get("organization_id", 1)

        config = {"organization_id": organization_id}
        client = BuiltinSecretsClient(config)

        success = client.test_connection()

        return jsonify({"success": success, "provider": "builtin"}), 200

    except Exception as e:
        logger.error(f"Test built-in secrets connection error: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500
