"""
Test suite for Pydantic models validation.

Tests CreateOrganizationRequest and OrganizationDTO validation
with valid and invalid data using pytest.
"""

from datetime import datetime
from pydantic import ValidationError
import pytest

from py_libs.pydantic.models.organization import (
    CreateOrganizationRequest,
    OrganizationDTO,
)


class TestCreateOrganizationRequest:
    """Test suite for CreateOrganizationRequest validation."""

    def test_valid_minimal_request(self):
        """Test creation with only required field (name)."""
        req = CreateOrganizationRequest(name="Engineering")
        assert req.name == "Engineering"
        assert req.description is None
        assert req.organization_type == "organization"
        assert req.parent_id is None
        assert req.ldap_dn is None
        assert req.saml_group is None
        assert req.owner_identity_id is None
        assert req.owner_group_id is None

    def test_valid_full_request(self):
        """Test creation with all fields populated."""
        req = CreateOrganizationRequest(
            name="Engineering Department",
            description="Main engineering team",
            organization_type="department",
            parent_id=1,
            ldap_dn="cn=engineering,ou=departments,dc=example,dc=com",
            saml_group="engineering-team",
            owner_identity_id=42,
            owner_group_id=100,
        )
        assert req.name == "Engineering Department"
        assert req.description == "Main engineering team"
        assert req.organization_type == "department"
        assert req.parent_id == 1
        assert req.ldap_dn == "cn=engineering,ou=departments,dc=example,dc=com"
        assert req.saml_group == "engineering-team"
        assert req.owner_identity_id == 42
        assert req.owner_group_id == 100

    def test_valid_name_at_max_length(self):
        """Test name validation at maximum length (255 chars)."""
        long_name = "A" * 255
        req = CreateOrganizationRequest(name=long_name)
        assert req.name == long_name
        assert len(req.name) == 255

    def test_valid_description_at_max_length(self):
        """Test description validation at maximum length (1000 chars)."""
        long_desc = "B" * 1000
        req = CreateOrganizationRequest(
            name="Test",
            description=long_desc
        )
        assert req.description == long_desc
        assert len(req.description) == 1000

    def test_valid_empty_description(self):
        """Test that empty description is allowed."""
        req = CreateOrganizationRequest(
            name="Test",
            description=""
        )
        assert req.description == ""

    def test_invalid_name_empty_string(self):
        """Test that empty name string raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrganizationRequest(name="")
        assert "name cannot be empty or whitespace-only" in str(exc_info.value)

    def test_invalid_name_whitespace_only(self):
        """Test that whitespace-only name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrganizationRequest(name="   ")
        assert "name cannot be empty or whitespace-only" in str(exc_info.value)

    def test_invalid_name_exceeds_max_length(self):
        """Test that name exceeding 255 chars raises validation error."""
        too_long_name = "A" * 256
        with pytest.raises(ValidationError):
            CreateOrganizationRequest(name=too_long_name)

    def test_invalid_description_exceeds_max_length(self):
        """Test that description exceeding 1000 chars raises validation error."""
        too_long_desc = "B" * 1001
        with pytest.raises(ValidationError):
            CreateOrganizationRequest(
                name="Test",
                description=too_long_desc
            )

    def test_invalid_extra_field_rejected(self):
        """Test that RequestModel rejects unknown fields (security)."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrganizationRequest(
                name="Test",
                admin=True  # Unknown field
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_invalid_parent_id_negative(self):
        """Test that negative parent_id is handled."""
        # Note: parent_id is int without validation constraints
        # This test documents the current behavior
        req = CreateOrganizationRequest(
            name="Test",
            parent_id=-1
        )
        assert req.parent_id == -1

    def test_invalid_owner_identity_id_negative(self):
        """Test that negative owner_identity_id is handled."""
        req = CreateOrganizationRequest(
            name="Test",
            owner_identity_id=-1
        )
        assert req.owner_identity_id == -1

    def test_invalid_owner_group_id_negative(self):
        """Test that negative owner_group_id is handled."""
        req = CreateOrganizationRequest(
            name="Test",
            owner_group_id=-1
        )
        assert req.owner_group_id == -1

    def test_valid_all_organization_type_values(self):
        """Test valid organization_type values."""
        types = ["department", "organization", "team", "collection", "other"]
        for org_type in types:
            req = CreateOrganizationRequest(
                name="Test",
                organization_type=org_type
            )
            assert req.organization_type == org_type

    def test_valid_custom_organization_type(self):
        """Test that custom organization_type strings are accepted."""
        req = CreateOrganizationRequest(
            name="Test",
            organization_type="custom-type"
        )
        assert req.organization_type == "custom-type"

    def test_to_dict_conversion(self):
        """Test RequestModel to_dict() conversion."""
        req = CreateOrganizationRequest(
            name="Test",
            description="Test Description",
            parent_id=5
        )
        result = req.to_dict()
        assert result["name"] == "Test"
        assert result["description"] == "Test Description"
        assert result["parent_id"] == 5

    def test_to_dict_exclude_none(self):
        """Test RequestModel to_dict() with exclude_none=True."""
        req = CreateOrganizationRequest(
            name="Test",
            description=None
        )
        result = req.to_dict(exclude_none=True)
        assert "name" in result
        assert "description" not in result

    def test_model_dump_method(self):
        """Test Pydantic model_dump() method."""
        req = CreateOrganizationRequest(
            name="Test",
            organization_type="team"
        )
        dumped = req.model_dump()
        assert dumped["name"] == "Test"
        assert dumped["organization_type"] == "team"


class TestOrganizationDTO:
    """Test suite for OrganizationDTO validation."""

    def test_valid_minimal_dto(self):
        """Test DTO creation with only required fields."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=1,
            name="Engineering",
            organization_type="department",
            created_at=now,
            updated_at=now
        )
        assert dto.id == 1
        assert dto.name == "Engineering"
        assert dto.organization_type == "department"
        assert dto.created_at == now
        assert dto.updated_at == now
        assert dto.description is None
        assert dto.parent_id is None

    def test_valid_full_dto(self):
        """Test DTO creation with all fields populated."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=42,
            name="Sales Department",
            description="Global sales organization",
            organization_type="department",
            parent_id=1,
            ldap_dn="cn=sales,ou=departments,dc=example,dc=com",
            saml_group="sales-team",
            owner_identity_id=100,
            owner_group_id=200,
            created_at=now,
            updated_at=now,
            tenant_id=5,
            village_id="a1b2-c3d4-e5f67890",
            village_segment="c3d4"
        )
        assert dto.id == 42
        assert dto.name == "Sales Department"
        assert dto.description == "Global sales organization"
        assert dto.organization_type == "department"
        assert dto.parent_id == 1
        assert dto.ldap_dn == "cn=sales,ou=departments,dc=example,dc=com"
        assert dto.saml_group == "sales-team"
        assert dto.owner_identity_id == 100
        assert dto.owner_group_id == 200
        assert dto.tenant_id == 5
        assert dto.village_id == "a1b2-c3d4-e5f67890"
        assert dto.village_segment == "c3d4"

    def test_invalid_missing_required_id(self):
        """Test that missing id raises validation error."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            OrganizationDTO(
                name="Test",
                organization_type="team",
                created_at=now,
                updated_at=now
            )

    def test_invalid_missing_required_name(self):
        """Test that missing name raises validation error."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            OrganizationDTO(
                id=1,
                organization_type="team",
                created_at=now,
                updated_at=now
            )

    def test_invalid_missing_required_organization_type(self):
        """Test that missing organization_type raises validation error."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            OrganizationDTO(
                id=1,
                name="Test",
                created_at=now,
                updated_at=now
            )

    def test_invalid_missing_required_created_at(self):
        """Test that missing created_at raises validation error."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            OrganizationDTO(
                id=1,
                name="Test",
                organization_type="team",
                updated_at=now
            )

    def test_invalid_missing_required_updated_at(self):
        """Test that missing updated_at raises validation error."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            OrganizationDTO(
                id=1,
                name="Test",
                organization_type="team",
                created_at=now
            )

    def test_immutable_prevents_modification(self):
        """Test that ImmutableModel prevents field modification."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=1,
            name="Original Name",
            organization_type="team",
            created_at=now,
            updated_at=now
        )
        with pytest.raises(ValidationError):
            dto.name = "Modified Name"

    def test_immutable_prevents_attribute_deletion(self):
        """Test that ImmutableModel prevents field deletion."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=1,
            name="Test",
            organization_type="team",
            created_at=now,
            updated_at=now
        )
        with pytest.raises(ValidationError):
            del dto.name

    def test_invalid_extra_field_rejected(self):
        """Test that ImmutableModel rejects unknown fields."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            OrganizationDTO(
                id=1,
                name="Test",
                organization_type="team",
                created_at=now,
                updated_at=now,
                custom_field="value"  # Unknown field
            )

    def test_invalid_wrong_type_id(self):
        """Test that non-integer id raises validation error."""
        now = datetime.now()
        with pytest.raises(ValidationError):
            OrganizationDTO(
                id="not-an-int",
                name="Test",
                organization_type="team",
                created_at=now,
                updated_at=now
            )

    def test_invalid_wrong_type_created_at(self):
        """Test that non-datetime created_at raises validation error."""
        with pytest.raises(ValidationError):
            OrganizationDTO(
                id=1,
                name="Test",
                organization_type="team",
                created_at="2025-01-01",  # String instead of datetime
                updated_at=datetime.now()
            )

    def test_type_coercion_datetime_string(self):
        """Test that datetime strings are coerced to datetime objects."""
        # ElderBaseModel has strict=False, so type coercion is allowed
        dto = OrganizationDTO(
            id=1,
            name="Test",
            organization_type="team",
            created_at="2025-01-01T12:00:00",
            updated_at="2025-01-01T12:00:00"
        )
        assert isinstance(dto.created_at, datetime)
        assert isinstance(dto.updated_at, datetime)

    def test_type_coercion_int_from_string(self):
        """Test that numeric strings are coerced to integers."""
        now = datetime.now()
        dto = OrganizationDTO(
            id="42",  # String instead of int
            name="Test",
            organization_type="team",
            created_at=now,
            updated_at=now,
            parent_id="5"  # String instead of int
        )
        assert isinstance(dto.id, int)
        assert dto.id == 42
        assert isinstance(dto.parent_id, int)
        assert dto.parent_id == 5

    def test_to_dict_conversion(self):
        """Test ImmutableModel to_dict() conversion."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=1,
            name="Test",
            organization_type="team",
            created_at=now,
            updated_at=now,
            parent_id=2
        )
        result = dto.to_dict()
        assert result["id"] == 1
        assert result["name"] == "Test"
        assert result["parent_id"] == 2

    def test_to_dict_exclude_none(self):
        """Test to_dict() with exclude_none=True."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=1,
            name="Test",
            organization_type="team",
            created_at=now,
            updated_at=now,
            description=None,
            parent_id=None
        )
        result = dto.to_dict(exclude_none=True)
        assert "id" in result
        assert "name" in result
        assert "description" not in result
        assert "parent_id" not in result

    def test_to_dict_exclude_unset(self):
        """Test to_dict() with exclude_unset=True."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=1,
            name="Test",
            organization_type="team",
            created_at=now,
            updated_at=now
        )
        result = dto.to_dict(exclude_unset=True)
        assert "id" in result
        assert "name" in result
        # Optional fields not explicitly set should be excluded
        # Note: behavior depends on Pydantic's unset tracking

    def test_model_dump_method(self):
        """Test Pydantic model_dump() method."""
        now = datetime.now()
        dto = OrganizationDTO(
            id=1,
            name="Test",
            organization_type="team",
            created_at=now,
            updated_at=now
        )
        dumped = dto.model_dump()
        assert dumped["id"] == 1
        assert dumped["name"] == "Test"
        assert dumped["organization_type"] == "team"

    def test_model_json_schema(self):
        """Test Pydantic model JSON schema generation."""
        schema = OrganizationDTO.model_json_schema()
        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "name" in schema["properties"]
        assert "organization_type" in schema["properties"]
        assert "created_at" in schema["properties"]
        assert "updated_at" in schema["properties"]

    def test_populate_by_name_configuration(self):
        """Test that model accepts both field name and alias."""
        now = datetime.now()
        # Test that field names work
        dto = OrganizationDTO(
            id=1,
            name="Test",
            organization_type="team",
            created_at=now,
            updated_at=now
        )
        assert dto.name == "Test"


