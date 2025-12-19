"""API v1 package for Elder."""

from flask import Blueprint

# Create main v1 blueprint
api_v1 = Blueprint("api_v1", __name__)

# Import routes to register them (will be created)
# This will be uncommented as we create each module
# from apps.api.api.v1 import organizations, entities, dependencies, identities, graph

# On-call rotations routes
from apps.api.api.v1 import on_call_rotations

api_v1.register_blueprint(on_call_rotations.bp, url_prefix="/on-call")
