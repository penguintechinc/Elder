import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Network, Trash2, Link2, Activity } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'
import NetworkTopologyGraph from '@/components/NetworkTopologyGraph'

const NETWORK_TYPES = [
  { value: 'subnet', label: 'Subnet' },
  { value: 'firewall', label: 'Firewall' },
  { value: 'proxy', label: 'Proxy' },
  { value: 'router', label: 'Router' },
  { value: 'switch', label: 'Switch' },
  { value: 'hub', label: 'Hub' },
  { value: 'tunnel', label: 'Tunnel' },
  { value: 'route_table', label: 'Route Table' },
  { value: 'vrrf', label: 'VRRF' },
  { value: 'vxlan', label: 'VXLAN' },
  { value: 'vlan', label: 'VLAN' },
  { value: 'namespace', label: 'Namespace' },
  { value: 'other', label: 'Other' },
]

const TABS = ['Networks', 'Topology', 'Connections'] as const
type Tab = typeof TABS[number]

export default function Networking() {
  const [activeTab, setActiveTab] = useState<Tab>('Networks')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showTopologyModal, setShowTopologyModal] = useState(false)
  const [selectedOrg, setSelectedOrg] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: networks, isLoading: networksLoading } = useQuery({
    queryKey: ['networks', selectedOrg],
    queryFn: () => api.listNetworks({ organization_id: selectedOrg || undefined }),
    enabled: !!selectedOrg,
  })

  const { data: connections } = useQuery({
    queryKey: ['networkConnections'],
    queryFn: () => api.listTopologyConnections(),
    enabled: activeTab === 'Connections',
  })

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteNetwork(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['networks'],
        refetchType: 'all'
      })
      toast.success('Network deleted')
    },
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Network Topology</h1>
          <p className="mt-2 text-slate-400">Manage networking resources and visualize topology</p>
        </div>
        <div className="flex gap-3">
          <Button variant="ghost" onClick={() => setShowTopologyModal(true)}>
            <Activity className="w-4 h-4 mr-2" />
            View Topology
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Network
          </Button>
        </div>
      </div>

      {/* Organization Selector */}
      <div className="mb-6 max-w-md">
        <Select
          label="Organization"
          value={selectedOrg?.toString() || ''}
          onChange={(e) => setSelectedOrg(parseInt(e.target.value))}
          options={[
            { value: '', label: 'Select organization' },
            ...(orgs?.items || []).map((o: any) => ({ value: o.id, label: o.name })),
          ]}
        />
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

      {activeTab === 'Networks' && (
        <div>
          {!selectedOrg ? (
            <Card>
              <CardContent className="text-center py-12">
                <Network className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select an organization to view networks</p>
              </CardContent>
            </Card>
          ) : networksLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : networks?.networks?.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Network className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No networks configured</p>
                <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
                  Add your first network
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {networks?.networks?.map((network: any) => (
                <Card key={network.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Network className="w-5 h-5 text-primary-400" />
                        <div>
                          <h3 className="text-lg font-semibold text-white">{network.name}</h3>
                          <p className="text-sm text-slate-400">
                            {NETWORK_TYPES.find(t => t.value === network.network_type)?.label}
                          </p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        network.is_active ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {network.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {network.description && (
                      <p className="text-sm text-slate-400 mb-3">{network.description}</p>
                    )}
                    {network.region && (
                      <p className="text-sm text-slate-500">Region: {network.region}</p>
                    )}
                    {network.location && (
                      <p className="text-sm text-slate-500">Location: {network.location}</p>
                    )}
                    <div className="flex gap-2 mt-4">
                      <Button size="sm" variant="ghost" onClick={() => deleteMutation.mutate(network.id)}>
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

      {activeTab === 'Topology' && (
        <div>
          {!selectedOrg ? (
            <Card>
              <CardContent className="text-center py-12">
                <Activity className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select an organization to view network topology</p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-0">
                <NetworkTopologyGraph organizationId={selectedOrg} />
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'Connections' && (
        <div className="space-y-3">
          {connections?.connections?.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Link2 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No network connections configured</p>
              </CardContent>
            </Card>
          ) : (
            connections?.connections?.map((conn: any) => (
              <Card key={conn.id}>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Link2 className="w-5 h-5 text-primary-400" />
                      <div>
                        <p className="text-white font-medium">{conn.connection_type}</p>
                        <p className="text-sm text-slate-400">
                          Network {conn.source_network_id} → Network {conn.target_network_id}
                        </p>
                      </div>
                    </div>
                    <div className="text-right text-sm">
                      {conn.bandwidth && <p className="text-slate-400">Bandwidth: {conn.bandwidth}</p>}
                      {conn.latency && <p className="text-slate-400">Latency: {conn.latency}ms</p>}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {showCreateModal && (
        <CreateNetworkModal
          organizationId={selectedOrg}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
          }}
        />
      )}

      {showTopologyModal && selectedOrg && (
        <TopologyModal
          organizationId={selectedOrg}
          onClose={() => setShowTopologyModal(false)}
        />
      )}
    </div>
  )
}

function CreateNetworkModal({ organizationId: initialOrgId, onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [networkType, setNetworkType] = useState('')
  const [description, setDescription] = useState('')
  const [region, setRegion] = useState('')
  const [location, setLocation] = useState('')
  const [organizationId, setOrganizationId] = useState(initialOrgId || '')

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createNetwork(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['networks'],
        refetchType: 'all'
      })
      toast.success('Network created')
      onSuccess()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create network')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!organizationId) {
      toast.error('Please select an organization first')
      return
    }
    createMutation.mutate({
      name,
      network_type: networkType,
      organization_id: parseInt(organizationId),
      description,
      region,
      location,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Add Network Resource</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Select
              label="Organization"
              required
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              options={[
                { value: '', label: 'Select organization' },
                ...(orgs?.items || []).map((o: any) => ({ value: o.id, label: o.name })),
              ]}
            />
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Production VPC"
            />
            <Select
              label="Network Type"
              required
              value={networkType}
              onChange={(e) => setNetworkType(e.target.value)}
              options={[
                { value: '', label: 'Select network type' },
                ...NETWORK_TYPES,
              ]}
            />
            <Input
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Main production network"
            />
            <Input
              label="Region"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder="us-east-1"
            />
            <Input
              label="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="AWS Virginia"
            />
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

function TopologyModal({ organizationId, onClose }: any) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Network Topology Visualization</h2>
            <Button variant="ghost" onClick={onClose}>Close</Button>
          </div>
        </CardHeader>
        <CardContent className="flex-1 p-0">
          <NetworkTopologyGraph organizationId={organizationId} />
        </CardContent>
      </Card>
    </div>
  )
}
