import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Shield, Users, FileKey, ScrollText, TestTube, Trash2, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const PROVIDER_TYPES = [
  { value: 'aws_iam', label: 'AWS IAM' },
  { value: 'gcp_iam', label: 'GCP IAM' },
  { value: 'kubernetes', label: 'Kubernetes RBAC' },
  { value: 'azure_ad', label: 'Azure AD (Microsoft Entra ID)' },
]

const TABS = ['Providers', 'Users', 'Roles', 'Policies'] as const
type Tab = typeof TABS[number]

export default function IAM() {
  const [activeTab, setActiveTab] = useState<Tab>('Providers')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: providers, isLoading: providersLoading } = useQuery({
    queryKey: ['iamProviders'],
    queryFn: () => api.getIAMProviders(),
  })

  const { data: users } = useQuery({
    queryKey: ['iamUsers', selectedProvider],
    queryFn: () => api.listIAMUsers({ provider_id: selectedProvider! }),
    enabled: activeTab === 'Users' && !!selectedProvider,
  })

  const { data: roles } = useQuery({
    queryKey: ['iamRoles', selectedProvider],
    queryFn: () => api.listIAMRoles({ provider_id: selectedProvider! }),
    enabled: activeTab === 'Roles' && !!selectedProvider,
  })

  const { data: policies } = useQuery({
    queryKey: ['iamPolicies', selectedProvider],
    queryFn: () => api.listIAMPolicies({ provider_id: selectedProvider! }),
    enabled: activeTab === 'Policies' && !!selectedProvider,
  })

  const testMutation = useMutation({
    mutationFn: (id: number) => api.testIAMProvider(id),
    onSuccess: () => toast.success('Connection test successful'),
    onError: () => toast.error('Connection test failed'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteIAMProvider(id),
    onSuccess: () => {
      toast.success('IAM provider deleted')
      queryClient.invalidateQueries({ queryKey: ['iamProviders'] })
      setSelectedProvider(null)
    },
  })

  const syncMutation = useMutation({
    mutationFn: (id: number) => api.syncIAM({ provider_id: id }),
    onSuccess: () => {
      toast.success('IAM sync started')
      queryClient.invalidateQueries({ queryKey: ['iamUsers'] })
      queryClient.invalidateQueries({ queryKey: ['iamRoles'] })
      queryClient.invalidateQueries({ queryKey: ['iamPolicies'] })
    },
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">IAM Integration</h1>
          <p className="mt-2 text-slate-400">Manage IAM users, roles, and policies across all identity providers</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Provider
        </Button>
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

      {activeTab === 'Providers' && (
        <div>
          {providersLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : providers?.providers?.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Shield className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No IAM providers configured</p>
                <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
                  Add your first IAM provider
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {providers?.providers?.map((provider: any) => (
                <Card key={provider.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Shield className="w-5 h-5 text-primary-400" />
                        <div>
                          <h3 className="text-lg font-semibold text-white">{provider.name}</h3>
                          <p className="text-sm text-slate-400">
                            {PROVIDER_TYPES.find(t => t.value === provider.provider_type)?.label}
                          </p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        provider.enabled ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {provider.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => {
                          setSelectedProvider(provider.id)
                          setActiveTab('Users')
                        }}
                      >
                        <Users className="w-4 h-4 mr-2" />
                        View IAM
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => syncMutation.mutate(provider.id)}>
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => testMutation.mutate(provider.id)}>
                        <TestTube className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => deleteMutation.mutate(provider.id)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'Users' && (
        <div>
          {!selectedProvider ? (
            <Card>
              <CardContent className="text-center py-12">
                <Users className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select a provider to view IAM users</p>
                <Button className="mt-4" onClick={() => setActiveTab('Providers')}>
                  Go to Providers
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">IAM Users</h2>
                <Button size="sm" onClick={() => syncMutation.mutate(selectedProvider)}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync
                </Button>
              </div>
              {users?.users?.map((user: any) => (
                <Card key={user.id}>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-white font-medium">{user.name || user.username}</h3>
                        <p className="text-sm text-slate-400">{user.email || user.arn}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        user.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {user.status || 'active'}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'Roles' && (
        <div>
          {!selectedProvider ? (
            <Card>
              <CardContent className="text-center py-12">
                <FileKey className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select a provider to view IAM roles</p>
                <Button className="mt-4" onClick={() => setActiveTab('Providers')}>
                  Go to Providers
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">IAM Roles</h2>
                <Button size="sm" onClick={() => syncMutation.mutate(selectedProvider)}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync
                </Button>
              </div>
              {roles?.roles?.map((role: any) => (
                <Card key={role.id}>
                  <CardContent>
                    <div>
                      <h3 className="text-white font-medium">{role.name}</h3>
                      <p className="text-sm text-slate-400">{role.description || role.arn}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'Policies' && (
        <div>
          {!selectedProvider ? (
            <Card>
              <CardContent className="text-center py-12">
                <ScrollText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select a provider to view IAM policies</p>
                <Button className="mt-4" onClick={() => setActiveTab('Providers')}>
                  Go to Providers
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">IAM Policies</h2>
                <Button size="sm" onClick={() => syncMutation.mutate(selectedProvider)}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync
                </Button>
              </div>
              {policies?.policies?.map((policy: any) => (
                <Card key={policy.id}>
                  <CardContent>
                    <div>
                      <h3 className="text-white font-medium">{policy.name}</h3>
                      <p className="text-sm text-slate-400">{policy.description || policy.arn}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {showCreateModal && (
        <CreateProviderModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['iamProviders'] })
          }}
        />
      )}
    </div>
  )
}

function CreateProviderModal({ onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [providerType, setProviderType] = useState('')
  const [config, setConfig] = useState('{}')
  const [orgId, setOrgId] = useState('')

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createIAMProvider(data),
    onSuccess: () => {
      toast.success('IAM provider created')
      onSuccess()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create provider')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const configObj = JSON.parse(config)
      createMutation.mutate({
        name,
        provider_type: providerType,
        organization_id: parseInt(orgId),
        config: configObj,
        enabled: true,
      })
    } catch (err) {
      toast.error('Invalid JSON configuration')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Add IAM Provider</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Production IAM"
            />
            <Select
              label="Provider Type"
              required
              value={providerType}
              onChange={(e) => setProviderType(e.target.value)}
              options={[
                { value: '', label: 'Select provider type' },
                ...PROVIDER_TYPES,
              ]}
            />
            <Select
              label="Organization"
              required
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              options={[
                { value: '', label: 'Select organization' },
                ...(orgs?.items || []).map((o: any) => ({ value: o.id, label: o.name })),
              ]}
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Configuration (JSON)
              </label>
              <textarea
                value={config}
                onChange={(e) => setConfig(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono text-sm"
                rows={8}
                placeholder='{"region": "us-east-1", "access_key_id": "...", "secret_access_key": "..."}'
              />
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
              <Button type="submit" isLoading={createMutation.isPending}>Create</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
