"""Graph visualization API endpoints using PyDAL with async/await."""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict
import networkx as nx

from shared.async_utils import run_in_threadpool

bp = Blueprint("graph", __name__)


@bp.route("", methods=["GET"])
async def get_graph():
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
    db = current_app.db

    # Get filter parameters
    org_id = request.args.get("organization_id", type=int)
    entity_type = request.args.get("entity_type")
    entity_id = request.args.get("entity_id", type=int)
    depth = request.args.get("depth", 2, type=int)
    include_metadata = request.args.get("include_metadata", "false").lower() == "true"

    def get_graph_data():
        # Build entity query
        query = db.entities.id > 0

        if org_id:
            query &= (db.entities.organization_id == org_id)

        if entity_type:
            query &= (db.entities.entity_type == entity_type)

        # If entity_id specified, get subgraph centered on that entity
        if entity_id:
            entity = db.entities[entity_id]
            if not entity:
                return None, "Entity not found", 404

            entities = _get_entity_subgraph(db, entity, depth)
        else:
            # Get all entities matching filters
            entities = db(query).select()

        # Get entity IDs for dependency filtering
        entity_ids = [e.id for e in entities]

        # Get dependencies between these entities
        dependencies = db(
            db.dependencies.source_entity_id.belongs(entity_ids) &
            db.dependencies.target_entity_id.belongs(entity_ids)
        ).select()

        # Build vis.js compatible graph data
        nodes = []
        for entity in entities:
            node = {
                "id": entity.id,
                "label": entity.name,
                "type": entity.entity_type,
                "organization_id": entity.organization_id,
            }

            if include_metadata and entity.attributes:
                node["metadata"] = entity.attributes

            # Add visual styling based on entity type
            node["shape"], node["color"] = _get_node_style(entity.entity_type)

            nodes.append(node)

        edges = []
        for dep in dependencies:
            edge = {
                "id": dep.id,
                "from": dep.source_entity_id,
                "to": dep.target_entity_id,
                "type": dep.dependency_type,
                "arrows": "to",
            }

            # Add visual styling based on dependency type
            edge["color"], edge["dashes"] = _get_edge_style(dep.dependency_type)

            edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "entity_count": len(entities),
                "dependency_count": len(dependencies),
            }
        }, None, 200

    result, error, status = await run_in_threadpool(get_graph_data)

    if error:
        return jsonify({"error": error}), status

    return jsonify(result), status


@bp.route("/analyze", methods=["GET"])
async def analyze_graph():
    """
    Analyze dependency graph and return insights.

    Query Parameters:
        - organization_id: Filter by organization

    Returns:
        200: Graph analysis metrics
    """
    db = current_app.db

    org_id = request.args.get("organization_id", type=int)

    def analyze():
        # Build query
        query = db.entities.id > 0
        if org_id:
            query &= (db.entities.organization_id == org_id)

        entities = db(query).select()
        entity_ids = [e.id for e in entities]

        dependencies = db(
            db.dependencies.source_entity_id.belongs(entity_ids) &
            db.dependencies.target_entity_id.belongs(entity_ids)
        ).select()

        # Build NetworkX graph for analysis
        G = nx.DiGraph()

        for entity in entities:
            G.add_node(entity.id, **{
                "name": entity.name,
                "type": entity.entity_type,
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
        except Exception:
            analysis["issues"] = {"circular_dependencies": 0, "cycles": []}

        # Find isolated entities (no dependencies)
        isolated = [n for n in G.nodes() if G.degree(n) == 0]
        analysis["issues"]["isolated_entities"] = len(isolated)

        return analysis

    analysis = await run_in_threadpool(analyze)
    return jsonify(analysis), 200


@bp.route("/path", methods=["GET"])
async def find_path():
    """
    Find dependency path between two entities.

    Query Parameters:
        - from: Source entity ID
        - to: Target entity ID

    Returns:
        200: Path information
        404: No path found
    """
    db = current_app.db

    from_id = request.args.get("from", type=int)
    to_id = request.args.get("to", type=int)

    if not from_id or not to_id:
        return jsonify({"error": "Both 'from' and 'to' parameters required"}), 400

    def find_path_impl():
        # Verify entities exist
        from_entity = db.entities[from_id]
        to_entity = db.entities[to_id]

        if not from_entity:
            return None, "Source entity not found", 404
        if not to_entity:
            return None, "Target entity not found", 404

        # Build graph
        dependencies = db(db.dependencies).select()
        G = nx.DiGraph()

        for dep in dependencies:
            G.add_edge(dep.source_entity_id, dep.target_entity_id, dependency_id=dep.id)

        # Find path
        try:
            path = nx.shortest_path(G, from_id, to_id)
            path_length = len(path) - 1

            # Get entities in path
            entities_in_path = db(db.entities.id.belongs(path)).select()
            entity_map = {e.id: e for e in entities_in_path}

            path_details = [
                {"id": eid, "name": entity_map[eid].name, "type": entity_map[eid].entity_type}
                for eid in path
            ]

            return {
                "path_exists": True,
                "path_length": path_length,
                "path": path_details,
            }, None, 200

        except nx.NetworkXNoPath:
            return {
                "path_exists": False,
                "message": f"No dependency path from {from_entity.name} to {to_entity.name}",
            }, None, 200

    result, error, status = await run_in_threadpool(find_path_impl)

    if error:
        return jsonify({"error": error}), status

    return jsonify(result), status


def _get_entity_subgraph(db, entity, depth: int):
    """
    Get entities within depth distance from given entity.

    Args:
        db: PyDAL database instance
        entity: Center entity (PyDAL row)
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
            # Get outgoing dependencies (this entity depends on others)
            outgoing = db(db.dependencies.source_entity_id == e.id).select()
            for dep in outgoing:
                if dep.target_entity_id not in visited:
                    visited.add(dep.target_entity_id)
                    target = db.entities[dep.target_entity_id]
                    if target:
                        next_level.append(target)
                        all_entities.append(target)

            # Get incoming dependencies (others depend on this entity)
            incoming = db(db.dependencies.target_entity_id == e.id).select()
            for dep in incoming:
                if dep.source_entity_id not in visited:
                    visited.add(dep.source_entity_id)
                    source = db.entities[dep.source_entity_id]
                    if source:
                        next_level.append(source)
                        all_entities.append(source)

        current_level = next_level

    return all_entities


def _count_by_type(entities) -> Dict[str, int]:
    """Count entities by type."""
    counts = {}
    for entity in entities:
        type_val = entity.entity_type
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
