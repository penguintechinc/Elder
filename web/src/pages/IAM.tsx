import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Shield, Users, User, Bot, Building2, Cloud, RefreshCw, Search, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const TABS = ['All Identities', 'Providers', 'Groups & Roles', 'Relationships'] as const
type Tab = typeof TABS[number]

const PROVIDER_TYPES = [
  { value: 'local', label: 'Local Database', icon: Shield },
  { value: 'aws_iam', label: 'AWS IAM', icon: Cloud },
  { value: 'gcp_iam', label: 'GCP IAM', icon: Cloud },
  { value: 'azure_ad', label: 'Azure AD', icon: Building2 },
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
  const queryClient = useQueryClient()

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

  const getTypeColor = (type: string) => {
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
          <Button onClick={() => setShowCreateModal(true)}>
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
                <Card key={`${identity.source}-${identity.id}`} className="hover:border-primary-500/50 transition-colors">
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
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getTypeColor(identity.type)}`}>
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
                        <Button size="sm" variant="ghost">View Details</Button>
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
                    provider.enabled ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
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
                    provider.enabled ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
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
              <Button onClick={() => setShowCreateModal(true)}>
                Add Provider
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Groups & Roles Tab */}
      {activeTab === 'Groups & Roles' && (
        <Card>
          <CardContent className="text-center py-12">
            <Users className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Groups & Roles</h3>
            <p className="text-slate-400 mb-4">
              View and manage groups, roles, and permissions across all identity providers
            </p>
            <p className="text-sm text-slate-500">Coming soon in next update</p>
          </CardContent>
        </Card>
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
    </div>
  )
}
