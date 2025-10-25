"""Database models for Elder application using PyDAL."""

# PyDAL table definitions
from apps.api.models.pydal_models import define_all_tables

# Python 3.12 dataclass DTOs
from apps.api.models.dataclasses import (
    OrganizationDTO,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    EntityDTO,
    CreateEntityRequest,
    UpdateEntityRequest,
    DependencyDTO,
    CreateDependencyRequest,
    IdentityDTO,
    CreateIdentityRequest,
    UpdateIdentityRequest,
    IdentityGroupDTO,
    CreateIdentityGroupRequest,
    RoleDTO,
    PermissionDTO,
    ResourceRoleDTO,
    CreateResourceRoleRequest,
    IssueDTO,
    CreateIssueRequest,
    UpdateIssueRequest,
    IssueLabelDTO,
    IssueCommentDTO,
    CreateIssueCommentRequest,
    MetadataFieldDTO,
    CreateMetadataFieldRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    AuditLogDTO,
    PaginatedResponse,
    from_pydal_row,
    from_pydal_rows,
    to_dict,
)

__all__ = [
    # PyDAL table definitions
    "define_all_tables",
    # DTOs - Organizations
    "OrganizationDTO",
    "CreateOrganizationRequest",
    "UpdateOrganizationRequest",
    # DTOs - Entities
    "EntityDTO",
    "CreateEntityRequest",
    "UpdateEntityRequest",
    # DTOs - Dependencies
    "DependencyDTO",
    "CreateDependencyRequest",
    # DTOs - Identities
    "IdentityDTO",
    "CreateIdentityRequest",
    "UpdateIdentityRequest",
    # DTOs - Groups
    "IdentityGroupDTO",
    "CreateIdentityGroupRequest",
    # DTOs - RBAC
    "RoleDTO",
    "PermissionDTO",
    "ResourceRoleDTO",
    "CreateResourceRoleRequest",
    # DTOs - Issues
    "IssueDTO",
    "CreateIssueRequest",
    "UpdateIssueRequest",
    "IssueLabelDTO",
    "IssueCommentDTO",
    "CreateIssueCommentRequest",
    # DTOs - Metadata
    "MetadataFieldDTO",
    "CreateMetadataFieldRequest",
    # DTOs - Auth
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    # DTOs - Audit
    "AuditLogDTO",
    # DTOs - Pagination
    "PaginatedResponse",
    # Helper functions
    "from_pydal_row",
    "from_pydal_rows",
    "to_dict",
]
