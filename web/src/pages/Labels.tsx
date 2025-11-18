import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Tag } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'

export default function Labels() {
  const [search, setSearch] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingLabel, setEditingLabel] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['labels', { search }],
    queryFn: () => api.getLabels({ search }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteLabel(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['labels'],
        refetchType: 'all'
      })
      toast.success('Label deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete label')
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Are you sure you want to delete label "${name}"?`)) {
      deleteMutation.mutate(id)
    }
  }

  const filteredLabels = data?.items?.filter((label: any) => {
    if (!search) return true
    return label.name.toLowerCase().includes(search.toLowerCase()) ||
           label.description?.toLowerCase().includes(search.toLowerCase())
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Labels</h1>
          <p className="mt-2 text-slate-400">
            Manage labels for organizations, entities, issues, and identities
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Label
        </Button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search labels..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Labels List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filteredLabels?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-400">No labels found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first label
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredLabels?.map((label: any) => (
            <Card key={label.id}>
              <CardContent>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <Tag
                      className="w-5 h-5 flex-shrink-0"
                      style={{ color: label.color || '#64748b' }}
                    />
                    <div className="flex-1 min-w-0">
                      <h3
                        className="text-lg font-semibold truncate"
                        style={{ color: label.color || '#ffffff' }}
                      >
                        {label.name}
                      </h3>
                    </div>
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={() => setEditingLabel(label)}
                      className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(label.id, label.name)}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {label.description && (
                  <p className="text-sm text-slate-400 mb-3">{label.description}</p>
                )}
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span
                    className="inline-block px-2 py-1 rounded"
                    style={{
                      backgroundColor: `${label.color || '#64748b'}20`,
                      color: label.color || '#64748b'
                    }}
                  >
                    {label.name}
                  </span>
                  <span>ID: {label.id}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <LabelModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={async () => {
            await queryClient.invalidateQueries({
              queryKey: ['labels'],
              refetchType: 'all'
            })
            setShowCreateModal(false)
          }}
        />
      )}

      {/* Edit Modal */}
      {editingLabel && (
        <LabelModal
          label={editingLabel}
          onClose={() => setEditingLabel(null)}
          onSuccess={async () => {
            await queryClient.invalidateQueries({
              queryKey: ['labels'],
              refetchType: 'all'
            })
            setEditingLabel(null)
          }}
        />
      )}
    </div>
  )
}

interface LabelModalProps {
  label?: any
  onClose: () => void
  onSuccess: () => void
}

function LabelModal({ label, onClose, onSuccess }: LabelModalProps) {
  const [name, setName] = useState(label?.name || '')
  const [description, setDescription] = useState(label?.description || '')
  const [color, setColor] = useState(label?.color || '#3b82f6')

  const mutation = useMutation({
    mutationFn: (data: { name: string; description?: string; color?: string }) =>
      label
        ? api.updateLabel(label.id, data)
        : api.createLabel(data),
    onSuccess: () => {
      toast.success(label ? 'Label updated successfully' : 'Label created successfully')
      onSuccess()
    },
    onError: () => {
      toast.error(label ? 'Failed to update label' : 'Failed to create label')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      name,
      description: description || undefined,
      color: color || undefined,
    })
  }

  const colorPresets = [
    '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
    '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
    '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
    '#ec4899', '#f43f5e', '#64748b', '#6b7280', '#374151'
  ]

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">
            {label ? 'Edit Label' : 'Create Label'}
          </h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter label name"
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter description (optional)"
                rows={3}
                className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-3">
                Color
              </label>
              <div className="flex items-center gap-3 mb-3">
                <input
                  type="color"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="w-12 h-12 rounded border-2 border-slate-700 cursor-pointer"
                />
                <div className="flex-1">
                  <Input
                    type="text"
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    placeholder="#3b82f6"
                    className="font-mono"
                  />
                </div>
              </div>
              <div className="grid grid-cols-10 gap-2">
                {colorPresets.map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => setColor(preset)}
                    className={`w-8 h-8 rounded border-2 transition-all ${
                      color === preset ? 'border-white scale-110' : 'border-slate-700'
                    }`}
                    style={{ backgroundColor: preset }}
                  />
                ))}
              </div>
            </div>
            <div className="bg-slate-800 p-3 rounded-lg">
              <p className="text-sm text-slate-300 mb-2">Preview:</p>
              <span
                className="inline-block px-3 py-1.5 rounded text-sm font-medium"
                style={{
                  backgroundColor: `${color}20`,
                  color: color
                }}
              >
                {name || 'Label Name'}
              </span>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" isLoading={mutation.isPending}>
                {label ? 'Update' : 'Create'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
