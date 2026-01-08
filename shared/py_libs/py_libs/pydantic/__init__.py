"""Pydantic 2 integration module for py_libs.

Provides custom base models for Elder applications and custom Annotated
types that integrate with py_libs.validation validators for seamless
Pydantic model validation.

Features:
- Base models with Elder-specific configuration (ElderBaseModel,
  ImmutableModel, RequestModel, ConfigurableModel)
- Pre-built Annotated types for common use cases (email, URL, IP, hostname)
- Factory functions for customizable types (strong_password, bounded_str)
- Full integration with py_libs.validation IS_* validators
- No breaking changes to existing validation code

Usage:
    from pydantic import BaseModel
    from py_libs.pydantic import (
        ElderBaseModel,
        RequestModel,
        EmailStr,
        StrongPassword,
        Name255,
    )

    class UserRequest(RequestModel):
        email: EmailStr
        password: StrongPassword
        name: Name255

    user = UserRequest(
        email="user@example.com",
        password="SecureP@ss123",
        name="John Doe"
    )
"""

# flake8: noqa: E501

# Base Models
from py_libs.pydantic.base import (
    ConfigurableModel,
    ElderBaseModel,
    ImmutableModel,
    RequestModel,
)

# Flask Integration
from py_libs.pydantic.flask_integration import (
    ValidationErrorResponse,
    model_response,
    validate_body,
    validate_query_params,
    validated_request,
)

# Domain Models - re-export everything from models submodule
from py_libs.pydantic.models import *  # noqa: F401, F403

# Type Aliases
from py_libs.pydantic.types import (
    Description1000,
    EmailStr,
    HostnameStr,
    IPAddressStr,
    IPv4Str,
    IPv6Str,
    ModeratePassword,
    Name255,
    NonEmptyStr,
    ShortText100,
    SlugStr,
    StrongPassword,
    URLStr,
    bounded_str,
    strong_password,
)

__all__ = [
    # Base Models
    "ElderBaseModel",
    "ImmutableModel",
    "RequestModel",
    "ConfigurableModel",
    # Basic types
    "EmailStr",
    "URLStr",
    "IPAddressStr",
    "IPv4Str",
    "IPv6Str",
    "HostnameStr",
    "NonEmptyStr",
    "SlugStr",
    # Factory functions
    "strong_password",
    "bounded_str",
    # Pre-built password types
    "StrongPassword",
    "ModeratePassword",
    # Pre-built text length types
    "Name255",
    "Description1000",
    "ShortText100",
    # Flask Integration
    "ValidationErrorResponse",
    "validate_body",
    "validate_query_params",
    "validated_request",
    "model_response",
    # Domain Models (imported from models/__init__.py)
    "EntityDTO",
    "CreateEntityRequest",
    "UpdateEntityRequest",
    "IdentityDTO",
    "CreateIdentityRequest",
    "UpdateIdentityRequest",
    "IdentityGroupDTO",
    "CreateIdentityGroupRequest",
    "UpdateIdentityGroupRequest",
    "IdentityType",
    "AuthProvider",
    "PortalRole",
    "IPAMEntryDTO",
    "CreateIPAMEntryRequest",
    "IssueDTO",
    "CreateIssueRequest",
    "UpdateIssueRequest",
    "IssueStatus",
    "IssuePriority",
    "IssueSeverity",
    "LabelDTO",
    "CreateLabelRequest",
    "UpdateLabelRequest",
    "MetadataFieldDTO",
    "CreateMetadataFieldRequest",
    "UpdateMetadataFieldRequest",
    "NetworkDTO",
    "CreateNetworkRequest",
    "OrganizationType",
    "OrganizationDTO",
    "CreateOrganizationRequest",
    "UpdateOrganizationRequest",
    "VulnerabilitySeverity",
    "VulnerabilityDTO",
    "CreateVulnerabilityRequest",
    "LicensePolicyDTO",
    "CreateLicensePolicyRequest",
    "UpdateLicensePolicyRequest",
    "IPAMPrefixDTO",
    "IPAMAddressDTO",
    "IPAMVlanDTO",
    "CreateIPAMPrefixRequest",
    "UpdateIPAMPrefixRequest",
    "CreateIPAMAddressRequest",
    "UpdateIPAMAddressRequest",
    "CreateIPAMVlanRequest",
    "UpdateIPAMVlanRequest",
    "UpdateGroupRequest",
    "CreateAccessRequestRequest",
    "AddGroupMemberRequest",
    "ApproveOrDenyRequestRequest",
    "BulkApproveRequestsRequest",
    "GroupDTO",
    "AccessRequestDTO",
    "GroupMemberDTO",
    "ListGroupsResponse",
    "ListRequestsResponse",
    "ListMembersResponse",
    "BulkApproveResult",
    "ResourceRoleResponse",
    "CreateResourceRoleRequest",
    "ResourceType",
    "RoleType",
    # Service Models
    "ServiceDTO",
    "CreateServiceRequest",
    "UpdateServiceRequest",
]
