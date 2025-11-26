"""Database models for Elder application using PyDAL."""

# PyDAL table definitions
# Python 3.12 dataclass DTOs
from apps.api.models.dataclasses import (AuditLogDTO, CreateDependencyRequest,
                                         CreateEntityRequest,
                                         CreateIdentityGroupRequest,
                                         CreateIdentityRequest,
                                         CreateIssueCommentRequest,
                                         CreateIssueRequest,
                                         CreateMetadataFieldRequest,
                                         CreateOrganizationRequest,
                                         CreateResourceRoleRequest,
                                         DependencyDTO, EntityDTO, IdentityDTO,
                                         IdentityGroupDTO, IssueCommentDTO,
                                         IssueDTO, IssueLabelDTO, LoginRequest,
                                         LoginResponse, MetadataFieldDTO,
                                         OrganizationDTO, PaginatedResponse,
                                         PermissionDTO, RegisterRequest,
                                         ResourceRoleDTO, RoleDTO,
                                         UpdateEntityRequest,
                                         UpdateIdentityRequest,
                                         UpdateIssueRequest,
                                         UpdateOrganizationRequest,
                                         from_pydal_row, from_pydal_rows,
                                         to_dict)
from apps.api.models.pydal_models import define_all_tables

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
