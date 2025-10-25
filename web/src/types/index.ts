export interface Organization {
  id: number
  name: string
  description?: string
  parent_id?: number
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Entity {
  id: number
  unique_id: string
  name: string
  description?: string
  entity_type: EntityType
  organization_id: number
  owner_identity_id?: number
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
  organization?: Organization
}

export type EntityType =
  | 'datacenter'
  | 'vpc'
  | 'subnet'
  | 'compute'
  | 'network'
  | 'user'
  | 'security_issue'

export interface Dependency {
  id: number
  source_entity_id: number
  target_entity_id: number
  dependency_type: DependencyType
  metadata?: Record<string, any>
  created_at: string
  source_entity?: Entity
  target_entity?: Entity
}

export type DependencyType = 'calls' | 'related' | 'affects' | 'depends' | 'manages' | 'other'

export interface Identity {
  id: number
  username: string
  email: string
  full_name: string
  identity_type: 'human' | 'service_account'
  auth_provider: 'local' | 'saml' | 'oauth2' | 'ldap'
  is_active: boolean
  is_superuser: boolean
  created_at: string
  last_login_at?: string
}

export interface IdentityGroup {
  id: number
  name: string
  description?: string
  created_at: string
  member_count?: number
}

export interface Issue {
  id: number
  title: string
  description?: string
  status: IssueStatus
  priority: IssuePriority
  organization_id?: number
  assigned_to?: number
  created_by: number
  created_at: string
  updated_at: string
  closed_at?: string
  labels?: IssueLabel[]
  entity_links?: Entity[]
  assignee?: Identity
}

export type IssueStatus = 'open' | 'in_progress' | 'resolved' | 'closed'
export type IssuePriority = 'low' | 'medium' | 'high' | 'critical'

export interface IssueLabel {
  id: number
  name: string
  color: string
  description?: string
}

export interface ResourceRole {
  id: number
  resource_type: 'entity' | 'organization'
  resource_id: number
  identity_id: number
  role: ResourceRoleType
  granted_at: string
  granted_by?: number
  identity?: Identity
}

export type ResourceRoleType = 'maintainer' | 'operator' | 'viewer'

export interface GraphNode {
  id: number
  unique_id: string
  name: string
  entity_type: EntityType
  organization_id: number
}

export interface GraphEdge {
  source_id: number
  target_id: number
  dependency_type: DependencyType
}

export interface Graph {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface PaginatedResponse<T> {
  items: T[]
  page: number
  pages: number
  per_page: number
  total: number
}

export interface ApiError {
  error: string
  message: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  identity: Identity
}
