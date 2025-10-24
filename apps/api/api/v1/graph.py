"""Graph visualization API endpoints for dependency mapping."""

from flask import Blueprint, request, jsonify
from typing import Dict, List, Set, Any
import networkx as nx

from apps.api.models import Entity, Dependency, Organization
from apps.api.schemas.entity import EntitySchema
from apps.api.schemas.dependency import DependencySchema
from shared.database import db
from shared.api_utils import make_error_response, get_or_404

bp = Blueprint("graph", __name__)


@bp.route("", methods=["GET"])
def get_graph():
    """
    Get full dependency graph or filtered subgraph.

    Query Parameters:
        - organization_id: Filter by organization
        - entity_type: Filter by entity type
        - entity_id: Center graph on specific entity
        - depth: Maximum depth from entity_id (default: 2, -1 for all)
        - include_metadata: Include entity metadata (default: false)

    Returns:
        200: Graph data in vis.js compatible format
        {
            "nodes": [{"id": 1, "label": "Entity Name", "type": "compute", ...}],
            "edges": [{"from": 1, "to": 2, "type": "depends_on", ...}]
        }
    """
    # Get filter parameters
    org_id = request.args.get("organization_id", type=int)
    entity_type = request.args.get("entity_type")
    entity_id = request.args.get("entity_id", type=int)
    depth = request.args.get("depth", 2, type=int)
    include_metadata = request.args.get("include_metadata", "false").lower() == "true"

    # Build entity query
    entity_query = db.session.query(Entity)

    if org_id:
        entity_query = entity_query.filter(Entity.organization_id == org_id)

    if entity_type:
        from apps.api.models.entity import EntityType
        try:
            entity_type_enum = EntityType(entity_type)
            entity_query = entity_query.filter(Entity.entity_type == entity_type_enum)
        except ValueError:
            return make_error_response(f"Invalid entity_type: {entity_type}", 400)

    # If entity_id specified, get subgraph centered on that entity
    if entity_id:
        entity = get_or_404(Entity, entity_id)
        entities = _get_entity_subgraph(entity, depth)
    else:
        # Get all entities matching filters
        entities = entity_query.all()

    # Get entity IDs for dependency filtering
    entity_ids = {e.id for e in entities}

    # Get dependencies between these entities
    dependencies = db.session.query(Dependency).filter(
        Dependency.source_entity_id.in_(entity_ids),
        Dependency.target_entity_id.in_(entity_ids),
    ).all()

    # Build vis.js compatible graph data
    nodes = []
    for entity in entities:
        node = {
            "id": entity.id,
            "label": entity.name,
            "type": entity.entity_type.value,
            "organization_id": entity.organization_id,
        }

        if include_metadata and entity.metadata:
            node["metadata"] = entity.metadata

        # Add visual styling based on entity type
        node["shape"], node["color"] = _get_node_style(entity.entity_type.value)

        nodes.append(node)

    edges = []
    for dep in dependencies:
        edge = {
            "id": dep.id,
            "from": dep.source_entity_id,
            "to": dep.target_entity_id,
            "type": dep.dependency_type.value,
            "arrows": "to",
        }

        # Add visual styling based on dependency type
        edge["color"], edge["dashes"] = _get_edge_style(dep.dependency_type.value)

        edges.append(edge)

    return jsonify({
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "entity_count": len(entities),
            "dependency_count": len(dependencies),
        }
    }), 200


@bp.route("/analyze", methods=["GET"])
def analyze_graph():
    """
    Analyze dependency graph and return insights.

    Query Parameters:
        - organization_id: Filter by organization

    Returns:
        200: Graph analysis metrics
    """
    org_id = request.args.get("organization_id", type=int)

    # Build query
    entity_query = db.session.query(Entity)
    if org_id:
        entity_query = entity_query.filter(Entity.organization_id == org_id)

    entities = entity_query.all()
    entity_ids = {e.id for e in entities}

    dependencies = db.session.query(Dependency).filter(
        Dependency.source_entity_id.in_(entity_ids),
        Dependency.target_entity_id.in_(entity_ids),
    ).all()

    # Build NetworkX graph for analysis
    G = nx.DiGraph()

    for entity in entities:
        G.add_node(entity.id, **{
            "name": entity.name,
            "type": entity.entity_type.value,
        })

    for dep in dependencies:
        G.add_edge(dep.source_entity_id, dep.target_entity_id)

    # Calculate metrics
    analysis = {
        "basic_stats": {
            "total_entities": len(entities),
            "total_dependencies": len(dependencies),
            "entities_by_type": _count_by_type(entities),
        },
        "graph_metrics": {
            "density": nx.density(G) if len(entities) > 1 else 0,
            "is_directed_acyclic": nx.is_directed_acyclic_graph(G),
        },
        "centrality": {},
        "critical_paths": [],
    }

    # Node centrality (most connected/important entities)
    if len(entities) > 0:
        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())

        # Top 10 most depended upon (high in-degree)
        most_depended = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["centrality"]["most_depended_upon"] = [
            {"entity_id": eid, "name": G.nodes[eid]["name"], "in_degree": deg}
            for eid, deg in most_depended if deg > 0
        ]

        # Top 10 with most dependencies (high out-degree)
        most_dependent = sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["centrality"]["most_dependent"] = [
            {"entity_id": eid, "name": G.nodes[eid]["name"], "out_degree": deg}
            for eid, deg in most_dependent if deg > 0
        ]

    # Detect cycles (circular dependencies)
    try:
        cycles = list(nx.simple_cycles(G))
        analysis["issues"] = {
            "circular_dependencies": len(cycles),
            "cycles": cycles[:5] if cycles else [],  # Return first 5 cycles
        }
    except:
        analysis["issues"] = {"circular_dependencies": 0, "cycles": []}

    # Find isolated entities (no dependencies)
    isolated = [n for n in G.nodes() if G.degree(n) == 0]
    analysis["issues"]["isolated_entities"] = len(isolated)

    return jsonify(analysis), 200


