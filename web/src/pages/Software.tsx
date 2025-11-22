import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Package, Calendar, DollarSign, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const SOFTWARE_TYPES = [
  { value: 'saas', label: 'SaaS' },
  { value: 'on_premise', label: 'On-Premise' },
  { value: 'desktop', label: 'Desktop' },
  { value: 'mobile', label: 'Mobile' },
  { value: 'open_source', label: 'Open Source' },
  { value: 'other', label: 'Other' },
]

export default function Software() {
  const [search, setSearch] = useState('')
  const [organizationFilter, setOrganizationFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingSoftware, setEditingSoftware] = useState<any>(null)
  const [viewingSoftware, setViewingSoftware] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data: organizations } = useQuery({
    queryKey: ['organizations-all'],
    queryFn: () => api.getOrganizations({ per_page: 1000 }),
  })

  const { data, isLoading } = useQuery({
    queryKey: ['software', { search, organization_id: organizationFilter, software_type: typeFilter }],
    queryFn: () => api.getSoftware({
      search,
      organization_id: organizationFilter ? parseInt(organizationFilter) : undefined,
      software_type: typeFilter || undefined
    }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteSoftware(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['software'],
        refetchType: 'all'
      })
      toast.success('Software deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete software')
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
      deleteMutation.mutate(id)
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'saas':
        return 'bg-blue-500/20 text-blue-400'
      case 'on_premise':
        return 'bg-purple-500/20 text-purple-400'
      case 'desktop':
        return 'bg-green-500/20 text-green-400'
      case 'mobile':
        return 'bg-orange-500/20 text-orange-400'
      case 'open_source':
        return 'bg-cyan-500/20 text-cyan-400'
      default:
        return 'bg-slate-500/20 text-slate-400'
    }
  }

  const formatCurrency = (amount: number | null) => {
    if (amount === null || amount === undefined) return '-'
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Software</h1>
          <p className="mt-2 text-slate-400">
            Track and manage software licenses and subscriptions
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Software
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <Input
              type="text"
              placeholder="Search software..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select
          value={organizationFilter}
          onChange={(e) => setOrganizationFilter(e.target.value)}
          className="w-48"
        >
          <option value="">All Organizations</option>
          {organizations?.items?.map((org: any) => (
            <option key={org.id} value={org.id}>
              {org.name}
            </option>
          ))}
        </Select>
        <Select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="w-48"
        >
          <option value="">All Types</option>
          {SOFTWARE_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </Select>
      </div>

      {/* Software List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Package className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No software found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Add your first software
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.items?.map((software: any) => (
            <Card
              key={software.id}
              className="cursor-pointer hover:border-primary-500/50 transition-colors"
              onClick={() => setViewingSoftware(software)}
            >
              <CardContent>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <Package className="w-5 h-5 text-primary-400 flex-shrink-0" />
                    <h3 className="text-lg font-semibold text-white truncate">
                      {software.name}
                    </h3>
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setEditingSoftware(software)
                      }}
                      className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(software.id, software.name)
                      }}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {software.vendor && (
                  <p className="text-sm text-slate-400 mb-2">
                    {software.vendor}
                  </p>
                )}

                <div className="flex items-center justify-between mb-3">
                  <span className={`text-xs px-2 py-1 rounded ${getTypeColor(software.software_type)}`}>
                    {software.software_type?.replace('_', ' ')}
                  </span>
                  {software.version && (
                    <span className="text-xs text-slate-500">
                      v{software.version}
                    </span>
                  )}
                </div>

                <div className="space-y-1 text-xs text-slate-400">
                  {software.seats && (
                    <div>Seats: {software.seats}</div>
                  )}
                  {software.cost_monthly !== null && software.cost_monthly !== undefined && (
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-3 h-3" />
                      {formatCurrency(software.cost_monthly)}/mo
                    </div>
                  )}
                  {software.renewal_date && (
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      Renews: {new Date(software.renewal_date).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <SoftwareModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={async () => {
            await queryClient.invalidateQueries({
              queryKey: ['software'],
              refetchType: 'all'
            })
            setShowCreateModal(false)
          }}
        />
      )}

      {/* Edit Modal */}
      {editingSoftware && (
        <SoftwareModal
          software={editingSoftware}
          onClose={() => setEditingSoftware(null)}
          onSuccess={async () => {
            await queryClient.invalidateQueries({
              queryKey: ['software'],
              refetchType: 'all'
            })
            setEditingSoftware(null)
          }}
        />
      )}

      {/* View Details Modal */}
      {viewingSoftware && (
        <SoftwareDetailModal
          software={viewingSoftware}
          onClose={() => setViewingSoftware(null)}
          onEdit={() => {
            setEditingSoftware(viewingSoftware)
            setViewingSoftware(null)
          }}
        />
      )}
    </div>
  )
}

