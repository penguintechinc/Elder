"""Python 3.12 dataclasses with slots for Elder application.

Using @dataclass(slots=True) provides 30-50% memory reduction and faster attribute access.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


# ==================== Organization Units (OUs) ====================

@dataclass(slots=True, frozen=True)
class OrganizationDTO:
    """Immutable Organization Unit (OU) data transfer object."""
    id: int
    name: str
    description: Optional[str]
    organization_type: str  # department, organization, team, collection, other
    parent_id: Optional[int]
    ldap_dn: Optional[str]
    saml_group: Optional[str]
    owner_identity_id: Optional[int]
    owner_group_id: Optional[int]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateOrganizationRequest:
    """Request to create a new Organization Unit (OU)."""
    name: str
    description: Optional[str] = None
    organization_type: str = 'organization'  # department, organization, team, collection, other
    parent_id: Optional[int] = None
    ldap_dn: Optional[str] = None
    saml_group: Optional[str] = None
    owner_identity_id: Optional[int] = None
    owner_group_id: Optional[int] = None


@dataclass(slots=True)
class UpdateOrganizationRequest:
    """Request to update an Organization Unit (OU)."""
    name: Optional[str] = None
    description: Optional[str] = None
    organization_type: Optional[str] = None  # department, organization, team, collection, other
    parent_id: Optional[int] = None
    ldap_dn: Optional[str] = None
    saml_group: Optional[str] = None
    owner_identity_id: Optional[int] = None
    owner_group_id: Optional[int] = None


# ==================== Entities ====================

@dataclass(slots=True, frozen=True)
class EntityDTO:
    """Immutable Entity data transfer object."""
    id: int
    name: str
    description: Optional[str]
    entity_type: str
    sub_type: Optional[str]
    organization_id: int
    parent_id: Optional[int]
    attributes: Optional[dict]
    tags: Optional[list[str]]
    is_active: bool
    default_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateEntityRequest:
    """Request to create a new Entity."""
    name: str
    entity_type: str
    organization_id: int
    description: Optional[str] = None
    sub_type: Optional[str] = None
    parent_id: Optional[int] = None
    attributes: Optional[dict] = None
    tags: Optional[list[str]] = field(default_factory=list)
    default_metadata: Optional[dict] = None
    is_active: bool = True


@dataclass(slots=True)
class UpdateEntityRequest:
    """Request to update an Entity."""
    name: Optional[str] = None
    description: Optional[str] = None
    entity_type: Optional[str] = None
    sub_type: Optional[str] = None
    parent_id: Optional[int] = None
    attributes: Optional[dict] = None
    tags: Optional[list[str]] = None
    default_metadata: Optional[dict] = None
    is_active: Optional[bool] = None


# ==================== Dependencies ====================

@dataclass(slots=True, frozen=True)
class DependencyDTO:
    """Immutable Dependency data transfer object."""
    id: int
    source_entity_id: int
    target_entity_id: int
    dependency_type: str
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateDependencyRequest:
    """Request to create a new Dependency."""
    source_entity_id: int
    target_entity_id: int
    dependency_type: str
    metadata: Optional[dict] = None


# ==================== Identities ====================

@dataclass(slots=True, frozen=True)
class IdentityDTO:
    """Immutable Identity data transfer object."""
    id: int
    identity_type: str
    username: str
    email: Optional[str]
    full_name: Optional[str]
    organization_id: Optional[int]  # Link to organization
    portal_role: str  # admin, editor, observer
    auth_provider: str
    auth_provider_id: Optional[str]
    is_active: bool
    is_superuser: bool
    mfa_enabled: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateIdentityRequest:
    """Request to create a new Identity."""
    username: str
    identity_type: str
    auth_provider: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None  # Will be hashed
    auth_provider_id: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    mfa_enabled: bool = False


@dataclass(slots=True)
class UpdateIdentityRequest:
    """Request to update an Identity."""
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None  # Will be hashed
    is_active: Optional[bool] = None
    mfa_enabled: Optional[bool] = None


# ==================== Identity Groups ====================

@dataclass(slots=True, frozen=True)
class IdentityGroupDTO:
    """Immutable Identity Group data transfer object."""
    id: int
    name: str
    description: Optional[str]
    ldap_dn: Optional[str]
    saml_group: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateIdentityGroupRequest:
    """Request to create a new Identity Group."""
    name: str
    description: Optional[str] = None
    ldap_dn: Optional[str] = None
    saml_group: Optional[str] = None
    is_active: bool = True


# ==================== Roles & Permissions ====================

@dataclass(slots=True, frozen=True)
class RoleDTO:
    """Immutable Role data transfer object."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True, frozen=True)
class PermissionDTO:
    """Immutable Permission data transfer object."""
    id: int
    name: str
    resource_type: str
    action: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


# ==================== Resource Roles (Enterprise) ====================

@dataclass(slots=True, frozen=True)
class ResourceRoleDTO:
    """Immutable Resource Role data transfer object."""
    id: int
    identity_id: Optional[int]
    group_id: Optional[int]
    role: str  # maintainer, operator, viewer
    resource_type: str
    resource_id: Optional[int]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateResourceRoleRequest:
    """Request to create a Resource Role assignment."""
    role: str
    resource_type: str
    identity_id: Optional[int] = None
    group_id: Optional[int] = None
    resource_id: Optional[int] = None


