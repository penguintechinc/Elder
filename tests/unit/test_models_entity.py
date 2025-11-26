"""
Unit tests for Entity model.

These tests are isolated and do not require network connections or external services.
"""

from apps.api import db
from apps.api.models.entity import Entity, EntityType
from apps.api.models.organization import Organization


class TestEntityModel:
    """Test Entity model functionality."""

    def test_entity_creation(self, app):
        """Test creating a basic entity."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity = Entity(
                name="Test Server",
                entity_type=EntityType.COMPUTE,
                organization_id=org.id,
                description="A test server",
            )
            db.session.add(entity)
            db.session.commit()

            assert entity.id is not None
            assert entity.name == "Test Server"
            assert entity.entity_type == EntityType.COMPUTE
            assert entity.organization_id == org.id
            assert entity.description == "A test server"

    def test_entity_types(self, app):
        """Test all entity types."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity_types = [
                (EntityType.DATACENTER, "DC1"),
                (EntityType.SUBNET, "10.0.0.0/24"),
                (EntityType.COMPUTE, "server-01"),
                (EntityType.NETWORK, "router-01"),
                (EntityType.USER, "john.doe"),
                (EntityType.SECURITY_ISSUE, "CVE-2024-1234"),
            ]

            for entity_type, name in entity_types:
                entity = Entity(
                    name=name, entity_type=entity_type, organization_id=org.id
                )
                db.session.add(entity)

            db.session.commit()

            for entity_type, name in entity_types:
                entity = Entity.query.filter_by(name=name).first()
                assert entity is not None
                assert entity.entity_type == entity_type

    def test_entity_metadata(self, app):
        """Test entity metadata field."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity = Entity(
                name="Server with metadata",
                entity_type=EntityType.COMPUTE,
                organization_id=org.id,
                metadata={"cpu": "8 cores", "memory": "32GB", "os": "Ubuntu 22.04"},
            )
            db.session.add(entity)
            db.session.commit()

            assert entity.metadata is not None
            assert entity.metadata["cpu"] == "8 cores"
            assert entity.metadata["memory"] == "32GB"
            assert entity.metadata["os"] == "Ubuntu 22.04"

    def test_entity_unique_id(self, app):
        """Test unique ID generation."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity = Entity(
                name="Unique Entity",
                entity_type=EntityType.COMPUTE,
                organization_id=org.id,
            )
            db.session.add(entity)
            db.session.commit()

            assert entity.unique_id is not None
            assert len(str(entity.unique_id)) > 0

    def test_entity_organization_relationship(self, app):
        """Test entity-organization relationship."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity = Entity(
                name="Test Entity",
                entity_type=EntityType.COMPUTE,
                organization_id=org.id,
            )
            db.session.add(entity)
            db.session.commit()

            assert entity.organization.id == org.id
            assert entity.organization.name == "Test Org"
            assert len(org.entities) == 1
            assert org.entities[0].id == entity.id

    def test_entity_update(self, app):
        """Test updating entity fields."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity = Entity(
                name="Original Name",
                entity_type=EntityType.COMPUTE,
                organization_id=org.id,
            )
            db.session.add(entity)
            db.session.commit()
            original_created = entity.created_at

            entity.name = "Updated Name"
            entity.description = "New description"
            db.session.commit()

            assert entity.name == "Updated Name"
            assert entity.description == "New description"
            assert entity.created_at == original_created
            assert entity.updated_at > original_created

    def test_entity_deletion(self, app):
        """Test entity deletion."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity = Entity(
                name="Delete Me", entity_type=EntityType.COMPUTE, organization_id=org.id
            )
            db.session.add(entity)
            db.session.commit()
            entity_id = entity.id

            db.session.delete(entity)
            db.session.commit()

            deleted_entity = Entity.query.get(entity_id)
            assert deleted_entity is None

    def test_multiple_entities_same_org(self, app):
        """Test multiple entities in same organization."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity1 = Entity(
                name="Entity 1", entity_type=EntityType.COMPUTE, organization_id=org.id
            )
            entity2 = Entity(
                name="Entity 2", entity_type=EntityType.NETWORK, organization_id=org.id
            )
            entity3 = Entity(
                name="Entity 3", entity_type=EntityType.SUBNET, organization_id=org.id
            )

            db.session.add_all([entity1, entity2, entity3])
            db.session.commit()

            entities = Entity.query.filter_by(organization_id=org.id).all()
            assert len(entities) == 3

    def test_entity_query_by_type(self, app):
        """Test querying entities by type."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            compute1 = Entity(
                name="Server 1", entity_type=EntityType.COMPUTE, organization_id=org.id
            )
            compute2 = Entity(
                name="Server 2", entity_type=EntityType.COMPUTE, organization_id=org.id
            )
            network = Entity(
                name="Router 1", entity_type=EntityType.NETWORK, organization_id=org.id
            )

            db.session.add_all([compute1, compute2, network])
            db.session.commit()

            compute_entities = Entity.query.filter_by(
                entity_type=EntityType.COMPUTE
            ).all()
            assert len(compute_entities) == 2

            network_entities = Entity.query.filter_by(
                entity_type=EntityType.NETWORK
            ).all()
            assert len(network_entities) == 1

    def test_entity_repr(self, app):
        """Test entity string representation."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            entity = Entity(
                name="Test Entity",
                entity_type=EntityType.COMPUTE,
                organization_id=org.id,
            )
            db.session.add(entity)
            db.session.commit()

            repr_str = repr(entity)
            assert "Entity" in repr_str
            assert "Test Entity" in repr_str
