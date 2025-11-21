import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Plus, Search, Building2, Users, Trash2, Edit, Eye } from 'lucide-react'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Card, { CardHeader, CardContent } from '@/components/Card'
import type { Tenant } from '@/types'

export default function Tenants() {
  const [search, setSearch] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    domain: '',
    subscription_tier: 'community',
    data_retention_days: 90,
    storage_quota_gb: 10,
  })
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: tenants, isLoading } = useQuery({
    queryKey: ['tenants'],
    queryFn: () => api.getTenants(),
  })

  const createMutation = useMutation({
    mutationFn: (data: typeof formData) => api.createTenant(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['tenants'] })
      toast.success('Tenant created successfully')
      setShowCreateModal(false)
      resetForm()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create tenant')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<typeof formData> }) =>
      api.updateTenant(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['tenants'] })
      toast.success('Tenant updated successfully')
      setEditingTenant(null)
      resetForm()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update tenant')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteTenant(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['tenants'] })
      toast.success('Tenant deactivated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to deactivate tenant')
    },
  })

  const resetForm = () => {
    setFormData({
      name: '',
      slug: '',
      domain: '',
      subscription_tier: 'community',
      data_retention_days: 90,
      storage_quota_gb: 10,
    })
  }

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const handleUpdate = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingTenant) {
      updateMutation.mutate({ id: editingTenant.id, data: formData })
    }
  }

  const handleEdit = (tenant: Tenant) => {
    setEditingTenant(tenant)
    setFormData({
      name: tenant.name,
      slug: tenant.slug,
      domain: tenant.domain || '',
      subscription_tier: tenant.subscription_tier,
      data_retention_days: tenant.data_retention_days,
      storage_quota_gb: tenant.storage_quota_gb,
    })
  }

  const handleDelete = (tenant: Tenant) => {
    if (tenant.id === 1) {
      toast.error('Cannot deactivate system tenant')
      return
    }
    if (confirm(`Are you sure you want to deactivate "${tenant.name}"?`)) {
      deleteMutation.mutate(tenant.id)
    }
  }

  const filteredTenants = tenants?.filter((t: Tenant) =>
    t.name.toLowerCase().includes(search.toLowerCase()) ||
    t.slug.toLowerCase().includes(search.toLowerCase())
  ) || []

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'enterprise': return 'bg-yellow-500/20 text-yellow-400'
      case 'professional': return 'bg-blue-500/20 text-blue-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">Tenant Management</h1>
        <p className="text-slate-400">Manage multi-tenant organizations and their configurations</p>
      </div>

      <div className="flex justify-between items-center mb-6">
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Search tenants..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Tenant
        </Button>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-slate-400">Loading tenants...</div>
      ) : filteredTenants.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Building2 className="w-12 h-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No tenants found</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredTenants.map((tenant: Tenant) => (
            <Card key={tenant.id} className="hover:border-slate-600 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-slate-400" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-white">{tenant.name}</h3>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getTierColor(tenant.subscription_tier)}`}>
                          {tenant.subscription_tier}
                        </span>
                        {!tenant.is_active && (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-500/20 text-red-400">
                            Inactive
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-400">
                        {tenant.slug} {tenant.domain && `• ${tenant.domain}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {tenant.usage && (
                      <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {tenant.usage.portal_users} users
                        </span>
                        <span>{tenant.usage.organizations} orgs</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(`/admin/tenants/${tenant.id}`)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(tenant)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      {tenant.id !== 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(tenant)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {(showCreateModal || editingTenant) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-white mb-4">
              {editingTenant ? 'Edit Tenant' : 'Create Tenant'}
            </h3>
            <form onSubmit={editingTenant ? handleUpdate : handleCreate} className="space-y-4">
              <Input
                label="Name"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Tenant name"
              />
              <Input
                label="Slug"
                required
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                placeholder="tenant-slug"
              />
              <Input
                label="Domain (optional)"
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                placeholder="tenant.example.com"
              />
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Subscription Tier
                </label>
                <select
                  value={formData.subscription_tier}
                  onChange={(e) => setFormData({ ...formData, subscription_tier: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500"
                >
                  <option value="community">Community</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              <Input
                label="Data Retention (days)"
                type="number"
                value={formData.data_retention_days}
                onChange={(e) => setFormData({ ...formData, data_retention_days: parseInt(e.target.value) })}
              />
              <Input
                label="Storage Quota (GB)"
                type="number"
                value={formData.storage_quota_gb}
                onChange={(e) => setFormData({ ...formData, storage_quota_gb: parseInt(e.target.value) })}
              />
              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  className="flex-1"
                  isLoading={createMutation.isPending || updateMutation.isPending}
                >
                  {editingTenant ? 'Save Changes' : 'Create Tenant'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="flex-1"
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingTenant(null)
                    resetForm()
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
