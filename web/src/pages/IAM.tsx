import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Shield, Users, User, Bot, Cloud, RefreshCw, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'
import ModalFormBuilder from '@/components/ModalFormBuilder'
import GroupMembershipManager from '@/components/GroupMembershipManager'
import { FormConfig } from '@/types/form'
import { getStatusColor } from '@/lib/colorHelpers'

const TABS = ['All Identities', 'Providers', 'Groups & Roles', 'Relationships'] as const
type Tab = typeof TABS[number]

const PROVIDER_TYPES = [
  { value: 'local', label: 'Local Database', icon: Shield },
  { value: 'aws_iam', label: 'AWS IAM', icon: Cloud },
  { value: 'gcp_iam', label: 'GCP IAM', icon: Cloud },
  { value: 'azure_ad', label: 'Azure AD', icon: Cloud },
  { value: 'google_workspace', label: 'Google Workspace', icon: Cloud },
  { value: 'kubernetes', label: 'Kubernetes RBAC', icon: Shield },
]

const IDENTITY_TYPES = [
  { value: 'employee', label: 'Employee', icon: User, color: 'blue' },
  { value: 'vendor', label: 'Vendor', icon: User, color: 'purple' },
  { value: 'bot', label: 'Bot', icon: Bot, color: 'green' },
  { value: 'serviceAccount', label: 'Service Account', icon: Shield, color: 'orange' },
  { value: 'integration', label: 'Integration', icon: Shield, color: 'cyan' },
  { value: 'otherHuman', label: 'Other Human', icon: User, color: 'slate' },
  { value: 'other', label: 'Other', icon: User, color: 'slate' },
]

