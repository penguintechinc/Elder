"""Basic API tests to verify endpoints work."""

import pytest
import json


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert data["service"] == "elder"


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Metrics should be in plain text format
    assert b"# HELP" in response.data or b"# TYPE" in response.data


def test_list_organizations(client):
    """Test listing organizations."""
    response = client.get("/api/v1/organizations")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_create_organization(client, db):
    """Test creating an organization."""
    org_data = {
        "name": "Test Organization",
        "description": "A test organization",
    }

    response = client.post(
        "/api/v1/organizations",
        data=json.dumps(org_data),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["name"] == "Test Organization"
    assert data["description"] == "A test organization"
    assert "id" in data


def test_list_entities(client):
    """Test listing entities."""
    response = client.get("/api/v1/entities")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "items" in data
    assert "total" in data


def test_create_entity_requires_organization(client, db):
    """Test that creating an entity requires a valid organization."""
    # First create an organization
    org_data = {"name": "Test Org"}
    org_response = client.post(
        "/api/v1/organizations",
        data=json.dumps(org_data),
        content_type="application/json",
    )
    org = json.loads(org_response.data)

    # Then create an entity
    entity_data = {
        "name": "Test Server",
        "entity_type": "compute",
        "organization_id": org["id"],
        "metadata": {
            "hostname": "server-01",
            "ip": "10.0.1.5",
        },
    }

    response = client.post(
        "/api/v1/entities",
        data=json.dumps(entity_data),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["name"] == "Test Server"
    assert data["entity_type"] == "compute"
    assert data["metadata"]["hostname"] == "server-01"


def test_list_dependencies(client):
    """Test listing dependencies."""
    response = client.get("/api/v1/dependencies")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "items" in data
    assert "total" in data


def test_create_dependency(client, db):
    """Test creating a dependency between entities."""
    # Create organization
    org = client.post(
        "/api/v1/organizations",
        data=json.dumps({"name": "Test Org"}),
        content_type="application/json",
    )
    org_id = json.loads(org.data)["id"]

    # Create two entities
    entity1 = client.post(
        "/api/v1/entities",
        data=json.dumps({
            "name": "Web Server",
            "entity_type": "compute",
            "organization_id": org_id,
        }),
        content_type="application/json",
    )
    entity1_id = json.loads(entity1.data)["id"]

    entity2 = client.post(
        "/api/v1/entities",
        data=json.dumps({
            "name": "Database",
            "entity_type": "compute",
            "organization_id": org_id,
        }),
        content_type="application/json",
    )
    entity2_id = json.loads(entity2.data)["id"]

    # Create dependency
    dep_data = {
        "source_entity_id": entity1_id,
        "target_entity_id": entity2_id,
        "dependency_type": "depends_on",
    }

    response = client.post(
        "/api/v1/dependencies",
        data=json.dumps(dep_data),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["source_entity_id"] == entity1_id
    assert data["target_entity_id"] == entity2_id
    assert data["dependency_type"] == "depends_on"


def test_get_graph(client, db):
    """Test getting dependency graph."""
    response = client.get("/api/v1/graph")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "nodes" in data
    assert "edges" in data
    assert "stats" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


def test_analyze_graph(client):
    """Test graph analysis endpoint."""
    response = client.get("/api/v1/graph/analyze")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "basic_stats" in data
    assert "graph_metrics" in data
