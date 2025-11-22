import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Trash2, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import type { DependencyType } from '@/types'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

// Resource types supported by dependencies
const RESOURCE_TYPES = [
  { value: 'entity', label: 'Entity' },
  { value: 'identity', label: 'Identity' },
  { value: 'project', label: 'Project' },
  { value: 'milestone', label: 'Milestone' },
  { value: 'issue', label: 'Issue' },
  { value: 'organization', label: 'Organization' },
]

interface PolymorphicDependency {
  id: number
  tenant_id: number
  source_type: string
  source_id: number
  target_type: string
  target_id: number
  dependency_type: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export default function Dependencies() {
  const [search, setSearch] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [sourceTypeFilter, setSourceTypeFilter] = useState<string>('')
  const [targetTypeFilter, setTargetTypeFilter] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: dependencies, isLoading } = useQuery({
    queryKey: ['dependencies', { sourceTypeFilter, targetTypeFilter }],
    queryFn: () =>
      api.getDependencies({
        source_type: sourceTypeFilter || undefined,
        target_type: targetTypeFilter || undefined,
      }),
  })

  // Fetch all resource types for display names
  const { data: entities } = useQuery({
    queryKey: ['entities-all'],
    queryFn: () => api.getEntities({ per_page: 1000 }),
  })

  const { data: identities } = useQuery({
    queryKey: ['identities-all'],
    queryFn: () => api.getIdentities({ per_page: 1000 }),
  })

  const { data: projects } = useQuery({
    queryKey: ['projects-all'],
    queryFn: () => api.getProjects({ per_page: 1000 }),
  })

  const { data: milestones } = useQuery({
    queryKey: ['milestones-all'],
    queryFn: () => api.getMilestones({ per_page: 1000 }),
  })

  const { data: issues } = useQuery({
    queryKey: ['issues-all'],
    queryFn: () => api.getIssues({ per_page: 1000 }),
  })

  const { data: organizations } = useQuery({
    queryKey: ['organizations-all'],
    queryFn: () => api.getOrganizations({ per_page: 1000 }),
  })

  // Helper to get resource name by type and id
  const getResourceName = (type: string, id: number): string => {
    switch (type) {
      case 'entity':
        return entities?.items?.find((e: any) => e.id === id)?.name || `Entity #${id}`
      case 'identity':
        return identities?.items?.find((i: any) => i.id === id)?.username || `Identity #${id}`
      case 'project':
        return projects?.items?.find((p: any) => p.id === id)?.name || `Project #${id}`
      case 'milestone':
        return milestones?.items?.find((m: any) => m.id === id)?.title || `Milestone #${id}`
      case 'issue':
        return issues?.items?.find((i: any) => i.id === id)?.title || `Issue #${id}`
      case 'organization':
        return organizations?.items?.find((o: any) => o.id === id)?.name || `Organization #${id}`
      default:
        return `${type} #${id}`
    }
  }

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteDependency(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['dependencies'],
        refetchType: 'all'
      })
      toast.success('Dependency deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete dependency')
    },
  })

  const handleDelete = (id: number, sourceName: string, targetName: string) => {
    if (window.confirm(`Delete dependency: ${sourceName} → ${targetName}?`)) {
      deleteMutation.mutate(id)
    }
  }

  const filteredDependencies = dependencies?.items?.filter((dep: PolymorphicDependency) => {
    if (!search) return true
    const sourceName = getResourceName(dep.source_type, dep.source_id).toLowerCase()
    const targetName = getResourceName(dep.target_type, dep.target_id).toLowerCase()
    const searchLower = search.toLowerCase()
    return sourceName.includes(searchLower) || targetName.includes(searchLower) ||
           dep.dependency_type.toLowerCase().includes(searchLower)
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Dependencies</h1>
          <p className="mt-2 text-slate-400">
            Manage relationships between all resource types
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Dependency
        </Button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search dependencies..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select
          value={sourceTypeFilter}
          onChange={(e) => setSourceTypeFilter(e.target.value)}
        >
          <option value="">All Source Types</option>
          {RESOURCE_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </Select>
        <Select
          value={targetTypeFilter}
          onChange={(e) => setTargetTypeFilter(e.target.value)}
        >
          <option value="">All Target Types</option>
          {RESOURCE_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </Select>
      </div>

      {/* Dependencies List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filteredDependencies?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-400">No dependencies found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first dependency
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredDependencies?.map((dep: PolymorphicDependency) => (
            <Card key={dep.id}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    {/* Source Resource */}
                    <div className="flex-1">
                      <div className="text-sm text-slate-400">Source</div>
                      <div className="text-white font-medium">
                        {getResourceName(dep.source_type, dep.source_id)}
                      </div>
                      <div className="text-xs text-slate-500 capitalize">
                        {dep.source_type}
                      </div>
                    </div>

                    {/* Arrow with dependency type */}
                    <div className="flex flex-col items-center">
                      <ArrowRight className="w-6 h-6 text-primary-500" />
                      <div className="text-xs text-slate-400 mt-1">
                        {dep.dependency_type}
                      </div>
                    </div>

                    {/* Target Resource */}
                    <div className="flex-1">
                      <div className="text-sm text-slate-400">Target</div>
                      <div className="text-white font-medium">
                        {getResourceName(dep.target_type, dep.target_id)}
                      </div>
                      <div className="text-xs text-slate-500 capitalize">
                        {dep.target_type}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-4">
                    <div className="text-xs text-slate-500">
                      {new Date(dep.created_at).toLocaleDateString()}
                    </div>
                    <button
                      onClick={() =>
                        handleDelete(
                          dep.id,
                          getResourceName(dep.source_type, dep.source_id),
                          getResourceName(dep.target_type, dep.target_id)
                        )
                      }
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateDependencyModal
          entities={entities?.items || []}
          identities={identities?.items || []}
          projects={projects?.items || []}
          milestones={milestones?.items || []}
          issues={issues?.items || []}
          organizations={organizations?.items || []}
          onClose={() => setShowCreateModal(false)}
          onSuccess={async () => {
            await queryClient.invalidateQueries({
              queryKey: ['dependencies'],
              refetchType: 'all'
            })
            setShowCreateModal(false)
          }}
        />
      )}
    </div>
  )
}

