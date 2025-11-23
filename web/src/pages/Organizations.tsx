import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Plus, Search, Trash2, Edit } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import type { Organization } from '@/types'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import ModalFormBuilder from '@/components/ModalFormBuilder'
import { FormConfig } from '@/types/form'

export default function Organizations() {
  const [search, setSearch] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const initialParentId = searchParams.get('parent_id')

  // Auto-open create modal if parent_id is in query params
  useEffect(() => {
    if (initialParentId) {
      setShowCreateModal(true)
    }
  }, [initialParentId])

  const { data, isLoading } = useQuery({
    queryKey: ['organizations', search],
    queryFn: () => api.getOrganizations({ search }),
  })

  // Fetch tenants for dropdown
  const { data: tenants } = useQuery({
    queryKey: ['tenants'],
    queryFn: () => api.getTenants(),
  })

  const createMutation = useMutation({
    mutationFn: (data: { name: string; description?: string; parent_id?: number; tenant_id: number }) =>
      api.createOrganization(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['organizations'],
        refetchType: 'all'
      })
      setShowCreateModal(false)
      toast.success('Organization created successfully')
      if (initialParentId) {
        navigate('/organizations', { replace: true })
      }
    },
    onError: (error) => {
      console.error('Create organization error:', error)
      toast.error('Failed to create organization')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { name: string; description?: string; tenant_id?: number } }) =>
      api.updateOrganization(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['organizations'],
        refetchType: 'all'
      })
      setEditingOrg(null)
      toast.success('Organization updated successfully')
    },
    onError: () => {
      toast.error('Failed to update organization')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteOrganization(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['organizations'],
        refetchType: 'all'
      })
      toast.success('Organization deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete organization')
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
      deleteMutation.mutate(id)
    }
  }

  // Form configurations
  const tenantOptions = tenants?.map((tenant: any) => ({
    value: tenant.id,
    label: `${tenant.name}${tenant.id === 1 ? ' (Global)' : ''}`
  })) || []

  const createFormConfig: FormConfig = {
    fields: [
      {
        name: 'name',
        label: 'Name',
        type: 'text',
        required: true,
        placeholder: 'Enter organization name'
      },
      {
        name: 'description',
        label: 'Description',
        type: 'textarea',
        placeholder: 'Enter description (optional)',
        rows: 3
      },
      {
        name: 'tenant_id',
        label: 'Tenant',
        type: 'select',
        required: true,
        options: tenantOptions,
        defaultValue: 1
      }
    ],
    submitLabel: 'Create'
  }

  const editFormConfig: FormConfig = {
    fields: [
      {
        name: 'name',
        label: 'Name',
        type: 'text',
        required: true,
        placeholder: 'Enter organization name'
      },
      {
        name: 'description',
        label: 'Description',
        type: 'textarea',
        placeholder: 'Enter description (optional)',
        rows: 3
      },
      {
        name: 'tenant_id',
        label: 'Tenant',
        type: 'select',
        required: true,
        options: tenantOptions
      }
    ],
    submitLabel: 'Update'
  }

  const handleCreate = (formData: Record<string, any>) => {
    const data: { name: string; description?: string; parent_id?: number; tenant_id: number } = {
      name: formData.name,
      description: formData.description || undefined,
      tenant_id: formData.tenant_id,
    }
    if (initialParentId) {
      data.parent_id = parseInt(initialParentId)
    }
    createMutation.mutate(data)
  }

  const handleUpdate = (formData: Record<string, any>) => {
    if (!editingOrg) return
    updateMutation.mutate({
      id: editingOrg.id,
      data: {
        name: formData.name,
        description: formData.description || undefined,
        tenant_id: formData.tenant_id,
      }
    })
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Organization Units</h1>
          <p className="mt-2 text-slate-400">
            Manage your organizational hierarchy
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Organization Unit
        </Button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search organizations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Organizations List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-400">No organization units found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first organization unit
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data?.items?.map((org: Organization) => (
            <Card key={org.id} className="cursor-pointer hover:ring-2 hover:ring-primary-500 transition-all">
              <CardContent onClick={() => navigate(`/organizations/${org.id}`)}>
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-white">{org.name}</h3>
                  <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => setEditingOrg(org)}
                      className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(org.id, org.name)}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {org.description && (
                  <p className="text-sm text-slate-400 mb-4">{org.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>ID: {org.id}</span>
                  <span>{new Date(org.created_at).toLocaleDateString()}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <ModalFormBuilder
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          if (initialParentId) {
            navigate('/organizations', { replace: true })
          }
        }}
        title="Create Organization Unit"
        config={createFormConfig}
        initialValues={{ tenant_id: 1 }}
        onSubmit={handleCreate}
        isLoading={createMutation.isPending}
      />

      {/* Edit Modal */}
      <ModalFormBuilder
        isOpen={!!editingOrg}
        onClose={() => setEditingOrg(null)}
        title="Edit Organization Unit"
        config={editFormConfig}
        initialValues={editingOrg ? {
          name: editingOrg.name,
          description: editingOrg.description || '',
          tenant_id: editingOrg.tenant_id || 1
        } : undefined}
        onSubmit={handleUpdate}
        isLoading={updateMutation.isPending}
      />
    </div>
  )
}
