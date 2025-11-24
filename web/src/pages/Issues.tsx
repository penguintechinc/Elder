import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Plus, Search, MessageSquare, Tag, User, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import { invalidateCache } from '@/lib/invalidateCache'
import { getStatusColor, getPriorityColor } from '@/lib/colorHelpers'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

type IssueStatus = 'open' | 'in_progress' | 'closed'
type IssuePriority = 'low' | 'medium' | 'high' | 'critical'

export default function Issues() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<IssueStatus | ''>('')
  const [priorityFilter, setPriorityFilter] = useState<IssuePriority | ''>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const organizationId = searchParams.get('organization_id')
  const entityId = searchParams.get('entity_id')

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.issues.list({ search, status: statusFilter, priority: priorityFilter, organizationId, entityId }),
    queryFn: () => api.getIssues({
      search,
      status: statusFilter || undefined,
      priority: priorityFilter || undefined,
      organization_id: organizationId ? parseInt(organizationId) : undefined,
      entity_id: entityId ? parseInt(entityId) : undefined,
    }),
  })

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: IssueStatus }) =>
      api.updateIssue(id, { status }),
    onSuccess: async () => {
      await invalidateCache.issues(queryClient)
      toast.success('Issue status updated')
    },
    onError: () => {
      toast.error('Failed to update issue status')
    },
  })


  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Issues</h1>
          <p className="mt-2 text-slate-400">
            Track and manage issues across your infrastructure
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Issue
        </Button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search issues..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as IssueStatus | '')}
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="closed">Closed</option>
        </Select>
        <Select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value as IssuePriority | '')}
        >
          <option value="">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </Select>
      </div>

      {/* Issues List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-400">No issues found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first issue
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {data?.items?.map((issue: any) => (
            <Card
              key={issue.id}
              className="cursor-pointer hover:ring-2 hover:ring-primary-500 transition-all"
              onClick={() => navigate(`/issues/${issue.id}`)}
            >
              <CardContent>
                <div className="flex items-start gap-4">
                  {/* Issue Icon */}
                  <div className="flex-shrink-0 mt-1">
                    {issue.is_incident ? (
                      <AlertTriangle className="w-5 h-5 text-red-500" />
                    ) : (
                      <MessageSquare className="w-5 h-5 text-primary-400" />
                    )}
                  </div>

                  {/* Issue Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-white mb-1">
                          {issue.title}
                        </h3>
                        {issue.description && (
                          <p className="text-sm text-slate-400 line-clamp-2 mb-3">
                            {issue.description}
                          </p>
                        )}
                        <div className="flex flex-wrap items-center gap-3">
                          <span className="text-xs text-slate-500">#{issue.id}</span>
                          {issue.is_incident === 1 && (
                            <span className="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30 font-semibold">
                              INCIDENT
                            </span>
                          )}
                          <span className={`text-xs px-2 py-0.5 rounded border ${getStatusColor(issue.status)}`}>
                            {issue.status.replace('_', ' ')}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded border ${getPriorityColor(issue.priority)}`}>
                            {issue.priority}
                          </span>
                          {issue.assignee_id && (
                            <span className="flex items-center gap-1 text-xs text-slate-400">
                              <User className="w-3 h-3" />
                              Assigned
                            </span>
                          )}
                          {issue.labels && issue.labels.length > 0 && (
                            <span className="flex items-center gap-1 text-xs text-slate-400">
                              <Tag className="w-3 h-3" />
                              {issue.labels.length} label(s)
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Quick Status Change */}
                      <div onClick={(e) => e.stopPropagation()}>
                        <Select
                          value={issue.status}
                          onChange={(e) =>
                            updateStatusMutation.mutate({
                              id: issue.id,
                              status: e.target.value as IssueStatus,
                            })
                          }
                          className="text-sm"
                        >
                          <option value="open">Open</option>
                          <option value="in_progress">In Progress</option>
                          <option value="closed">Closed</option>
                        </Select>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateIssueModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={async () => {
            await queryClient.invalidateQueries({
              queryKey: ['issues'],
              refetchType: 'all'
            })
            setShowCreateModal(false)
          }}
          defaultOrganizationId={organizationId ? parseInt(organizationId) : undefined}
          defaultEntityId={entityId ? parseInt(entityId) : undefined}
        />
      )}
    </div>
  )
}

interface CreateIssueModalProps {
  onClose: () => void
  onSuccess: () => void
  defaultOrganizationId?: number
  defaultEntityId?: number
}