export default function IAM() {
  const [activeTab, setActiveTab] = useState<Tab>('All Identities')
  const [searchQuery, setSearchQuery] = useState('')
  const [providerFilter, setProviderFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedIdentity, setSelectedIdentity] = useState<any>(null)
  const [modalType, setModalType] = useState<'identity' | 'provider'>('identity')
  const queryClient = useQueryClient()

  // Provider form state (keeping these for provider modal which has complex conditional fields)
  const [providerName, setProviderName] = useState('')
  const [providerType, setProviderType] = useState('aws_iam')

  // AWS IAM specific fields
  const [awsRegion, setAwsRegion] = useState('us-east-1')
  const [awsAccessKeyId, setAwsAccessKeyId] = useState('')
  const [awsSecretAccessKey, setAwsSecretAccessKey] = useState('')

  // GCP IAM specific fields
  const [gcpProjectId, setGcpProjectId] = useState('')
  const [gcpServiceAccountKey, setGcpServiceAccountKey] = useState('')

  // Azure AD specific fields
  const [azureTenantId, setAzureTenantId] = useState('')
  const [azureClientId, setAzureClientId] = useState('')
  const [azureClientSecret, setAzureClientSecret] = useState('')

  // Google Workspace specific fields
  const [googleAdminEmail, setGoogleAdminEmail] = useState('')
  const [googleServiceAccountKey, setGoogleServiceAccountKey] = useState('')
  const [googleCustomerId, setGoogleCustomerId] = useState('')

  // Kubernetes specific fields
  const [k8sApiServer, setK8sApiServer] = useState('')
  const [k8sToken, setK8sToken] = useState('')
  const [k8sCaCert, setK8sCaCert] = useState('')

  // Fetch organizations for dropdown
  const { data: organizations } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })


  // Fetch all identity sources
  const { data: localIdentities } = useQuery({
    queryKey: ['identities', searchQuery, typeFilter],
    queryFn: () => api.getIdentities({
      search: searchQuery,
      identity_type: typeFilter || undefined,
    }),
    enabled: activeTab === 'All Identities',
  })

  const { data: iamProviders } = useQuery({
    queryKey: ['iamProviders'],
    queryFn: () => api.getIAMProviders(),
  })

  const { data: googleWorkspaceProviders } = useQuery({
    queryKey: ['googleWorkspaceProviders'],
    queryFn: () => api.getGoogleWorkspaceProviders(),
  })

  // Form configs for identity creation
  const createIdentityFormConfig: FormConfig = {
    fields: [
      {
        name: 'username',
        label: 'Username',
        type: 'username',
        required: true,
        placeholder: 'Enter username',
      },
      {
        name: 'email',
        label: 'Email',
        type: 'email',
        required: true,
        placeholder: 'Enter email',
      },
      {
        name: 'full_name',
        label: 'Full Name',
        type: 'text',
        required: true,
        placeholder: 'Enter full name',
      },
      {
        name: 'identity_type',
        label: 'Identity Type',
        type: 'select',
        required: true,
        defaultValue: 'employee',
        options: IDENTITY_TYPES.map(t => ({ value: t.value, label: t.label })),
      },
      {
        name: 'auth_provider',
        label: 'Authentication Provider',
        type: 'select',
        required: true,
        defaultValue: 'local',
        options: [
          { value: 'local', label: 'Local App' },
          { value: 'ldap', label: 'LDAP' },
          { value: 'saml', label: 'SAML' },
          { value: 'oauth2', label: 'OAuth2' },
        ],
      },
      {
        name: 'password',
        label: 'Password',
        type: 'password_generate',
        required: true,
        placeholder: 'Enter or generate password',
        showWhen: (values) => values.auth_provider === 'local',
      },
      {
        name: 'organization_id',
        label: 'Organization',
        type: 'select',
        required: true,
        options: [
          { value: '', label: 'Select organization' },
          ...(organizations?.items?.map((org: any) => ({
            value: org.id,
            label: org.name,
          })) || []),
        ],
      },
      {
        name: 'is_portal_user',
        label: 'Create as Portal User',
        type: 'checkbox',
        defaultValue: false,
        helpText: 'Portal users can log in to the Elder web interface',
      },
      {
        name: 'portal_role',
        label: 'Portal Role',
        type: 'select',
        required: true,
        defaultValue: 'viewer',
        showWhen: (values) => values.is_portal_user === true,
        options: [
          { value: 'viewer', label: 'Viewer - Read-only access' },
          { value: 'editor', label: 'Editor - Can modify data' },
          { value: 'admin', label: 'Admin - Full access' },
        ],
      },
      {
        name: 'must_change_password',
        label: 'Require password change on first login',
        type: 'checkbox',
        defaultValue: true,
        showWhen: (values) => values.is_portal_user === true,
      },
    ],
    submitLabel: 'Create Identity',
  }

  // Form config for editing identity
  const editIdentityFormConfig: FormConfig = {
    fields: [
      {
        name: 'email',
        label: 'Email',
        type: 'email',
        placeholder: 'user@example.com',
      },
      {
        name: 'full_name',
        label: 'Full Name',
        type: 'text',
        placeholder: 'John Doe',
      },
      {
        name: 'organization_id',
        label: 'Organization',
        type: 'select',
        required: true,
        options: [
          { value: '', label: 'Select organization' },
          ...(organizations?.items?.map((org: any) => ({
            value: org.id,
            label: org.name,
          })) || []),
        ],
      },
      {
        name: 'password',
        label: 'New Password (leave blank to keep current)',
        type: 'password_generate',
        placeholder: 'Enter or generate new password',
      },
      {
        name: 'is_active',
        label: 'Active',
        type: 'checkbox',
        defaultValue: true,
      },
      {
        name: 'mfa_enabled',
        label: 'MFA Enabled',
        type: 'checkbox',
        defaultValue: false,
      },
    ],
    submitLabel: 'Update Identity',
  }

  // Create identity mutation
  const createIdentityMutation = useMutation({
    mutationFn: (data: any) => api.createIdentity(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['identities'],
        refetchType: 'all'
      })
      toast.success('Identity created successfully')
      setShowCreateModal(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create identity')
    },
  })

  // Update identity mutation
  const updateIdentityMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => api.updateIdentity(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['identities'],
        refetchType: 'all'
      })
      toast.success('Identity updated successfully')
      setShowEditModal(false)
      setSelectedIdentity(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update identity')
    },
  })

  // Create IAM provider mutation
  const createProviderMutation = useMutation({
    mutationFn: (data: any) => api.createIAMProvider(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['iamProviders'],
        refetchType: 'all'
      })
      toast.success('Provider created successfully')
      setShowCreateModal(false)
      // Reset form
      setProviderName('')
      setProviderType('aws_iam')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create provider')
    },
  })

  const handleCreateIdentity = (formData: Record<string, any>) => {
    const identityData: any = {
      username: formData.username,
      email: formData.email,
      full_name: formData.full_name,
      identity_type: formData.identity_type,
      auth_provider: formData.auth_provider,
    }

    // Only include password for local auth provider
    if (formData.auth_provider === 'local' && formData.password) {
      identityData.password = formData.password
    }

    // Include organization and derive tenant_id from it
    if (formData.organization_id) {
      identityData.organization_id = formData.organization_id
      // Get tenant_id from the selected organization
      const selectedOrg = organizations?.items?.find((org: any) => org.id === formData.organization_id)
      if (selectedOrg?.tenant_id) {
        identityData.tenant_id = selectedOrg.tenant_id
      }
    }

    // Include portal user fields if enabled
    if (formData.is_portal_user) {
      identityData.is_portal_user = true
      identityData.portal_role = formData.portal_role
      identityData.must_change_password = formData.must_change_password
    }

    createIdentityMutation.mutate(identityData)
  }

  const handleUpdateIdentity = (formData: Record<string, any>) => {
    if (!selectedIdentity) return

    const updateData: any = {}

    // Only include fields that have been changed
    if (formData.email !== (selectedIdentity.email || '')) {
      updateData.email = formData.email
    }
    if (formData.full_name !== (selectedIdentity.displayName || selectedIdentity.full_name || '')) {
      updateData.full_name = formData.full_name
    }
    if (formData.password) {
      updateData.password = formData.password
    }
    if (formData.is_active !== (selectedIdentity.is_active !== false)) {
      updateData.is_active = formData.is_active
    }
    if (formData.mfa_enabled !== (selectedIdentity.mfa_enabled || false)) {
      updateData.mfa_enabled = formData.mfa_enabled
    }

    // Check if organization changed
    const currentOrgId = selectedIdentity.organization_id || ''
    if (formData.organization_id !== currentOrgId) {
      updateData.organization_id = formData.organization_id || null
      // Derive tenant_id from the selected organization
      if (formData.organization_id) {
        const selectedOrg = organizations?.items?.find((org: any) => org.id === formData.organization_id)
        if (selectedOrg?.tenant_id) {
          updateData.tenant_id = selectedOrg.tenant_id
        }
      }
    }

    // Only submit if there are changes
    if (Object.keys(updateData).length === 0) {
      toast.info('No changes to save')
      return
    }

    updateIdentityMutation.mutate({ id: selectedIdentity.id, data: updateData })
  }

  const handleCreateProvider = (e: React.FormEvent) => {
    e.preventDefault()
    let config: any = {}

    // Build config based on provider type
    switch (providerType) {
      case 'aws_iam':
        config = {
          region: awsRegion,
          access_key_id: awsAccessKeyId,
          secret_access_key: awsSecretAccessKey,
        }
        break
      case 'gcp_iam':
        try {
          config = {
            project_id: gcpProjectId,
            service_account_key: JSON.parse(gcpServiceAccountKey),
          }
        } catch (error) {
          toast.error('Invalid GCP Service Account Key JSON')
          return
        }
        break
      case 'azure_ad':
        config = {
          tenant_id: azureTenantId,
          client_id: azureClientId,
          client_secret: azureClientSecret,
        }
        break
      case 'google_workspace':
        try {
          config = {
            admin_email: googleAdminEmail,
            customer_id: googleCustomerId,
            service_account_key: JSON.parse(googleServiceAccountKey),
          }
        } catch (error) {
          toast.error('Invalid Google Service Account Key JSON')
          return
        }
        break
      case 'kubernetes':
        config = {
          api_server: k8sApiServer,
          token: k8sToken,
          ca_cert: k8sCaCert,
        }
        break
      default:
        toast.error('Unknown provider type')
        return
    }

    createProviderMutation.mutate({
      name: providerName.trim(),
      provider_type: providerType,
      config,
      enabled: true,
    })
  }

  // Aggregate all identities from all sources
  const getAllIdentities = () => {
    const identities: any[] = []

    // Local identities
    if (localIdentities?.items) {
      localIdentities.items.forEach((identity: any) => {
        identities.push({
          ...identity,
          source: 'local',
          sourceLabel: 'Local Database',
          displayName: identity.full_name || identity.username,
          email: identity.email,
          type: identity.identity_type,
          provider_id: null,
        })
      })
    }

    // TODO: Add AWS IAM users (when synced)
    // TODO: Add GCP IAM users (when synced)
    // TODO: Add Azure AD users (when synced)
    // TODO: Add Google Workspace users (when synced)
    // TODO: Add Kubernetes service accounts (when synced)

    return identities
  }

  const getIdentityIcon = (type: string) => {
    const identityType = IDENTITY_TYPES.find(t => t.value === type)
    if (identityType) {
      const Icon = identityType.icon
      return <Icon className={`w-5 h-5 text-${identityType.color}-400`} />
    }
    return <User className="w-5 h-5 text-slate-400" />
  }

  const getIdentityTypeColor = (type: string) => {
    const identityType = IDENTITY_TYPES.find(t => t.value === type)
    return identityType
      ? `bg-${identityType.color}-500/20 text-${identityType.color}-400`
      : 'bg-slate-500/20 text-slate-400'
  }

  const getSourceBadge = (source: string) => {
    const colors: Record<string, string> = {
      local: 'bg-blue-500/20 text-blue-400',
      aws_iam: 'bg-orange-500/20 text-orange-400',
      gcp_iam: 'bg-red-500/20 text-red-400',
      azure_ad: 'bg-cyan-500/20 text-cyan-400',
      google_workspace: 'bg-green-500/20 text-green-400',
      kubernetes: 'bg-purple-500/20 text-purple-400',
    }
    return colors[source] || 'bg-slate-500/20 text-slate-400'
  }

  const filteredIdentities = getAllIdentities().filter(identity => {
    if (providerFilter && identity.source !== providerFilter) return false
    if (searchQuery && !identity.displayName?.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !identity.email?.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Shield className="w-8 h-8 text-primary-400" />
            Identity Center
          </h1>
          <p className="mt-2 text-slate-400">
            Unified view of all identities, users, roles, and permissions across all providers
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="ghost">
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync All
          </Button>
          <Button onClick={() => { setModalType('identity'); setShowCreateModal(true); }}>
            <Plus className="w-4 h-4 mr-2" />
            Add Identity
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Identities</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {filteredIdentities.length}
                </p>
              </div>
              <Users className="w-12 h-12 text-primary-400 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Providers</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {(iamProviders?.providers?.length || 0) + (googleWorkspaceProviders?.providers?.length || 0) + 1}
                </p>
              </div>
              <Cloud className="w-12 h-12 text-blue-400 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Employees</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {filteredIdentities.filter(i => i.type === 'employee').length}
                </p>
              </div>
              <User className="w-12 h-12 text-green-400 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Service Accounts</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {filteredIdentities.filter(i => i.type === 'serviceAccount').length}
                </p>
              </div>
              <Shield className="w-12 h-12 text-orange-400 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-700">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium transition-colors border-b-2 ${
              activeTab === tab
                ? 'text-primary-400 border-primary-400'
                : 'text-slate-400 border-transparent hover:text-slate-300'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* All Identities Tab */}
      {activeTab === 'All Identities' && (
        <div>
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                type="text"
                placeholder="Search identities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select
              value={providerFilter}
              onChange={(e) => setProviderFilter(e.target.value)}
            >
              <option value="">All Providers</option>
              <option value="local">Local Database</option>
              <option value="aws_iam">AWS IAM</option>
              <option value="gcp_iam">GCP IAM</option>
              <option value="azure_ad">Azure AD</option>
              <option value="google_workspace">Google Workspace</option>
              <option value="kubernetes">Kubernetes</option>
            </Select>
            <Select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="">All Types</option>
              {IDENTITY_TYPES.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </Select>
          </div>

          {/* Identities Grid */}
          <div className="grid grid-cols-1 gap-4">
            {filteredIdentities.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Users className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">No identities found</p>
                  <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
                    Add your first identity
                  </Button>
                </CardContent>
              </Card>
            ) : (
              filteredIdentities.map((identity) => (
                <Card
                  key={`${identity.source}-${identity.id}`}
                  className="hover:border-primary-500/50 transition-colors cursor-pointer"
                  onClick={() => {
                    setSelectedIdentity(identity)
                    setShowDetailsModal(true)
                  }}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <div className="mt-1">
                          {getIdentityIcon(identity.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-white">
                              {identity.displayName}
                            </h3>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getIdentityTypeColor(identity.type)}`}>
                              {IDENTITY_TYPES.find(t => t.value === identity.type)?.label || identity.type}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getSourceBadge(identity.source)}`}>
                              {identity.sourceLabel}
                            </span>
                          </div>
                          {identity.email && (
                            <p className="text-sm text-slate-400">{identity.email}</p>
                          )}
                          {identity.username && identity.username !== identity.email && (
                            <p className="text-sm text-slate-500">@{identity.username}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedIdentity(identity)
                            setShowDetailsModal(true)
                          }}
                        >
                          View
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedIdentity(identity)
                            setShowEditModal(true)
                          }}
                        >
                          Edit
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      )}

      {/* Providers Tab */}
      {activeTab === 'Providers' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Local Database Provider (Always present) */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Shield className="w-6 h-6 text-blue-400" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">Local Database</h3>
                    <p className="text-sm text-slate-400">Built-in identity provider</p>
                  </div>
                </div>
                <span className="px-3 py-1 text-xs font-medium rounded bg-green-500/20 text-green-400">
                  Active
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Identities:</span>
                  <span className="text-white font-medium">{localIdentities?.items?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Type:</span>
                  <span className="text-white">PyDAL Database</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* IAM Providers */}
          {iamProviders?.providers?.map((provider: any) => (
            <Card key={provider.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Cloud className="w-6 h-6 text-orange-400" />
                    <div>
                      <h3 className="text-lg font-semibold text-white">{provider.name}</h3>
                      <p className="text-sm text-slate-400">
                        {PROVIDER_TYPES.find(p => p.value === provider.provider_type)?.label || provider.provider_type}
                      </p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 text-xs font-medium rounded ${
                    getStatusColor(provider.enabled ? 'active' : 'inactive')
                  }`}>
                    {provider.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button size="sm" variant="ghost">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Sync
                  </Button>
                  <Button size="sm" variant="ghost">Configure</Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Google Workspace Providers */}
          {googleWorkspaceProviders?.providers?.map((provider: any) => (
            <Card key={provider.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Cloud className="w-6 h-6 text-green-400" />
                    <div>
                      <h3 className="text-lg font-semibold text-white">{provider.name}</h3>
                      <p className="text-sm text-slate-400">Google Workspace</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 text-xs font-medium rounded ${
                    getStatusColor(provider.enabled ? 'active' : 'inactive')
                  }`}>
                    {provider.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Domain:</span>
                    <span className="text-white">{provider.domain}</span>
                  </div>
                  {provider.last_sync_at && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Last Sync:</span>
                      <span className="text-white">{new Date(provider.last_sync_at).toLocaleString()}</span>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="ghost">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Sync
                  </Button>
                  <Button size="sm" variant="ghost">Configure</Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Add Provider Card */}
          <Card className="border-2 border-dashed border-slate-700 hover:border-primary-500/50 transition-colors">
            <CardContent className="p-6 text-center">
              <Plus className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">Add Identity Provider</h3>
              <p className="text-sm text-slate-400 mb-4">
                Connect AWS IAM, GCP, Azure AD, Google Workspace, or Kubernetes
              </p>
              <Button onClick={() => { setModalType('provider'); setShowCreateModal(true); }}>
                Add Provider
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Groups & Roles Tab */}
      {activeTab === 'Groups & Roles' && (
        <GroupMembershipManager />
      )}

      {/* Relationships Tab */}
      {activeTab === 'Relationships' && (
        <Card>
          <CardContent className="text-center py-12">
            <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Identity Relationships</h3>
            <p className="text-slate-400 mb-4">
              Map identities to entities, organizations, and resources
            </p>
            <p className="text-sm text-slate-500">Coming soon in next update</p>
          </CardContent>
        </Card>
      )}

      {/* Create Identity Modal */}
      <ModalFormBuilder
        isOpen={showCreateModal && modalType === 'identity'}
        onClose={() => setShowCreateModal(false)}
        title="Create Identity"
        config={createIdentityFormConfig}
        onSubmit={handleCreateIdentity}
        isLoading={createIdentityMutation.isPending}
      />

      {/* Edit Identity Modal */}
      <ModalFormBuilder
        isOpen={showEditModal && selectedIdentity !== null}
        onClose={() => {
          setShowEditModal(false)
          setSelectedIdentity(null)
        }}
        title="Edit Identity"
        config={editIdentityFormConfig}
        initialValues={selectedIdentity ? {
          email: selectedIdentity.email || '',
          full_name: selectedIdentity.displayName || selectedIdentity.full_name || '',
          organization_id: selectedIdentity.organization_id || '',
          password: '',
          is_active: selectedIdentity.is_active !== false,
          mfa_enabled: selectedIdentity.mfa_enabled || false,
        } : undefined}
        onSubmit={handleUpdateIdentity}
        isLoading={updateIdentityMutation.isPending}
      />

      {/* Create Provider Modal */}
      {showCreateModal && modalType === 'provider' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <h2 className="text-xl font-semibold text-white">Add Identity Provider</h2>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateProvider} className="space-y-4">
                <Input
                  label="Provider Name"
                  required
                  value={providerName}
                  onChange={(e) => setProviderName(e.target.value)}
                  placeholder="Enter provider name"
                />
                <Select
                  label="Provider Type"
                  required
                  value={providerType}
                  onChange={(e) => setProviderType(e.target.value)}
                >
                  {PROVIDER_TYPES.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </Select>

                {/* AWS IAM Fields */}
                {providerType === 'aws_iam' && (
                  <>
                    <Select
                      label="AWS Region"
                      required
                      value={awsRegion}
                      onChange={(e) => setAwsRegion(e.target.value)}
                    >
                      <option value="us-east-1">US East (N. Virginia)</option>
                      <option value="us-east-2">US East (Ohio)</option>
                      <option value="us-west-1">US West (N. California)</option>
                      <option value="us-west-2">US West (Oregon)</option>
                      <option value="eu-west-1">EU (Ireland)</option>
                      <option value="eu-central-1">EU (Frankfurt)</option>
                      <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                      <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
                    </Select>
                    <Input
                      label="Access Key ID"
                      type="text"
                      required
                      value={awsAccessKeyId}
                      onChange={(e) => setAwsAccessKeyId(e.target.value)}
                      placeholder="AKIA..."
                    />
                    <Input
                      label="Secret Access Key"
                      type="password"
                      required
                      value={awsSecretAccessKey}
                      onChange={(e) => setAwsSecretAccessKey(e.target.value)}
                      placeholder="Enter secret key"
                    />
                  </>
                )}

                {/* GCP IAM Fields */}
                {providerType === 'gcp_iam' && (
                  <>
                    <Input
                      label="Project ID"
                      type="text"
                      required
                      value={gcpProjectId}
                      onChange={(e) => setGcpProjectId(e.target.value)}
                      placeholder="my-project-123456"
                    />
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1.5">
                        Service Account Key (JSON)
                      </label>
                      <textarea
                        required
                        value={gcpServiceAccountKey}
                        onChange={(e) => setGcpServiceAccountKey(e.target.value)}
                        placeholder='{"type": "service_account", "project_id": "...", ...}'
                        rows={6}
                        className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500 focus:border-primary-500 font-mono"
                      />
                    </div>
                  </>
                )}

                {/* Azure AD Fields */}
                {providerType === 'azure_ad' && (
                  <>
                    <Input
                      label="Tenant ID"
                      type="text"
                      required
                      value={azureTenantId}
                      onChange={(e) => setAzureTenantId(e.target.value)}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    />
                    <Input
                      label="Client ID (Application ID)"
                      type="text"
                      required
                      value={azureClientId}
                      onChange={(e) => setAzureClientId(e.target.value)}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    />
                    <Input
                      label="Client Secret"
                      type="password"
                      required
                      value={azureClientSecret}
                      onChange={(e) => setAzureClientSecret(e.target.value)}
                      placeholder="Enter client secret"
                    />
                  </>
                )}

                {/* Google Workspace Fields */}
                {providerType === 'google_workspace' && (
                  <>
                    <Input
                      label="Admin Email"
                      type="email"
                      required
                      value={googleAdminEmail}
                      onChange={(e) => setGoogleAdminEmail(e.target.value)}
                      placeholder="admin@company.com"
                    />
                    <Input
                      label="Customer ID"
                      type="text"
                      required
                      value={googleCustomerId}
                      onChange={(e) => setGoogleCustomerId(e.target.value)}
                      placeholder="C012xxxxx"
                    />
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1.5">
                        Service Account Key (JSON)
                      </label>
                      <textarea
                        required
                        value={googleServiceAccountKey}
                        onChange={(e) => setGoogleServiceAccountKey(e.target.value)}
                        placeholder='{"type": "service_account", "project_id": "...", ...}'
                        rows={6}
                        className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500 focus:border-primary-500 font-mono"
                      />
                    </div>
                  </>
                )}

                {/* Kubernetes Fields */}
                {providerType === 'kubernetes' && (
                  <>
                    <Input
                      label="API Server URL"
                      type="text"
                      required
                      value={k8sApiServer}
                      onChange={(e) => setK8sApiServer(e.target.value)}
                      placeholder="https://kubernetes.default.svc"
                    />
                    <Input
                      label="Service Account Token"
                      type="password"
                      required
                      value={k8sToken}
                      onChange={(e) => setK8sToken(e.target.value)}
                      placeholder="eyJhbGci..."
                    />
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1.5">
                        CA Certificate (optional)
                      </label>
                      <textarea
                        value={k8sCaCert}
                        onChange={(e) => setK8sCaCert(e.target.value)}
                        placeholder="-----BEGIN CERTIFICATE-----&#10;...&#10;-----END CERTIFICATE-----"
                        rows={4}
                        className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500 focus:border-primary-500 font-mono"
                      />
                    </div>
                  </>
                )}
                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={createProviderMutation.isPending}
                    className="flex-1"
                  >
                    {createProviderMutation.isPending ? 'Creating...' : 'Add Provider'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Identity Details Modal */}
      {showDetailsModal && selectedIdentity && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader>
              <h2 className="text-xl font-semibold text-white">Identity Details</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-slate-400">Display Name</p>
                    <p className="text-white font-medium">{selectedIdentity.displayName}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Username</p>
                    <p className="text-white font-medium">{selectedIdentity.username}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Email</p>
                    <p className="text-white font-medium">{selectedIdentity.email || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Type</p>
                    <p className="text-white font-medium">
                      {IDENTITY_TYPES.find(t => t.value === selectedIdentity.type)?.label || selectedIdentity.type}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Source</p>
                    <p className="text-white font-medium">{selectedIdentity.sourceLabel}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Status</p>
                    <p className="text-white font-medium">
                      {selectedIdentity.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                </div>

                {selectedIdentity.last_login_at && (
                  <div>
                    <p className="text-sm text-slate-400">Last Login</p>
                    <p className="text-white font-medium">
                      {new Date(selectedIdentity.last_login_at).toLocaleString()}
                    </p>
                  </div>
                )}

                {selectedIdentity.created_at && (
                  <div>
                    <p className="text-sm text-slate-400">Created</p>
                    <p className="text-white font-medium">
                      {new Date(selectedIdentity.created_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>

              <div className="flex gap-3 pt-6">
                <Button
                  variant="ghost"
                  onClick={() => {
                    setShowDetailsModal(false)
                    setSelectedIdentity(null)
                  }}
                  className="flex-1"
                >
                  Close
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
