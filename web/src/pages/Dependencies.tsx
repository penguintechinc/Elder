import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Trash2, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import type { Dependency, Entity, DependencyType } from '@/types'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

export default function Dependencies() {
  const [search, setSearch] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [sourceFilter, setSourceFilter] = useState<number | undefined>()
  const [targetFilter, setTargetFilter] = useState<number | undefined>()
  const queryClient = useQueryClient()

  const { data: dependencies, isLoading } = useQuery({
    queryKey: ['dependencies', { sourceFilter, targetFilter }],
    queryFn: () =>
      api.getDependencies({
        source_entity_id: sourceFilter,
        target_entity_id: targetFilter,
      }),
  })

  const { data: entities } = useQuery({
    queryKey: ['entities-all'],
    queryFn: () => api.getEntities({ per_page: 1000 }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteDependency(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dependencies'] })
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

  const filteredDependencies = dependencies?.items?.filter((dep: Dependency) => {
    if (!search) return true
    const sourceName = dep.source_entity?.name?.toLowerCase() || ''
    const targetName = dep.target_entity?.name?.toLowerCase() || ''
    const searchLower = search.toLowerCase()
    return sourceName.includes(searchLower) || targetName.includes(searchLower)
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Dependencies</h1>
          <p className="mt-2 text-slate-400">
            Manage entity relationships and dependencies
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
          value={sourceFilter?.toString() || ''}
          onChange={(e) =>
            setSourceFilter(e.target.value ? parseInt(e.target.value) : undefined)
          }
        >
          <option value="">All Sources</option>
          {entities?.items?.map((entity: Entity) => (
            <option key={entity.id} value={entity.id}>
              {entity.name}
            </option>
          ))}
        </Select>
        <Select
          value={targetFilter?.toString() || ''}
          onChange={(e) =>
            setTargetFilter(e.target.value ? parseInt(e.target.value) : undefined)
          }
        >
          <option value="">All Targets</option>
          {entities?.items?.map((entity: Entity) => (
            <option key={entity.id} value={entity.id}>
              {entity.name}
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
          {filteredDependencies?.map((dep: Dependency) => (
            <Card key={dep.id}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    {/* Source Entity */}
                    <div className="flex-1">
                      <div className="text-sm text-slate-400">Source</div>
                      <div className="text-white font-medium">
                        {dep.source_entity?.name || `Entity #${dep.source_entity_id}`}
                      </div>
                      <div className="text-xs text-slate-500">
                        {dep.source_entity?.entity_type}
                      </div>
                    </div>

                    {/* Arrow with dependency type */}
                    <div className="flex flex-col items-center">
                      <ArrowRight className="w-6 h-6 text-primary-500" />
                      <div className="text-xs text-slate-400 mt-1">
                        {dep.dependency_type}
                      </div>
                    </div>

                    {/* Target Entity */}
                    <div className="flex-1">
                      <div className="text-sm text-slate-400">Target</div>
                      <div className="text-white font-medium">
                        {dep.target_entity?.name || `Entity #${dep.target_entity_id}`}
                      </div>
                      <div className="text-xs text-slate-500">
                        {dep.target_entity?.entity_type}
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
                          dep.source_entity?.name || `Entity #${dep.source_entity_id}`,
                          dep.target_entity?.name || `Entity #${dep.target_entity_id}`
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
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['dependencies'] })
          }}
        />
      )}
    </div>
  )
}

interface CreateDependencyModalProps {
  entities: Entity[]
  onClose: () => void
  onSuccess: () => void
}

function CreateDependencyModal({ entities, onClose, onSuccess }: CreateDependencyModalProps) {
  const [sourceEntityId, setSourceEntityId] = useState<number | undefined>()
  const [targetEntityId, setTargetEntityId] = useState<number | undefined>()
  const [dependencyType, setDependencyType] = useState<DependencyType>('depends_on')

  const createMutation = useMutation({
    mutationFn: (data: {
      source_entity_id: number
      target_entity_id: number
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
    if (!sourceEntityId || !targetEntityId) {
      toast.error('Please select both source and target entities')
      return
    }
    if (sourceEntityId === targetEntityId) {
      toast.error('Source and target entities must be different')
      return
    }
    createMutation.mutate({
      source_entity_id: sourceEntityId,
      target_entity_id: targetEntityId,
      dependency_type: dependencyType,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Create Dependency</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Source Entity <span className="text-red-500">*</span>
              </label>
              <Select
                required
                value={sourceEntityId?.toString() || ''}
                onChange={(e) => setSourceEntityId(parseInt(e.target.value))}
              >
                <option value="">Select source entity</option>
                {entities.map((entity) => (
                  <option key={entity.id} value={entity.id}>
                    {entity.name} ({entity.entity_type})
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Dependency Type <span className="text-red-500">*</span>
              </label>
              <Select
                required
                value={dependencyType}
                onChange={(e) => setDependencyType(e.target.value as DependencyType)}
              >
                <option value="depends_on">Depends On</option>
                <option value="related_to">Related To</option>
                <option value="part_of">Part Of</option>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Target Entity <span className="text-red-500">*</span>
              </label>
              <Select
                required
                value={targetEntityId?.toString() || ''}
                onChange={(e) => setTargetEntityId(parseInt(e.target.value))}
              >
                <option value="">Select target entity</option>
                {entities.map((entity) => (
                  <option key={entity.id} value={entity.id}>
                    {entity.name} ({entity.entity_type})
                  </option>
                ))}
              </Select>
            </div>

            <div className="bg-slate-800 p-3 rounded-lg text-sm text-slate-300">
              <strong>Note:</strong> This will create a dependency from{' '}
              <span className="text-white">
                {sourceEntityId
                  ? entities.find((e) => e.id === sourceEntityId)?.name || 'source'
                  : 'source'}
              </span>{' '}
              to{' '}
              <span className="text-white">
                {targetEntityId
                  ? entities.find((e) => e.id === targetEntityId)?.name || 'target'
                  : 'target'}
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
