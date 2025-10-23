"""Public lookup endpoint for entities by unique 64-bit ID."""

from flask import Blueprint, jsonify

from apps.api.models import Entity
from apps.api.schemas.entity import EntitySchema
from shared.api_utils import make_error_response

bp = Blueprint("lookup", __name__)


@bp.route("/<int:unique_id>", methods=["GET"])
def lookup_entity(unique_id: int):
    """
    Lookup entity by unique 64-bit identifier.

    Public endpoint - no authentication required.
    Returns entity type and details (not including children/dependencies).

    Path Parameters:
        - unique_id: Unique 64-bit entity identifier

    Returns:
        200: Entity details in JSON format
        404: Entity not found

    Example:
        GET /lookup/1234567890123456
        {
            "id": 42,
            "unique_id": 1234567890123456,
            "name": "Web Server 01",
            "description": "Primary web server",
            "entity_type": "compute",
            "organization_id": 1,
            "metadata": {
                "hostname": "web-01.example.com",
                "ip": "10.0.1.5",
                "os": "Ubuntu 22.04"
            },
            "created_at": "2024-10-23T10:00:00Z",
            "updated_at": "2024-10-23T15:30:00Z"
        }
    """
    # Find entity by unique_id
    entity = Entity.query.filter_by(unique_id=unique_id).first()

    if not entity:
        return make_error_response(
            f"Entity with unique_id {unique_id} not found",
            404,
        )

    # Serialize entity (without nested relationships to keep response simple)
    schema = EntitySchema(exclude=["organization", "owner"])
    return jsonify(schema.dump(entity)), 200


@bp.route("/batch", methods=["POST"])
def lookup_entities_batch():
    """
    Lookup multiple entities by unique IDs in a single request.

    Public endpoint - no authentication required.

    Request Body:
        {
            "unique_ids": [1234567890123456, 9876543210987654, ...]
        }

    Returns:
        200: Array of entity details (up to 100 entities)
        400: Invalid request

    Example:
        POST /lookup/batch
        {
            "unique_ids": [1234567890123456, 9876543210987654]
        }

        Response:
        {
            "results": [
                {
                    "unique_id": 1234567890123456,
                    "found": true,
                    "entity": { ... }
                },
                {
                    "unique_id": 9876543210987654,
                    "found": false,
                    "entity": null
                }
            ]
        }
    """
    from flask import request

    data = request.get_json() or {}

    if "unique_ids" not in data or not isinstance(data["unique_ids"], list):
        return make_error_response("Request must include 'unique_ids' array", 400)

    unique_ids = data["unique_ids"]

    if len(unique_ids) == 0:
        return make_error_response("At least one unique_id required", 400)

    if len(unique_ids) > 100:
        return make_error_response("Maximum 100 entities per batch lookup", 400)

    # Query all entities
    entities = Entity.query.filter(Entity.unique_id.in_(unique_ids)).all()

    # Build lookup map
    entity_map = {e.unique_id: e for e in entities}

    # Build response
    schema = EntitySchema(exclude=["organization", "owner"])
    results = []

    for uid in unique_ids:
        if uid in entity_map:
            results.append({
                "unique_id": uid,
                "found": True,
                "entity": schema.dump(entity_map[uid]),
            })
        else:
            results.append({
                "unique_id": uid,
                "found": False,
                "entity": None,
            })

    return jsonify({"results": results}), 200