interface CreateDependencyModalProps {
  entities: any[]
  identities: any[]
  projects: any[]
  milestones: any[]
  issues: any[]
  organizations: any[]
  onClose: () => void
  onSuccess: () => void
}

function CreateDependencyModal({
  entities,
  identities,
  projects,
  milestones,
  issues,
  organizations,
  onClose,
  onSuccess,
}: CreateDependencyModalProps) {
  const [sourceType, setSourceType] = useState<string>('entity')
  const [sourceId, setSourceId] = useState<number | undefined>()
  const [targetType, setTargetType] = useState<string>('entity')
  const [targetId, setTargetId] = useState<number | undefined>()
  const [dependencyType, setDependencyType] = useState<DependencyType>('depends')

  // Get items for a resource type
  const getItemsForType = (type: string) => {
    switch (type) {
      case 'entity':
        return entities.map((e) => ({ id: e.id, name: e.name, detail: e.entity_type }))
      case 'identity':
        return identities.map((i) => ({ id: i.id, name: i.username, detail: i.identity_type }))
      case 'project':
        return projects.map((p) => ({ id: p.id, name: p.name, detail: p.status }))
      case 'milestone':
        return milestones.map((m) => ({ id: m.id, name: m.title, detail: m.status }))
      case 'issue':
        return issues.map((i) => ({ id: i.id, name: i.title, detail: i.status }))
      case 'organization':
        return organizations.map((o) => ({ id: o.id, name: o.name, detail: o.organization_type }))
      default:
        return []
    }
  }

  const sourceItems = getItemsForType(sourceType)
  const targetItems = getItemsForType(targetType)

  const createMutation = useMutation({
    mutationFn: (data: {
      source_type: string
      source_id: number
      target_type: string
      target_id: number
      dependency_type: string
    }) => api.createDependency(data),
    onSuccess: () => {
      toast.success('Dependency created successfully')
      onSuccess()
    },
    onError: () => {
      toast.error('Failed to create dependency')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!sourceId || !targetId) {
      toast.error('Please select both source and target resources')
      return
    }
    if (sourceType === targetType && sourceId === targetId) {
      toast.error('Source and target cannot be the same resource')
      return
    }
    createMutation.mutate({
      source_type: sourceType,
      source_id: sourceId,
      target_type: targetType,
      target_id: targetId,
      dependency_type: dependencyType,
    })
  }

  // Reset selection when type changes
  const handleSourceTypeChange = (type: string) => {
    setSourceType(type)
    setSourceId(undefined)
  }

  const handleTargetTypeChange = (type: string) => {
    setTargetType(type)
    setTargetId(undefined)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Create Dependency</h2>
          <p className="text-sm text-slate-400 mt-1">
            Link any resource types together
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Source */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-slate-300">
                Source <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <Select
                  value={sourceType}
                  onChange={(e) => handleSourceTypeChange(e.target.value)}
                >
                  {RESOURCE_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </Select>
                <Select
                  required
                  value={sourceId?.toString() || ''}
                  onChange={(e) => setSourceId(parseInt(e.target.value))}
                >
                  <option value="">Select {sourceType}</option>
                  {sourceItems.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name} {item.detail ? `(${item.detail})` : ''}
                    </option>
                  ))}
                </Select>
              </div>
            </div>

            {/* Dependency Type */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Relationship Type <span className="text-red-500">*</span>
              </label>
              <Select
                required
                value={dependencyType}
                onChange={(e) => setDependencyType(e.target.value as DependencyType)}
              >
                <option value="depends">Depends On</option>
                <option value="calls">Calls</option>
                <option value="related">Related To</option>
                <option value="affects">Affects</option>
                <option value="manages">Manages</option>
                <option value="owns">Owns</option>
                <option value="contains">Contains</option>
                <option value="connects">Connects To</option>
                <option value="other">Other</option>
              </Select>
            </div>

            {/* Target */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-slate-300">
                Target <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <Select
                  value={targetType}
                  onChange={(e) => handleTargetTypeChange(e.target.value)}
                >
                  {RESOURCE_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </Select>
                <Select
                  required
                  value={targetId?.toString() || ''}
                  onChange={(e) => setTargetId(parseInt(e.target.value))}
                >
                  <option value="">Select {targetType}</option>
                  {targetItems.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name} {item.detail ? `(${item.detail})` : ''}
                    </option>
                  ))}
                </Select>
              </div>
            </div>

            {/* Preview */}
            <div className="bg-slate-800 p-3 rounded-lg text-sm text-slate-300">
              <strong>Preview:</strong>{' '}
              <span className="text-white">
                {sourceId
                  ? sourceItems.find((i) => i.id === sourceId)?.name || sourceType
                  : `[${sourceType}]`}
              </span>{' '}
              <span className="text-primary-400">{dependencyType}</span>{' '}
              <span className="text-white">
                {targetId
                  ? targetItems.find((i) => i.id === targetId)?.name || targetType
                  : `[${targetType}]`}
              </span>
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
