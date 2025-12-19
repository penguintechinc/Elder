"""
Pydantic 2 domain models for Elder application entities.

This module provides Pydantic 2 equivalents of Elder dataclasses with proper
validation, immutability for DTOs, and security hardening for requests.
"""

from .entity import EntityDTO, CreateEntityRequest, UpdateEntityRequest
from .identity import (
    IdentityDTO,
    CreateIdentityRequest,
    UpdateIdentityRequest,
    IdentityGroupDTO,
    CreateIdentityGroupRequest,
    UpdateIdentityGroupRequest,
    IdentityType,
    AuthProvider,
    PortalRole,
)
from .issue import (
    IssueDTO,
    CreateIssueRequest,
    UpdateIssueRequest,
    IssueStatus,
    IssuePriority,
    IssueSeverity,
)
from .label import LabelDTO, CreateLabelRequest, UpdateLabelRequest
from .metadata import (
    MetadataFieldDTO,
    CreateMetadataFieldRequest,
    UpdateMetadataFieldRequest,
)
from .network import (
    NetworkDTO,
    IPAMEntryDTO,
    CreateNetworkRequest,
    CreateIPAMEntryRequest,
)
from .organization import (
    OrganizationType,
    OrganizationDTO,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
)
from .vulnerability import (
    VulnerabilitySeverity,
    VulnerabilityDTO,
    CreateVulnerabilityRequest,
)
from .license_policy import (
    LicensePolicyDTO,
    CreateLicensePolicyRequest,
    UpdateLicensePolicyRequest,
)
from .ipam import (
    IPAMPrefixDTO,
    IPAMAddressDTO,
    IPAMVlanDTO,
    CreateIPAMPrefixRequest,
    UpdateIPAMPrefixRequest,
    CreateIPAMAddressRequest,
    UpdateIPAMAddressRequest,
    CreateIPAMVlanRequest,
    UpdateIPAMVlanRequest,
)
from .resource_role import (
    ResourceRoleResponse,
    CreateResourceRoleRequest,
    ResourceType,
    RoleType,
)
from .group import (
    UpdateGroupRequest,
    CreateAccessRequestRequest,
    AddGroupMemberRequest,
    ApproveOrDenyRequestRequest,
    BulkApproveRequestsRequest,
    GroupDTO,
    AccessRequestDTO,
    GroupMemberDTO,
    ListGroupsResponse,
    ListRequestsResponse,
    ListMembersResponse,
    BulkApproveResult,
)

__all__ = [
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
]
