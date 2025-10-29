import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Cloud, Users, UsersRound, UserPlus, TestTube, Trash2, RefreshCw, Mail } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const TABS = ['Providers', 'Users', 'Groups'] as const
type Tab = typeof TABS[number]

export default function GoogleWorkspace() {
  const [activeTab, setActiveTab] = useState<Tab>('Providers')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState<number | null>(null)
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: providers, isLoading: providersLoading } = useQuery({
    queryKey: ['googleWorkspaceProviders'],
    queryFn: () => api.getGoogleWorkspaceProviders(),
  })

  const { data: users } = useQuery({
    queryKey: ['googleWorkspaceUsers', selectedProvider],
    queryFn: () => api.listGoogleWorkspaceUsers({ provider_id: selectedProvider! }),
    enabled: activeTab === 'Users' && !!selectedProvider,
  })

  const { data: groups } = useQuery({
    queryKey: ['googleWorkspaceGroups', selectedProvider],
    queryFn: () => api.listGoogleWorkspaceGroups({ provider_id: selectedProvider! }),
    enabled: activeTab === 'Groups' && !!selectedProvider,
  })

  const { data: groupMembers } = useQuery({
    queryKey: ['googleWorkspaceGroupMembers', selectedGroup],
    queryFn: () => api.listGoogleWorkspaceGroupMembers({ group_email: selectedGroup! }),
    enabled: !!selectedGroup,
  })

  const testMutation = useMutation({
    mutationFn: (id: number) => api.testGoogleWorkspaceProvider(id),
    onSuccess: () => toast.success('Connection test successful'),
    onError: () => toast.error('Connection test failed'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteGoogleWorkspaceProvider(id),
    onSuccess: () => {
      toast.success('Google Workspace provider deleted')
      queryClient.invalidateQueries({ queryKey: ['googleWorkspaceProviders'] })
      setSelectedProvider(null)
    },
  })

  const syncMutation = useMutation({
    mutationFn: (id: number) => api.syncGoogleWorkspace({ provider_id: id }),
    onSuccess: () => {
      toast.success('Sync started')
      queryClient.invalidateQueries({ queryKey: ['googleWorkspaceUsers'] })
      queryClient.invalidateQueries({ queryKey: ['googleWorkspaceGroups'] })
    },
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Google Workspace</h1>
          <p className="mt-2 text-slate-400">Manage Google Workspace users and groups</p>
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
                <Cloud className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No Google Workspace providers configured</p>
                <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
                  Add your first Google Workspace provider
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
                        <Cloud className="w-5 h-5 text-primary-400" />
                        <div>
                          <h3 className="text-lg font-semibold text-white">{provider.name}</h3>
                          <p className="text-sm text-slate-400">{provider.domain}</p>
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
                        View Users
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
                <p className="text-slate-400">Select a provider to view users</p>
                <Button className="mt-4" onClick={() => setActiveTab('Providers')}>
                  Go to Providers
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Workspace Users</h2>
                <Button size="sm" onClick={() => syncMutation.mutate(selectedProvider)}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Sync
                </Button>
              </div>
              {users?.users?.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-12">
                    <Users className="w-8 h-8 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400">No users found</p>
                  </CardContent>
                </Card>
              ) : (
                users?.users?.map((user: any) => (
                  <Card key={user.id}>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center">
                            {user.photo_url ? (
                              <img src={user.photo_url} alt={user.name} className="w-10 h-10 rounded-full" />
                            ) : (
                              <UserPlus className="w-5 h-5 text-primary-400" />
                            )}
                          </div>
                          <div>
                            <h3 className="text-white font-medium">{user.name}</h3>
                            <p className="text-sm text-slate-400 flex items-center gap-1">
                              <Mail className="w-3 h-3" />
                              {user.email}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {user.is_admin && (
                            <span className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-400 rounded">
                              Admin
                            </span>
                          )}
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            user.suspended ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
                          }`}>
                            {user.suspended ? 'Suspended' : 'Active'}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'Groups' && (
        <div>
          {!selectedProvider ? (
            <Card>
              <CardContent className="text-center py-12">
                <UsersRound className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select a provider to view groups</p>
                <Button className="mt-4" onClick={() => setActiveTab('Providers')}>
                  Go to Providers
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Groups List */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-white">Workspace Groups</h2>
                  <Button size="sm" onClick={() => syncMutation.mutate(selectedProvider)}>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Sync
                  </Button>
                </div>
                <div className="space-y-3">
                  {groups?.groups?.length === 0 ? (
                    <Card>
                      <CardContent className="text-center py-12">
                        <UsersRound className="w-8 h-8 text-slate-600 mx-auto mb-3" />
                        <p className="text-slate-400">No groups found</p>
                      </CardContent>
                    </Card>
                  ) : (
                    groups?.groups?.map((group: any) => (
                      <Card
                        key={group.id}
                        className={`cursor-pointer ${selectedGroup === group.email ? 'ring-2 ring-primary-500' : ''}`}
                        onClick={() => setSelectedGroup(group.email)}
                      >
                        <CardContent>
                          <div>
                            <h3 className="text-white font-medium">{group.name}</h3>
                            <p className="text-sm text-slate-400">{group.email}</p>
                            {group.description && (
                              <p className="text-sm text-slate-500 mt-1">{group.description}</p>
                            )}
                            <p className="text-xs text-slate-500 mt-2">
                              {group.members_count} member{group.members_count !== 1 ? 's' : ''}
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </div>

              {/* Group Members */}
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Group Members</h2>
                {!selectedGroup ? (
                  <Card>
                    <CardContent className="text-center py-12">
                      <UsersRound className="w-8 h-8 text-slate-600 mx-auto mb-3" />
                      <p className="text-slate-400">Select a group to view members</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-3">
                    {groupMembers?.members?.map((member: any) => (
                      <Card key={member.id}>
                        <CardContent>
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="text-white text-sm">{member.email}</h3>
                              <p className="text-xs text-slate-400">{member.role}</p>
                            </div>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              member.status === 'ACTIVE' ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                            }`}>
                              {member.status}
                            </span>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {showCreateModal && (
        <CreateProviderModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['googleWorkspaceProviders'] })
          }}
        />
      )}
    </div>
  )
}

function CreateProviderModal({ onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [domain, setDomain] = useState('')
  const [config, setConfig] = useState('{}')
  const [orgId, setOrgId] = useState('')

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createGoogleWorkspaceProvider(data),
    onSuccess: () => {
      toast.success('Google Workspace provider created')
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
        domain,
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
          <h2 className="text-xl font-semibold text-white">Add Google Workspace Provider</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Company Workspace"
            />
            <Input
              label="Domain"
              required
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="company.com"
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
              <p className="text-xs text-slate-500 mb-2">
                Include service account credentials and delegated admin email
              </p>
              <textarea
                value={config}
                onChange={(e) => setConfig(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono text-sm"
                rows={10}
                placeholder='{"service_account_key": {...}, "delegated_admin": "admin@company.com"}'
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
