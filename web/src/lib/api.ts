import axios from 'axios'
import type { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('elder_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // Redirect to login on 401 Unauthorized, but only if we had a token
        // (Don't redirect if we're already on login page or if request was anonymous)
        if (error.response?.status === 401) {
          const hadToken = !!localStorage.getItem('elder_token')
          const isLoginPage = window.location.pathname === '/login'

          if (hadToken && !isLoginPage) {
            localStorage.removeItem('elder_token')
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Health check
  async health() {
    const response = await axios.get(`${API_BASE_URL}/healthz`)
    return response.data
  }

  // Auth endpoints
  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login', { username, password })
    if (response.data.access_token) {
      localStorage.setItem('elder_token', response.data.access_token)
    }
    return response.data
  }

  async register(data: {
    username: string
    email: string
    password: string
    full_name: string
  }) {
    const response = await this.client.post('/auth/register', data)
    return response.data
  }

  async logout() {
    localStorage.removeItem('elder_token')
  }

  // Profile
  async getProfile() {
    const response = await this.client.get('/profile/me')
    return response.data
  }

  async updateProfile(data: Partial<{
    email: string
    full_name: string
    organization_id: number | null
  }>) {
    const response = await this.client.patch('/profile/me', data)
    return response.data
  }

  // Organizations
  async getOrganizations(params?: { page?: number; per_page?: number; search?: string }) {
    const response = await this.client.get('/organizations', { params })
    return response.data
  }

  async getOrganization(id: number) {
    const response = await this.client.get(`/organizations/${id}`)
    return response.data
  }

  async createOrganization(data: { name: string; description?: string; parent_id?: number; metadata?: any }) {
    const response = await this.client.post('/organizations', data)
    return response.data
  }

  async updateOrganization(id: number, data: Partial<{ name: string; description: string; metadata: any }>) {
    const response = await this.client.put(`/organizations/${id}`, data)
    return response.data
  }

  async deleteOrganization(id: number) {
    const response = await this.client.delete(`/organizations/${id}`)
    return response.data
  }

  async getOrganizationTreeStats(id: number) {
    const response = await this.client.get(`/organizations/${id}/tree-stats`)
    return response.data
  }

  async getOrganizationGraph(id: number, depth: number = 3) {
    const response = await this.client.get(`/organizations/${id}/graph`, {
      params: { depth }
    })
    return response.data
  }

  // Entities
  async getEntities(params?: {
    page?: number
    per_page?: number
    organization_id?: number
    entity_type?: string
    search?: string
  }) {
    const response = await this.client.get('/entities', { params })
    return response.data
  }

  async getEntity(id: number) {
    const response = await this.client.get(`/entities/${id}`)
    return response.data
  }

  async createEntity(data: {
    name: string
    description?: string
    entity_type: string
    entity_sub_type?: string
    organization_id: number
    metadata?: any
  }) {
    const response = await this.client.post('/entities', data)
    return response.data
  }

  async updateEntity(id: number, data: Partial<{
    name: string
    description: string
    metadata: any
  }>) {
    const response = await this.client.put(`/entities/${id}`, data)
    return response.data
  }

  async deleteEntity(id: number) {
    const response = await this.client.delete(`/entities/${id}`)
    return response.data
  }

  async lookupEntity(uniqueId: string) {
    const response = await this.client.get(`/lookup/${uniqueId}`)
    return response.data
  }

  // Entity Types
  async getEntityTypes(params?: { category?: string }) {
    const response = await this.client.get('/entity-types', { params })
    return response.data
  }

  async getEntityType(id: number) {
    const response = await this.client.get(`/entity-types/${id}`)
    return response.data
  }

  async createEntityType(data: {
    name: string
    category: string
    sub_type?: string
    description?: string
    default_metadata?: any
  }) {
    const response = await this.client.post('/entity-types', data)
    return response.data
  }

  async updateEntityType(id: number, data: Partial<{
    name: string
    description: string
    default_metadata: any
  }>) {
    const response = await this.client.put(`/entity-types/${id}`, data)
    return response.data
  }

  async deleteEntityType(id: number) {
    const response = await this.client.delete(`/entity-types/${id}`)
    return response.data
  }

  // Dependencies
  async getDependencies(params?: {
    page?: number
    per_page?: number
    source_entity_id?: number
    target_entity_id?: number
  }) {
    const response = await this.client.get('/dependencies', { params })
    return response.data
  }

  async createDependency(data: {
    source_entity_id: number
    target_entity_id: number
    dependency_type: string
    metadata?: any
  }) {
    const response = await this.client.post('/dependencies', data)
    return response.data
  }

  async deleteDependency(id: number) {
    const response = await this.client.delete(`/dependencies/${id}`)
    return response.data
  }

  async bulkDeleteDependencies(ids: number[]) {
    const response = await this.client.post('/dependencies/bulk-delete', { ids })
    return response.data
  }

  // Graph
  async getGraph(params?: { organization_id?: number; entity_id?: number; depth?: number }) {
    const response = await this.client.get('/graph', { params })
    return response.data
  }

  // Identities
  async getIdentities(params?: { page?: number; per_page?: number; search?: string; organization_id?: number }) {
    const response = await this.client.get('/identities', { params })
    return response.data
  }

  async getIdentity(id: number) {
    const response = await this.client.get(`/identities/${id}`)
    return response.data
  }

  async createIdentity(data: {
    username: string
    email: string
    full_name: string
    identity_type: string
    auth_provider: string
    password?: string
  }) {
    const response = await this.client.post('/identities', data)
    return response.data
  }

  async updateIdentity(id: number, data: Partial<{
    email: string
    full_name: string
    is_active: boolean
  }>) {
    const response = await this.client.put(`/identities/${id}`, data)
    return response.data
  }

  // Identity Groups
  async getIdentityGroups() {
    const response = await this.client.get('/identities/groups')
    return response.data
  }

  async createIdentityGroup(data: { name: string; description?: string }) {
    const response = await this.client.post('/identities/groups', data)
    return response.data
  }

  // Issues
  async getIssues(params?: {
    organization_id?: number
    entity_id?: number
    status?: string
    priority?: string
    assigned_to?: number
    search?: string
  }) {
    const response = await this.client.get('/issues', { params })
    return response.data
  }

  async getIssue(id: number) {
    const response = await this.client.get(`/issues/${id}`)
    return response.data
  }

  async createIssue(data: {
    title: string
    description?: string
    priority?: string
    organization_id?: number
    entity_ids?: number[]
    assigned_to?: number
    label_ids?: number[]
  }) {
    const response = await this.client.post('/issues', data)
    return response.data
  }

  async updateIssue(id: number, data: Partial<{
    title: string
    description: string
    status: string
    priority: string
    assignee_id: number | null
  }>) {
    const response = await this.client.put(`/issues/${id}`, data)
    return response.data
  }

  async deleteIssue(id: number) {
    const response = await this.client.delete(`/issues/${id}`)
    return response.data
  }

  async closeIssue(id: number) {
    const response = await this.client.post(`/issues/${id}/close`)
    return response.data
  }

  // Issue Comments
  async getIssueComments(issueId: number) {
    const response = await this.client.get(`/issues/${issueId}/comments`)
    return response.data
  }

  async createIssueComment(issueId: number, data: { body: string }) {
    const response = await this.client.post(`/issues/${issueId}/comments`, data)
    return response.data
  }

  async deleteIssueComment(issueId: number, commentId: number) {
    const response = await this.client.delete(`/issues/${issueId}/comments/${commentId}`)
    return response.data
  }

  // Issue Labels
  async getIssueLabels(issueId: number) {
    const response = await this.client.get(`/issues/${issueId}/labels`)
    return response.data
  }

  async addIssueLabel(issueId: number, labelId: number) {
    const response = await this.client.post(`/issues/${issueId}/labels/${labelId}`)
    return response.data
  }

  async removeIssueLabel(issueId: number, labelId: number) {
    const response = await this.client.delete(`/issues/${issueId}/labels/${labelId}`)
    return response.data
  }

  // Issue Entity Links
  async getIssueEntities(issueId: number) {
    const response = await this.client.get(`/issues/${issueId}/entities`)
    return response.data
  }

  async linkIssueEntity(issueId: number, entityId: number) {
    const response = await this.client.post(`/issues/${issueId}/entities/${entityId}`)
    return response.data
  }

  async unlinkIssueEntity(issueId: number, entityId: number) {
    const response = await this.client.delete(`/issues/${issueId}/entities/${entityId}`)
    return response.data
  }

  // Labels
  async getLabels(params?: { page?: number; per_page?: number; search?: string }) {
    const response = await this.client.get('/labels', { params })
    return response.data
  }

  async getLabel(id: number) {
    const response = await this.client.get(`/labels/${id}`)
    return response.data
  }

  async createLabel(data: { name: string; description?: string; color?: string }) {
    const response = await this.client.post('/labels', data)
    return response.data
  }

  async updateLabel(id: number, data: Partial<{ name: string; description: string; color: string }>) {
    const response = await this.client.put(`/labels/${id}`, data)
    return response.data
  }

  async deleteLabel(id: number) {
    const response = await this.client.delete(`/labels/${id}`)
    return response.data
  }

  // Projects
  async getProjects(params?: { page?: number; per_page?: number; organization_id?: number; status?: string; search?: string }) {
    const response = await this.client.get('/projects', { params })
    return response.data
  }

  async getProject(id: number) {
    const response = await this.client.get(`/projects/${id}`)
    return response.data
  }

  async createProject(data: { name: string; organization_id: number; description?: string; status?: string; start_date?: string; end_date?: string }) {
    const response = await this.client.post('/projects', data)
    return response.data
  }

  async updateProject(id: number, data: Partial<{ name: string; description: string; status: string; start_date: string; end_date: string }>) {
    const response = await this.client.put(`/projects/${id}`, data)
    return response.data
  }

  async deleteProject(id: number) {
    const response = await this.client.delete(`/projects/${id}`)
    return response.data
  }

  // Milestones
  async getMilestones(params?: { page?: number; per_page?: number; organization_id?: number; project_id?: number; status?: string; search?: string }) {
    const response = await this.client.get('/milestones', { params })
    return response.data
  }

  async getMilestone(id: number) {
    const response = await this.client.get(`/milestones/${id}`)
    return response.data
  }

  async createMilestone(data: { title: string; organization_id: number; description?: string; status?: string; project_id?: number; due_date?: string }) {
    const response = await this.client.post('/milestones', data)
    return response.data
  }

  async updateMilestone(id: number, data: Partial<{ title: string; description: string; status: string; project_id: number; due_date: string }>) {
    const response = await this.client.put(`/milestones/${id}`, data)
    return response.data
  }

  async deleteMilestone(id: number) {
    const response = await this.client.delete(`/milestones/${id}`)
    return response.data
  }

  async getMilestoneIssues(id: number) {
    const response = await this.client.get(`/milestones/${id}/issues`)
    return response.data
  }

  // Issue-Project Linking
  async linkIssueToProject(issueId: number, projectId: number) {
    const response = await this.client.post(`/issues/${issueId}/projects`, { project_id: projectId })
    return response.data
  }

  async unlinkIssueFromProject(issueId: number, projectId: number) {
    const response = await this.client.delete(`/issues/${issueId}/projects/${projectId}`)
    return response.data
  }

  // Issue-Milestone Linking
  async linkIssueToMilestone(issueId: number, milestoneId: number) {
    const response = await this.client.post(`/issues/${issueId}/milestones`, { milestone_id: milestoneId })
    return response.data
  }

  async unlinkIssueFromMilestone(issueId: number, milestoneId: number) {
    const response = await this.client.delete(`/issues/${issueId}/milestones/${milestoneId}`)
    return response.data
  }

  // Resource Roles
  async getResourceRoles(params?: {
    resource_type?: string
    resource_id?: number
    identity_id?: number
  }) {
    const response = await this.client.get('/resource-roles', { params })
    return response.data
  }

  async assignResourceRole(data: {
    resource_type: string
    resource_id: number
    identity_id: number
    role: string
  }) {
    const response = await this.client.post('/resource-roles', data)
    return response.data
  }

  async revokeResourceRole(id: number) {
    const response = await this.client.delete(`/resource-roles/${id}`)
    return response.data
  }

  // Organization Metadata
  async getOrganizationMetadata(id: number) {
    const response = await this.client.get(`/metadata/organizations/${id}/metadata`)
    return response.data
  }

  async createOrganizationMetadata(id: number, data: { key: string; field_type: string; value: any }) {
    const response = await this.client.post(`/metadata/organizations/${id}/metadata`, data)
    return response.data
  }

  async updateOrganizationMetadata(id: number, key: string, data: { value: any; field_type?: string }) {
    const response = await this.client.patch(`/metadata/organizations/${id}/metadata/${key}`, data)
    return response.data
  }

  async deleteOrganizationMetadata(id: number, key: string) {
    const response = await this.client.delete(`/metadata/organizations/${id}/metadata/${key}`)
    return response.data
  }

  // Entity Metadata
  async getEntityMetadata(id: number) {
    const response = await this.client.get(`/metadata/entities/${id}/metadata`)
    return response.data
  }

  async createEntityMetadata(id: number, data: { key: string; field_type: string; value: any }) {
    const response = await this.client.post(`/metadata/entities/${id}/metadata`, data)
    return response.data
  }

  async updateEntityMetadata(id: number, key: string, data: { value: any; field_type?: string }) {
    const response = await this.client.patch(`/metadata/entities/${id}/metadata/${key}`, data)
    return response.data
  }

  async deleteEntityMetadata(id: number, key: string) {
    const response = await this.client.delete(`/metadata/entities/${id}/metadata/${key}`)
    return response.data
  }

  // ===========================
  // v1.2.0 Features
  // ===========================

  // Secrets Management
  async getSecretProviders(params?: { organization_id?: number }) {
    const response = await this.client.get('/secrets/providers', { params })
    return response.data
  }

  async getSecretProvider(id: number) {
    const response = await this.client.get(`/secrets/providers/${id}`)
    return response.data
  }

  async createSecretProvider(data: {
    name: string
    provider_type: string
    organization_id: number
    config: any
    description?: string
  }) {
    const response = await this.client.post('/secrets/providers', data)
    return response.data
  }

  async updateSecretProvider(id: number, data: Partial<{ name: string; config: any; description: string; enabled: boolean }>) {
    const response = await this.client.put(`/secrets/providers/${id}`, data)
    return response.data
  }

  async deleteSecretProvider(id: number) {
    const response = await this.client.delete(`/secrets/providers/${id}`)
    return response.data
  }

  async testSecretProvider(id: number) {
    const response = await this.client.post(`/secrets/providers/${id}/test`)
    return response.data
  }

  async getSecret(providerId: number, secretName: string, params?: { version?: string }) {
    const response = await this.client.get(`/secrets/providers/${providerId}/secrets/${secretName}`, { params })
    return response.data
  }

  async listSecrets(providerId: number) {
    const response = await this.client.get(`/secrets/providers/${providerId}/secrets`)
    return response.data
  }

  // Keys Management
  async getKeyProviders(params?: { organization_id?: number }) {
    const response = await this.client.get('/keys/providers', { params })
    return response.data
  }

  async getKeyProvider(id: number) {
    const response = await this.client.get(`/keys/providers/${id}`)
    return response.data
  }

  async createKeyProvider(data: {
    name: string
    provider_type: string
    organization_id: number
    config: any
    description?: string
  }) {
    const response = await this.client.post('/keys/providers', data)
    return response.data
  }

  async updateKeyProvider(id: number, data: Partial<{ name: string; config: any; description: string; enabled: boolean }>) {
    const response = await this.client.put(`/keys/providers/${id}`, data)
    return response.data
  }

  async deleteKeyProvider(id: number) {
    const response = await this.client.delete(`/keys/providers/${id}`)
    return response.data
  }

  async testKeyProvider(id: number) {
    const response = await this.client.post(`/keys/providers/${id}/test`)
    return response.data
  }

  async encryptData(providerId: number, keyId: string, data: { plaintext: string; context?: any }) {
    const response = await this.client.post(`/keys/providers/${providerId}/keys/${keyId}/encrypt`, data)
    return response.data
  }

  async decryptData(providerId: number, keyId: string, data: { ciphertext: string; context?: any }) {
    const response = await this.client.post(`/keys/providers/${providerId}/keys/${keyId}/decrypt`, data)
    return response.data
  }

  // IAM Integration
  async getIAMProviders(params?: { organization_id?: number }) {
    const response = await this.client.get('/iam/providers', { params })
    return response.data
  }

  async getIAMProvider(id: number) {
    const response = await this.client.get(`/iam/providers/${id}`)
    return response.data
  }

  async createIAMProvider(data: {
    name: string
    provider_type: string
    organization_id: number
    config: any
    description?: string
  }) {
    const response = await this.client.post('/iam/providers', data)
    return response.data
  }

  async updateIAMProvider(id: number, data: Partial<{ name: string; config: any; description: string; enabled: boolean }>) {
    const response = await this.client.put(`/iam/providers/${id}`, data)
    return response.data
  }

  async deleteIAMProvider(id: number) {
    const response = await this.client.delete(`/iam/providers/${id}`)
    return response.data
  }

  async listIAMUsers(providerId: number) {
    const response = await this.client.get(`/iam/providers/${providerId}/users`)
    return response.data
  }

  async listIAMRoles(providerId: number) {
    const response = await this.client.get(`/iam/providers/${providerId}/roles`)
    return response.data
  }

  async listIAMPolicies(providerId: number) {
    const response = await this.client.get(`/iam/providers/${providerId}/policies`)
    return response.data
  }

  // Cloud Discovery
  async getDiscoveryJobs(params?: { organization_id?: number; status?: string }) {
    const response = await this.client.get('/discovery/jobs', { params })
    return response.data
  }

  async getDiscoveryJob(id: number) {
    const response = await this.client.get(`/discovery/jobs/${id}`)
    return response.data
  }

  async createDiscoveryJob(data: {
    name: string
    provider_type: string
    organization_id: number
    config: any
    schedule?: string
    enabled?: boolean
  }) {
    const response = await this.client.post('/discovery/jobs', data)
    return response.data
  }

  async updateDiscoveryJob(id: number, data: Partial<{ name: string; config: any; schedule: string; enabled: boolean }>) {
    const response = await this.client.put(`/discovery/jobs/${id}`, data)
    return response.data
  }

  async deleteDiscoveryJob(id: number) {
    const response = await this.client.delete(`/discovery/jobs/${id}`)
    return response.data
  }

  async runDiscoveryJob(id: number) {
    const response = await this.client.post(`/discovery/jobs/${id}/run`)
    return response.data
  }

  async getDiscoveryJobHistory(jobId: number) {
    const response = await this.client.get(`/discovery/jobs/${jobId}/history`)
    return response.data
  }

  // Google Workspace
  async getGoogleWorkspaceProviders(params?: { organization_id?: number }) {
    const response = await this.client.get('/google-workspace/providers', { params })
    return response.data
  }

  async getGoogleWorkspaceProvider(id: number) {
    const response = await this.client.get(`/google-workspace/providers/${id}`)
    return response.data
  }

  async createGoogleWorkspaceProvider(data: {
    name: string
    organization_id: number
    customer_id: string
    admin_email: string
    service_account_json: any
    description?: string
  }) {
    const response = await this.client.post('/google-workspace/providers', data)
    return response.data
  }

  async updateGoogleWorkspaceProvider(id: number, data: Partial<{
    name: string
    customer_id: string
    admin_email: string
    service_account_json: any
    description: string
    enabled: boolean
  }>) {
    const response = await this.client.put(`/google-workspace/providers/${id}`, data)
    return response.data
  }

  async deleteGoogleWorkspaceProvider(id: number) {
    const response = await this.client.delete(`/google-workspace/providers/${id}`)
    return response.data
  }

  async testGoogleWorkspaceProvider(id: number) {
    const response = await this.client.post(`/google-workspace/providers/${id}/test`)
    return response.data
  }

  async listGoogleWorkspaceUsers(providerId: number, params?: { domain?: string; limit?: number }) {
    const response = await this.client.get(`/google-workspace/providers/${providerId}/users`, { params })
    return response.data
  }

  async listGoogleWorkspaceGroups(providerId: number, params?: { domain?: string; limit?: number }) {
    const response = await this.client.get(`/google-workspace/providers/${providerId}/groups`, { params })
    return response.data
  }

  // Webhooks
  async getWebhooks(params?: { organization_id?: number }) {
    const response = await this.client.get('/webhooks', { params })
    return response.data
  }

  async getWebhook(id: number) {
    const response = await this.client.get(`/webhooks/${id}`)
    return response.data
  }

  async createWebhook(data: {
    name: string
    url: string
    organization_id: number
    events: string[]
    secret?: string
    enabled?: boolean
  }) {
    const response = await this.client.post('/webhooks', data)
    return response.data
  }

  async updateWebhook(id: number, data: Partial<{ name: string; url: string; events: string[]; secret: string; enabled: boolean }>) {
    const response = await this.client.put(`/webhooks/${id}`, data)
    return response.data
  }

  async deleteWebhook(id: number) {
    const response = await this.client.delete(`/webhooks/${id}`)
    return response.data
  }

  async testWebhook(id: number) {
    const response = await this.client.post(`/webhooks/${id}/test`)
    return response.data
  }

  async getWebhookDeliveries(webhookId: number) {
    const response = await this.client.get(`/webhooks/${webhookId}/deliveries`)
    return response.data
  }

  // Backup Management
  async getBackupJobs(params?: { organization_id?: number }) {
    const response = await this.client.get('/backup/jobs', { params })
    return response.data
  }

  async getBackupJob(id: number) {
    const response = await this.client.get(`/backup/jobs/${id}`)
    return response.data
  }

  async createBackupJob(data: {
    name: string
    schedule: string
    organization_id?: number
    retention_days: number
    enabled?: boolean
  }) {
    const response = await this.client.post('/backup/jobs', data)
    return response.data
  }

  async updateBackupJob(id: number, data: Partial<{ name: string; schedule: string; retention_days: number; enabled: boolean }>) {
    const response = await this.client.put(`/backup/jobs/${id}`, data)
    return response.data
  }

  async deleteBackupJob(id: number) {
    const response = await this.client.delete(`/backup/jobs/${id}`)
    return response.data
  }

  async runBackupJob(id: number) {
    const response = await this.client.post(`/backup/jobs/${id}/run`)
    return response.data
  }

  async getBackups(params?: { job_id?: number }) {
    const response = await this.client.get('/backup/backups', { params })
    return response.data
  }

  async getBackup(id: number) {
    const response = await this.client.get(`/backup/backups/${id}`)
    return response.data
  }

  async deleteBackup(id: number) {
    const response = await this.client.delete(`/backup/backups/${id}`)
    return response.data
  }

  async restoreBackup(id: number, data?: { dry_run?: boolean }) {
    const response = await this.client.post(`/backup/backups/${id}/restore`, data)
    return response.data
  }
}

export const api = new ApiClient()
export default api
