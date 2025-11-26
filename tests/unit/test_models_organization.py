"""
Unit tests for Organization model.

These tests are isolated and do not require network connections or external services.
All database operations use in-memory SQLite or mocked connections.
"""

from apps.api import db
from apps.api.models.organization import Organization


class TestOrganizationModel:
    """Test Organization model functionality."""

    def test_organization_creation(self, app):
        """Test creating a basic organization."""
        with app.app_context():
            org = Organization(
                name="Test Organization", description="A test organization"
            )
            db.session.add(org)
            db.session.commit()

            assert org.id is not None
            assert org.name == "Test Organization"
            assert org.description == "A test organization"
            assert org.parent_id is None
            assert org.created_at is not None
            assert org.updated_at is not None

    def test_organization_hierarchy(self, app):
        """Test parent-child organization relationships."""
        with app.app_context():
            parent = Organization(name="Parent Org")
            db.session.add(parent)
            db.session.commit()

            child = Organization(name="Child Org", parent_id=parent.id)
            db.session.add(child)
            db.session.commit()

            assert child.parent_id == parent.id
            assert child.parent.id == parent.id
            assert child.parent.name == "Parent Org"
            assert len(parent.children) == 1
            assert parent.children[0].id == child.id

    def test_organization_metadata(self, app):
        """Test organization metadata field."""
        with app.app_context():
            org = Organization(
                name="Metadata Org",
                metadata={"region": "us-west", "tier": "production"},
            )
            db.session.add(org)
            db.session.commit()

            assert org.metadata is not None
            assert org.metadata["region"] == "us-west"
            assert org.metadata["tier"] == "production"

    def test_organization_ldap_dn(self, app):
        """Test LDAP DN assignment."""
        with app.app_context():
            org = Organization(
                name="LDAP Org", ldap_dn="ou=engineering,dc=example,dc=com"
            )
            db.session.add(org)
            db.session.commit()

            assert org.ldap_dn == "ou=engineering,dc=example,dc=com"

    def test_organization_saml_group(self, app):
        """Test SAML group assignment."""
        with app.app_context():
            org = Organization(name="SAML Org", saml_group="engineering-team")
            db.session.add(org)
            db.session.commit()

            assert org.saml_group == "engineering-team"

    def test_organization_unique_id(self, app):
        """Test unique ID generation."""
        with app.app_context():
            org = Organization(name="Unique ID Org")
            db.session.add(org)
            db.session.commit()

            assert org.unique_id is not None
            assert len(str(org.unique_id)) > 0

    def test_organization_update(self, app):
        """Test updating organization fields."""
        with app.app_context():
            org = Organization(name="Original Name")
            db.session.add(org)
            db.session.commit()
            original_created = org.created_at

            org.name = "Updated Name"
            org.description = "New description"
            db.session.commit()

            assert org.name == "Updated Name"
            assert org.description == "New description"
            assert org.created_at == original_created
            assert org.updated_at > original_created

    def test_organization_deletion(self, app):
        """Test organization deletion."""
        with app.app_context():
            org = Organization(name="Delete Me")
            db.session.add(org)
            db.session.commit()
            org_id = org.id

            db.session.delete(org)
            db.session.commit()

            deleted_org = Organization.query.get(org_id)
            assert deleted_org is None

    def test_multiple_organizations(self, app):
        """Test creating multiple organizations."""
        with app.app_context():
            org1 = Organization(name="Org 1")
            org2 = Organization(name="Org 2")
            org3 = Organization(name="Org 3")

            db.session.add_all([org1, org2, org3])
            db.session.commit()

            orgs = Organization.query.all()
            assert len(orgs) >= 3
            org_names = [o.name for o in orgs]
            assert "Org 1" in org_names
            assert "Org 2" in org_names
            assert "Org 3" in org_names

    def test_organization_query_by_parent(self, app):
        """Test querying organizations by parent."""
        with app.app_context():
            parent = Organization(name="Parent")
            db.session.add(parent)
            db.session.commit()

            child1 = Organization(name="Child 1", parent_id=parent.id)
            child2 = Organization(name="Child 2", parent_id=parent.id)
            db.session.add_all([child1, child2])
            db.session.commit()

            children = Organization.query.filter_by(parent_id=parent.id).all()
            assert len(children) == 2
            child_names = [c.name for c in children]
            assert "Child 1" in child_names
            assert "Child 2" in child_names

    def test_organization_repr(self, app):
        """Test organization string representation."""
        with app.app_context():
            org = Organization(name="Test Org")
            db.session.add(org)
            db.session.commit()

            repr_str = repr(org)
            assert "Organization" in repr_str
            assert "Test Org" in repr_str