interface SoftwareModalProps {
  software?: any
  onClose: () => void
  onSuccess: () => void
}

function SoftwareModal({ software, onClose, onSuccess }: SoftwareModalProps) {
  const [name, setName] = useState(software?.name || '')
  const [vendor, setVendor] = useState(software?.vendor || '')
  const [softwareType, setSoftwareType] = useState(software?.software_type || 'saas')
  const [version, setVersion] = useState(software?.version || '')
  const [seats, setSeats] = useState(software?.seats?.toString() || '')
  const [costMonthly, setCostMonthly] = useState(software?.cost_monthly?.toString() || '')
  const [renewalDate, setRenewalDate] = useState(software?.renewal_date || '')
  const [licenseUrl, setLicenseUrl] = useState(software?.license_url || '')
  const [organizationId, setOrganizationId] = useState(software?.organization_id?.toString() || '')

  const { data: organizations, isLoading: orgsLoading } = useQuery({
    queryKey: ['organizations-all'],
    queryFn: () => api.getOrganizations({ per_page: 1000 }),
  })

  const mutation = useMutation({
    mutationFn: (data: any) =>
      software
        ? api.updateSoftware(software.id, data)
        : api.createSoftware(data),
    onSuccess: () => {
      toast.success(software ? 'Software updated successfully' : 'Software added successfully')
      onSuccess()
    },
    onError: () => {
      toast.error(software ? 'Failed to update software' : 'Failed to add software')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      name,
      vendor: vendor || undefined,
      software_type: softwareType,
      version: version || undefined,
      seats: seats ? parseInt(seats) : undefined,
      cost_monthly: costMonthly ? parseFloat(costMonthly) : undefined,
      renewal_date: renewalDate || undefined,
      license_url: licenseUrl || undefined,
      organization_id: parseInt(organizationId),
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">
            {software ? 'Edit Software' : 'Add Software'}
          </h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Microsoft 365"
            />
            <Input
              label="Vendor"
              value={vendor}
              onChange={(e) => setVendor(e.target.value)}
              placeholder="Microsoft"
            />
            <Select
              label="Organization"
              required
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
            >
              <option value="">
                {orgsLoading ? 'Loading...' : organizations?.items?.length ? 'Select organization' : 'No organizations found'}
              </option>
              {organizations?.items?.map((org: any) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </Select>
            <Select
              label="Software Type"
              value={softwareType}
              onChange={(e) => setSoftwareType(e.target.value)}
            >
              {SOFTWARE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </Select>
            <Input
              label="Version"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              placeholder="2024.1"
            />
            <Input
              label="Seats"
              type="number"
              value={seats}
              onChange={(e) => setSeats(e.target.value)}
              placeholder="50"
            />
            <Input
              label="Monthly Cost"
              type="number"
              step="0.01"
              value={costMonthly}
              onChange={(e) => setCostMonthly(e.target.value)}
              placeholder="500.00"
            />
            <Input
              label="Renewal Date"
              type="date"
              value={renewalDate}
              onChange={(e) => setRenewalDate(e.target.value)}
            />
            <Input
              label="License URL"
              type="url"
              value={licenseUrl}
              onChange={(e) => setLicenseUrl(e.target.value)}
              placeholder="https://portal.vendor.com/license"
            />
            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" isLoading={mutation.isPending}>
                {software ? 'Update' : 'Add'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

interface SoftwareDetailModalProps {
  software: any
  onClose: () => void
  onEdit: () => void
}

function SoftwareDetailModal({ software, onClose, onEdit }: SoftwareDetailModalProps) {
  const formatCurrency = (amount: number | null) => {
    if (amount === null || amount === undefined) return '-'
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">{software.name}</h2>
            <Button variant="ghost" size="sm" onClick={onEdit}>
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-slate-500 uppercase">Vendor</label>
                <p className="text-white">{software.vendor || '-'}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500 uppercase">Type</label>
                <p className="text-white capitalize">{software.software_type?.replace('_', ' ') || '-'}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500 uppercase">Version</label>
                <p className="text-white">{software.version || '-'}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500 uppercase">Seats</label>
                <p className="text-white">{software.seats || '-'}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500 uppercase">Monthly Cost</label>
                <p className="text-white">{formatCurrency(software.cost_monthly)}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500 uppercase">Renewal Date</label>
                <p className="text-white">
                  {software.renewal_date
                    ? new Date(software.renewal_date).toLocaleDateString()
                    : '-'}
                </p>
              </div>
            </div>

            {software.license_url && (
              <div>
                <label className="text-xs text-slate-500 uppercase">License URL</label>
                <a
                  href={software.license_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-primary-400 hover:text-primary-300"
                >
                  {software.license_url}
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}

            <div className="flex justify-end pt-4">
              <Button variant="ghost" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
