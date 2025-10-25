import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Flag, Calendar } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const MILESTONE_STATUSES = [
  { value: 'open', label: 'Open' },
  { value: 'closed', label: 'Closed' },
]

export default function Milestones() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [projectFilter, setProjectFilter] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingMilestone, setEditingMilestone] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['milestones', { search, status: statusFilter, project_id: projectFilter }],
    queryFn: () => api.getMilestones({
      search,
      status: statusFilter || undefined,
      project_id: projectFilter ? parseInt(projectFilter) : undefined,
    }),
  })

  const { data: projects } = useQuery({
    queryKey: ['projects-all'],
    queryFn: () => api.getProjects({ per_page: 1000 }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteMilestone(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['milestones'] })
      toast.success('Milestone deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete milestone')
    },
  })

  const handleDelete = (id: number, title: string) => {
    if (window.confirm(`Are you sure you want to delete milestone "${title}"?`)) {
      deleteMutation.mutate(id)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-green-500/20 text-green-400'
      case 'closed':
        return 'bg-slate-500/20 text-slate-400'
      default:
        return 'bg-slate-500/20 text-slate-400'
    }
  }

  const isOverdue = (dueDate: string, status: string) => {
    if (status === 'closed') return false
    if (!dueDate) return false
    return new Date(dueDate) < new Date()
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Milestones</h1>
          <p className="mt-2 text-slate-400">
            Track project milestones and deadlines
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Milestone
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <Input
              type="text"
              placeholder="Search milestones..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select
          value={projectFilter}
          onChange={(e) => setProjectFilter(e.target.value)}
          className="w-48"
        >
          <option value="">All Projects</option>
          {projects?.items?.map((project: any) => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </Select>
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-48"
        >
          <option value="">All Statuses</option>
          {MILESTONE_STATUSES.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          ))}
        </Select>
      </div>

      {/* Milestones List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Flag className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No milestones found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first milestone
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.items?.map((milestone: any) => (
            <Card key={milestone.id}>
              <CardContent>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <Flag className={`w-5 h-5 flex-shrink-0 ${
                      isOverdue(milestone.due_date, milestone.status)
                        ? 'text-red-400'
                        : 'text-primary-400'
                    }`} />
                    <h3 className="text-lg font-semibold text-white truncate">
                      {milestone.title}
                    </h3>
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={() => setEditingMilestone(milestone)}
                      className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(milestone.id, milestone.title)}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {milestone.description && (
                  <p className="text-sm text-slate-400 mb-3 line-clamp-2">
                    {milestone.description}
                  </p>
                )}

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs px-2 py-1 rounded ${getStatusColor(milestone.status)}`}>
                      {milestone.status}
                    </span>
                    {milestone.due_date && (
                      <div className={`flex items-center gap-1 text-xs ${
                        isOverdue(milestone.due_date, milestone.status)
                          ? 'text-red-400 font-semibold'
                          : 'text-slate-500'
                      }`}>
                        <Calendar className="w-3 h-3" />
                        {new Date(milestone.due_date).toLocaleDateString()}
                        {isOverdue(milestone.due_date, milestone.status) && ' (Overdue)'}
                      </div>
                    )}
                  </div>

                  {milestone.project_id && (
                    <div className="text-xs text-slate-500">
                      Project: {projects?.items?.find((p: any) => p.id === milestone.project_id)?.name || milestone.project_id}
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
        <MilestoneModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['milestones'] })
          }}
        />
      )}

      {/* Edit Modal */}
      {editingMilestone && (
        <MilestoneModal
          milestone={editingMilestone}
          onClose={() => setEditingMilestone(null)}
          onSuccess={() => {
            setEditingMilestone(null)
            queryClient.invalidateQueries({ queryKey: ['milestones'] })
          }}
        />
      )}
    </div>
  )
}

interface MilestoneModalProps {
  milestone?: any
  onClose: () => void
  onSuccess: () => void
}

function MilestoneModal({ milestone, onClose, onSuccess }: MilestoneModalProps) {
  const [title, setTitle] = useState(milestone?.title || '')
  const [description, setDescription] = useState(milestone?.description || '')
  const [status, setStatus] = useState(milestone?.status || 'open')
  const [organizationId, setOrganizationId] = useState(milestone?.organization_id || '')
  const [projectId, setProjectId] = useState(milestone?.project_id || '')
  const [dueDate, setDueDate] = useState(milestone?.due_date || '')

  const { data: organizations, isLoading: orgsLoading } = useQuery({
    queryKey: ['organizations-all'],
    queryFn: () => api.getOrganizations({ per_page: 1000 }),
  })

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects-all'],
    queryFn: () => api.getProjects({ per_page: 1000 }),
  })

  const mutation = useMutation({
    mutationFn: (data: any) =>
      milestone
        ? api.updateMilestone(milestone.id, data)
        : api.createMilestone(data),
    onSuccess: () => {
      toast.success(milestone ? 'Milestone updated successfully' : 'Milestone created successfully')
      onSuccess()
    },
    onError: () => {
      toast.error(milestone ? 'Failed to update milestone' : 'Failed to create milestone')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      title,
      description: description || undefined,
      status,
      organization_id: parseInt(organizationId),
      project_id: projectId ? parseInt(projectId) : undefined,
      due_date: dueDate || undefined,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">
            {milestone ? 'Edit Milestone' : 'Create Milestone'}
          </h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Title"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Beta Release"
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Milestone description (optional)"
                rows={3}
                className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <Select
              label="Organization"
              required
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
            >
              <option value="">
                {orgsLoading ? 'Loading...' : organizations?.items?.length ? 'Select organization' : 'No organizations found - create one first'}
              </option>
              {organizations?.items?.map((org: any) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </Select>
            <Select
              label="Project (Optional)"
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
            >
              <option value="">
                {projectsLoading ? 'Loading...' : 'No project'}
              </option>
              {projects?.items?.map((project: any) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </Select>
            <Select
              label="Status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              {MILESTONE_STATUSES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </Select>
            <Input
              label="Due Date"
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
            />
            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" isLoading={mutation.isPending}>
                {milestone ? 'Update' : 'Create'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