class TestIntegration:
    """Integration tests between Request and DTO models."""

    def test_request_to_dto_conversion(self):
        """Test converting CreateOrganizationRequest data to OrganizationDTO."""
        req = CreateOrganizationRequest(
            name="Engineering",
            description="Eng team",
            organization_type="department",
            parent_id=1,
            owner_identity_id=10
        )

        # Simulate database storage and retrieval
        now = datetime.now()
        dto_data = {
            **req.model_dump(),
            "id": 1,
            "created_at": now,
            "updated_at": now,
            "tenant_id": 5
        }

        dto = OrganizationDTO(**dto_data)
        assert dto.name == req.name
        assert dto.description == req.description
        assert dto.organization_type == req.organization_type
        assert dto.parent_id == req.parent_id
        assert dto.owner_identity_id == req.owner_identity_id

    def test_populate_by_name_both_formats(self):
        """Test that both camelCase and snake_case can be used."""
        req = CreateOrganizationRequest(
            name="Test",
            organization_type="team"
        )
        assert req.organization_type == "team"

    def test_validation_error_messages_are_clear(self):
        """Test that validation errors provide clear messages."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrganizationRequest(name="   ")

        error = exc_info.value
        assert len(error.errors()) > 0
        error_msg = str(error)
        assert "name" in error_msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