@bp.route("/path", methods=["GET"])
def find_path():
    """
    Find dependency path between two entities.

    Query Parameters:
        - from: Source entity ID
        - to: Target entity ID

    Returns:
        200: Path information
        404: No path found
    """
    from_id = request.args.get("from", type=int)
    to_id = request.args.get("to", type=int)

    if not from_id or not to_id:
        return make_error_response("Both 'from' and 'to' parameters required", 400)

    # Verify entities exist
    from_entity = get_or_404(Entity, from_id)
    to_entity = get_or_404(Entity, to_id)

    # Build graph
    dependencies = db.session.query(Dependency).all()
    G = nx.DiGraph()

    for dep in dependencies:
        G.add_edge(dep.source_entity_id, dep.target_entity_id, dependency_id=dep.id)

    # Find path
    try:
        path = nx.shortest_path(G, from_id, to_id)
        path_length = len(path) - 1

        # Get entities in path
        entities_in_path = db.session.query(Entity).filter(Entity.id.in_(path)).all()
        entity_map = {e.id: e for e in entities_in_path}

        path_details = [
            {"id": eid, "name": entity_map[eid].name, "type": entity_map[eid].entity_type.value}
            for eid in path
        ]

        return jsonify({
            "path_exists": True,
            "path_length": path_length,
            "path": path_details,
        }), 200

    except nx.NetworkXNoPath:
        return jsonify({
            "path_exists": False,
            "message": f"No dependency path from {from_entity.name} to {to_entity.name}",
        }), 200


def _get_entity_subgraph(entity: Entity, depth: int) -> List[Entity]:
    """
    Get entities within depth distance from given entity.

    Args:
        entity: Center entity
        depth: Maximum depth (-1 for unlimited)

    Returns:
        List of entities in subgraph
    """
    if depth == -1:
        depth = 9999

    visited = {entity.id}
    current_level = [entity]
    all_entities = [entity]

    for _ in range(depth):
        if not current_level:
            break

        next_level = []

        for e in current_level:
            # Get outgoing dependencies
            for dep in e.outgoing_dependencies:
                if dep.target_entity_id not in visited:
                    visited.add(dep.target_entity_id)
                    target = dep.target_entity
                    if target:
                        next_level.append(target)
                        all_entities.append(target)

            # Get incoming dependencies
            for dep in e.incoming_dependencies:
                if dep.source_entity_id not in visited:
                    visited.add(dep.source_entity_id)
                    source = dep.source_entity
                    if source:
                        next_level.append(source)
                        all_entities.append(source)

        current_level = next_level

    return all_entities


def _count_by_type(entities: List[Entity]) -> Dict[str, int]:
    """Count entities by type."""
    counts = {}
    for entity in entities:
        type_val = entity.entity_type.value
        counts[type_val] = counts.get(type_val, 0) + 1
    return counts


def _get_node_style(entity_type: str) -> tuple:
    """Get vis.js node styling based on entity type."""
    styles = {
        "datacenter": ("box", "#3498db"),
        "vpc": ("box", "#2980b9"),
        "subnet": ("ellipse", "#1abc9c"),
        "compute": ("circle", "#e74c3c"),
        "network": ("diamond", "#f39c12"),
        "user": ("triangle", "#9b59b6"),
        "security_issue": ("star", "#e67e22"),
    }
    return styles.get(entity_type, ("dot", "#95a5a6"))


def _get_edge_style(dependency_type: str) -> tuple:
    """Get vis.js edge styling based on dependency type."""
    styles = {
        "depends_on": ("#34495e", False),  # solid
        "related_to": ("#95a5a6", True),    # dashed
        "part_of": ("#2ecc71", False),      # solid green
    }
    return styles.get(dependency_type, ("#7f8c8d", False))