# ==================== Issues (Enterprise) ====================

@dataclass(slots=True, frozen=True)
class IssueDTO:
    """Immutable Issue data transfer object."""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    issue_type: str
    reporter_id: int
    assignee_id: Optional[int]
    organization_id: Optional[int]
    is_incident: int
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateIssueRequest:
    """Request to create a new Issue."""
    title: str
    reporter_id: int
    description: Optional[str] = None
    status: str = "open"
    priority: str = "medium"
    issue_type: str = "other"
    assignee_id: Optional[int] = None
    organization_id: Optional[int] = None
    is_incident: int = 0


@dataclass(slots=True)
class UpdateIssueRequest:
    """Request to update an Issue."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    issue_type: Optional[str] = None
    assignee_id: Optional[int] = None
    is_incident: Optional[int] = None


@dataclass(slots=True, frozen=True)
class IssueLabelDTO:
    """Immutable Issue Label data transfer object."""
    id: int
    name: str
    color: str
    description: Optional[str]
    created_at: datetime


@dataclass(slots=True, frozen=True)
class IssueCommentDTO:
    """Immutable Issue Comment data transfer object."""
    id: int
    issue_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateIssueCommentRequest:
    """Request to create an Issue Comment."""
    issue_id: int
    author_id: int
    content: str


@dataclass(slots=True)
class CreateLabelRequest:
    """Request to create a Label."""
    name: str
    description: Optional[str] = None
    color: Optional[str] = '#cccccc'


@dataclass(slots=True)
class UpdateLabelRequest:
    """Request to update a Label."""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


# ==================== Projects ====================

@dataclass(slots=True, frozen=True)
class ProjectDTO:
    """Immutable Project data transfer object."""
    id: int
    name: str
    description: Optional[str]
    status: str
    organization_id: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateProjectRequest:
    """Request to create a new Project."""
    name: str
    organization_id: int
    description: Optional[str] = None
    status: str = 'active'
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass(slots=True)
class UpdateProjectRequest:
    """Request to update a Project."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ==================== Milestones ====================

@dataclass(slots=True, frozen=True)
class MilestoneDTO:
    """Immutable Milestone data transfer object."""
    id: int
    title: str
    description: Optional[str]
    status: str
    organization_id: int
    project_id: Optional[int]
    due_date: Optional[datetime]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateMilestoneRequest:
    """Request to create a new Milestone."""
    title: str
    organization_id: int
    description: Optional[str] = None
    status: str = 'open'
    project_id: Optional[int] = None
    due_date: Optional[datetime] = None


@dataclass(slots=True)
class UpdateMilestoneRequest:
    """Request to update a Milestone."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[int] = None
    due_date: Optional[datetime] = None
    closed_at: Optional[datetime] = None


# ==================== Metadata (Enterprise) ====================

@dataclass(slots=True, frozen=True)
class MetadataFieldDTO:
    """Immutable Metadata Field data transfer object."""
    id: int
    key: str
    value: Optional[str]
    field_type: str  # string, number, date, boolean, json
    is_system: bool
    resource_type: str
    resource_id: int
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateMetadataFieldRequest:
    """Request to create a Metadata Field."""
    key: str
    value: Optional[str]
    field_type: str
    resource_type: str
    resource_id: int
    is_system: bool = False


# ==================== API Keys ====================

@dataclass(slots=True, frozen=True)
class APIKeyDTO:
    """Immutable API Key data transfer object."""
    id: int
    identity_id: int
    name: str
    prefix: str  # First few chars for display
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class CreateAPIKeyRequest:
    """Request to create a new API Key."""
    name: str
    expires_at: Optional[datetime] = None


@dataclass(slots=True, frozen=True)
class CreateAPIKeyResponse:
    """Response when creating a new API Key (includes full key once)."""
    id: int
    name: str
    api_key: str  # Full key - shown only once!
    prefix: str
    expires_at: Optional[datetime]
    created_at: datetime


# ==================== Auth Requests/Responses ====================

@dataclass(slots=True)
class LoginRequest:
    """Login request with username and password."""
    username: str
    password: str
    mfa_code: Optional[str] = None


@dataclass(slots=True, frozen=True)
class LoginResponse:
    """Login response with access token."""
    access_token: str
    token_type: str
    expires_in: int
    identity: IdentityDTO


@dataclass(slots=True)
class RegisterRequest:
    """User registration request."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


# ==================== Audit Logs ====================

@dataclass(slots=True, frozen=True)
class AuditLogDTO:
    """Immutable Audit Log data transfer object."""
    id: int
    identity_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[dict]
    success: bool
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


# ==================== Pagination ====================

@dataclass(slots=True, frozen=True)
class PaginatedResponse:
    """Generic paginated response wrapper."""
    items: list
    total: int
    page: int
    per_page: int
    pages: int


# ==================== Helper Functions ====================

def to_dict(obj) -> dict:
    """Convert dataclass to dictionary (handles nested objects)."""
    return asdict(obj)


def from_pydal_row(row, dto_class):
    """Convert PyDAL Row to dataclass DTO."""
    if row is None:
        return None
    return dto_class(**row.as_dict())


def from_pydal_rows(rows, dto_class) -> list:
    """Convert PyDAL Rows to list of dataclass DTOs."""
    return [dto_class(**row.as_dict()) for row in rows]
