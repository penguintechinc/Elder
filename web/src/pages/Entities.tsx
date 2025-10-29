import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Plus, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

export default function Entities() {
  const [search, setSearch] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const initialOrgId = searchParams.get('organization_id')

  // Auto-open create modal if organization_id is in query params
  useEffect(() => {
    if (initialOrgId) {
      setShowCreateModal(true)
    }
  }, [initialOrgId])

  const { data, isLoading } = useQuery({
    queryKey: ['entities', { search }],
    queryFn: () => api.getEntities({ search }),
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Entities</h1>
          <p className="mt-2 text-slate-400">Manage infrastructure and resources</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Entity
        </Button>
      </div>

      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search entities..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-400">No entities found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first entity
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data?.items?.map((entity: any) => (
            <Card
              key={entity.id}
              className="cursor-pointer hover:ring-2 hover:ring-primary-500 transition-all"
              onClick={() => navigate(`/entities/${entity.id}`)}
            >
              <CardContent>
                <h3 className="text-lg font-semibold text-white mb-2">{entity.name}</h3>
                <div className="flex gap-2 flex-wrap mb-3">
                  <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-500/20 text-primary-400 rounded">
                    {entity.entity_type.replace('_', ' ').toUpperCase()}
                  </span>
                  {entity.entity_sub_type && (
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-400 rounded">
                      {entity.entity_sub_type.replace('_', ' ').toUpperCase()}
                    </span>
                  )}
                </div>
                {entity.description && (
                  <p className="text-sm text-slate-400 mt-3">{entity.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-slate-500 mt-4">
                  <span>ID: {entity.id}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreateEntityModal
          initialOrganizationId={initialOrgId}
          onClose={() => {
            setShowCreateModal(false)
            // Clear query params when closing modal
            if (initialOrgId) {
              navigate('/entities', { replace: true })
            }
          }}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['entities'] })
            // Clear query params on success
            if (initialOrgId) {
              navigate('/entities', { replace: true })
            }
          }}
        />
      )}
    </div>
  )
}

function CreateEntityModal({ initialOrganizationId, onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [entityCategory, setEntityCategory] = useState('')
  const [entitySubType, setEntitySubType] = useState('')
  const [orgId, setOrgId] = useState(initialOrganizationId || '')

  // Fetch entity types from API
  const { data: entityTypesData } = useQuery({
    queryKey: ['entityTypes'],
    queryFn: () => api.getEntityTypes(),
  })

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  // Group entity types by category
  const categorizedTypes: Record<string, any[]> = {}
  if (entityTypesData?.items) {
    entityTypesData.items.forEach((type: any) => {
      if (!categorizedTypes[type.category]) {
        categorizedTypes[type.category] = []
      }
      categorizedTypes[type.category].push(type)
    })
  }

  // Get category options
  const categoryOptions = Object.keys(categorizedTypes).map(cat => ({
    value: cat,
    label: cat.charAt(0).toUpperCase() + cat.slice(1).replace('_', ' ')
  }))

  // Get sub-type options for selected category
  const subTypeOptions = entityCategory && categorizedTypes[entityCategory]
    ? categorizedTypes[entityCategory].map(type => ({
        value: type.sub_type || type.name,
        label: (type.sub_type || type.name).replace('_', ' ').split(' ').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
      }))
    : []

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createEntity(data),
    onSuccess: () => {
      toast.success('Entity created successfully')
      onSuccess()
    },
    onError: () => {
      toast.error('Failed to create entity')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      name,
      description: description || undefined,
      entity_type: entityCategory,
      entity_sub_type: entitySubType || undefined,
      organization_id: parseInt(orgId),
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Create Entity</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <Select
              label="Category"
              required
              value={entityCategory}
              onChange={(e) => {
                setEntityCategory(e.target.value)
                setEntitySubType('') // Reset sub-type when category changes
              }}
              options={[
                { value: '', label: 'Select category' },
                ...categoryOptions
              ]}
            />
            {entityCategory && subTypeOptions.length > 0 && (
              <Select
                label="Sub-Type"
                value={entitySubType}
                onChange={(e) => setEntitySubType(e.target.value)}
                options={[
                  { value: '', label: 'None' },
                  ...subTypeOptions
                ]}
              />
            )}
            <Select
              label="Organization"
              required
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              options={[
                { value: '', label: 'Select organization' },
                ...(orgs?.items || []).map((o: any) => ({
                  value: o.id,
                  label: o.name,
                })),
              ]}
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500"
              />
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" isLoading={createMutation.isPending}>
                Create
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