function CreateIssueModal({ onClose, onSuccess, defaultOrganizationId, defaultEntityId }: CreateIssueModalProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<IssuePriority>('medium')
  const [assignmentType, setAssignmentType] = useState<'organization' | 'entity'>('organization')
  const [organizationId, setOrganizationId] = useState<number | undefined>(defaultOrganizationId)
  const [selectedEntities, setSelectedEntities] = useState<number[]>(defaultEntityId ? [defaultEntityId] : [])
  const [selectedLabels, setSelectedLabels] = useState<number[]>([])
  const [isIncident, setIsIncident] = useState(false)

  const { data: organizations } = useQuery({
    queryKey: ['organizations-all'],
    queryFn: () => api.getOrganizations({ per_page: 1000 }),
  })

  const { data: entities } = useQuery({
    queryKey: ['entities-all'],
    queryFn: () => api.getEntities({ per_page: 1000 }),
  })

  const { data: labels } = useQuery({
    queryKey: ['labels-all'],
    queryFn: () => api.getLabels({ per_page: 1000 }),
  })

  const createMutation = useMutation({
    mutationFn: (data: {
      title: string
      description?: string
      priority: string
      organization_id?: number
      entity_ids?: number[]
      label_ids?: number[]
      is_incident?: number
    }) => api.createIssue(data),
    onSuccess: () => {
      toast.success('Issue created successfully')
      onSuccess()
    },
    onError: () => {
      toast.error('Failed to create issue')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      title,
      description: description || undefined,
      priority,
      organization_id: assignmentType === 'organization' ? organizationId : undefined,
      entity_ids: assignmentType === 'entity' && selectedEntities.length > 0 ? selectedEntities : undefined,
      label_ids: selectedLabels.length > 0 ? selectedLabels : undefined,
      is_incident: isIncident ? 1 : 0,
    })
  }

  const toggleEntity = (entityId: number) => {
    setSelectedEntities(prev =>
      prev.includes(entityId)
        ? prev.filter(id => id !== entityId)
        : [...prev, entityId]
    )
  }

  const toggleLabel = (labelId: number) => {
    setSelectedLabels(prev =>
      prev.includes(labelId)
        ? prev.filter(id => id !== labelId)
        : [...prev, labelId]
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Create Issue</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Title"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter issue title"
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter description (optional)"
                rows={4}
                className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <Select
              label="Priority"
              required
              value={priority}
              onChange={(e) => setPriority(e.target.value as IssuePriority)}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </Select>

            {/* Assignment Type Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Assign To
              </label>
              <div className="flex gap-4 mb-3">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="organization"
                    checked={assignmentType === 'organization'}
                    onChange={(e) => setAssignmentType(e.target.value as 'organization' | 'entity')}
                    className="mr-2"
                  />
                  <span className="text-sm text-slate-300">Organization</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="entity"
                    checked={assignmentType === 'entity'}
                    onChange={(e) => setAssignmentType(e.target.value as 'organization' | 'entity')}
                    className="mr-2"
                  />
                  <span className="text-sm text-slate-300">Entity</span>
                </label>
              </div>

              {assignmentType === 'organization' ? (
                <Select
                  value={organizationId?.toString() || ''}
                  onChange={(e) => setOrganizationId(e.target.value ? parseInt(e.target.value) : undefined)}
                >
                  <option value="">None</option>
                  {organizations?.items?.map((org: any) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </Select>
              ) : (
                <div className="max-h-40 overflow-y-auto border border-slate-700 rounded-lg p-2 bg-slate-900">
                  {entities?.items && entities.items.length > 0 ? (
                    entities.items.map((entity: any) => (
                      <label key={entity.id} className="flex items-center p-2 hover:bg-slate-800 rounded cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedEntities.includes(entity.id)}
                          onChange={() => toggleEntity(entity.id)}
                          className="mr-2"
                        />
                        <span className="text-sm text-slate-300">{entity.name}</span>
                      </label>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500 p-2">No entities available</p>
                  )}
                </div>
              )}
            </div>

            {/* Labels Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Labels
              </label>
              <div className="max-h-40 overflow-y-auto border border-slate-700 rounded-lg p-2 bg-slate-900">
                {labels?.items && labels.items.length > 0 ? (
                  labels.items.map((label: any) => (
                    <label key={label.id} className="flex items-center p-2 hover:bg-slate-800 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedLabels.includes(label.id)}
                        onChange={() => toggleLabel(label.id)}
                        className="mr-2"
                      />
                      <span
                        className="inline-block w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: label.color }}
                      />
                      <span className="text-sm text-slate-300">{label.name}</span>
                    </label>
                  ))
                ) : (
                  <p className="text-sm text-slate-500 p-2">No labels available</p>
                )}
              </div>
            </div>

            {/* Incident Checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is-incident"
                checked={isIncident}
                onChange={(e) => setIsIncident(e.target.checked)}
                className="mr-2 h-4 w-4 text-yellow-500 bg-slate-900 border-slate-700 rounded focus:ring-2 focus:ring-yellow-500"
              />
              <label htmlFor="is-incident" className="text-sm font-medium text-slate-300 cursor-pointer">
                Mark as Incident
              </label>
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
