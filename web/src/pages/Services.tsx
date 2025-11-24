import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Server, Globe, Lock, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { queryKeys } from '@/lib/queryKeys'
import { invalidateCache } from '@/lib/invalidateCache'
import { getStatusColor } from '@/lib/colorHelpers'
import { confirmDelete } from '@/lib/confirmActions'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'
import ModalFormBuilder from '@/components/ModalFormBuilder'
import { FormConfig } from '@/types/form'

const SERVICE_STATUSES = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'deprecated', label: 'Deprecated' },
]

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'go', label: 'Go' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'rust', label: 'Rust' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'php', label: 'PHP' },
  { value: 'csharp', label: 'C#' },
  { value: 'other', label: 'Other' },
]

const DEPLOYMENT_METHODS = [
  { value: 'kubernetes', label: 'Kubernetes' },
  { value: 'docker', label: 'Docker' },
  { value: 'docker-compose', label: 'Docker Compose' },
  { value: 'serverless', label: 'Serverless' },
  { value: 'vm', label: 'Virtual Machine' },
  { value: 'bare-metal', label: 'Bare Metal' },
  { value: 'paas', label: 'PaaS' },
  { value: 'other', label: 'Other' },
]

export default function Services() {
  const [search, setSearch] = useState('')
  const [organizationFilter, setOrganizationFilter] = useState<string>('')
  const [languageFilter, setLanguageFilter] = useState<string>('')
  const [deploymentFilter, setDeploymentFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingService, setEditingService] = useState<any>(null)
  const [viewingService, setViewingService] = useState<any>(null)
  const queryClient = useQueryClient()

  const { data: organizations } = useQuery({
    queryKey: queryKeys.organizations.dropdown,
    queryFn: () => api.getOrganizations({ per_page: 1000 }),
  })

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.services.list({ search, organization_id: organizationFilter, language: languageFilter, deployment_method: deploymentFilter, status: statusFilter }),
    queryFn: () => api.getServices({
      search,
      organization_id: organizationFilter ? parseInt(organizationFilter) : undefined,
      language: languageFilter || undefined,
      deployment_method: deploymentFilter || undefined,
      status: statusFilter || undefined,
    }),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createService(data),
    onSuccess: async () => {
      await invalidateCache.services(queryClient)
      toast.success('Service created successfully')
      setShowCreateModal(false)
    },
    onError: () => {
      toast.error('Failed to create service')
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data: any) => api.updateService(editingService.id, data),
    onSuccess: async () => {
      await invalidateCache.services(queryClient)
      toast.success('Service updated successfully')
      setEditingService(null)
    },
    onError: () => {
      toast.error('Failed to update service')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteService(id),
    onSuccess: async () => {
      await invalidateCache.services(queryClient)
      toast.success('Service deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete service')
    },
  })

  const handleDelete = (id: number, name: string) => {
    confirmDelete(`service "${name}"`, () => {
      deleteMutation.mutate(id)
    })
  }

  const getLanguageColor = (language: string) => {
    switch (language) {
      case 'python':
        return 'bg-blue-500/20 text-blue-400'
      case 'go':
        return 'bg-cyan-500/20 text-cyan-400'
      case 'javascript':
      case 'typescript':
        return 'bg-yellow-500/20 text-yellow-400'
      case 'java':
        return 'bg-orange-500/20 text-orange-400'
      case 'rust':
        return 'bg-red-500/20 text-red-400'
      default:
        return 'bg-purple-500/20 text-purple-400'
    }
  }

  // Build organization options for form
  const organizationOptions = organizations?.items?.map((org: any) => ({
    value: org.id.toString(),
    label: org.name,
  })) || []

  // Form configuration for create/edit
  const getServiceFormConfig = (): FormConfig => ({
    fields: [
      {
        name: 'name',
        label: 'Name',
        type: 'text',
        required: true,
        placeholder: 'api-gateway',
      },
      {
        name: 'description',
        label: 'Description',
        type: 'textarea',
        placeholder: 'Service description (optional)',
        rows: 2,
      },
      {
        name: 'organization_id',
        label: 'Organization',
        type: 'select',
        required: true,
        options: [
          { value: '', label: organizationOptions.length ? 'Select organization' : 'No organizations found' },
          ...organizationOptions,
        ],
      },
      {
        name: 'language',
        label: 'Language',
        type: 'select',
        options: LANGUAGES,
        defaultValue: 'python',
      },
      {
        name: 'deployment_method',
        label: 'Deployment Method',
        type: 'select',
        options: DEPLOYMENT_METHODS,
        defaultValue: 'kubernetes',
      },
      {
        name: 'status',
        label: 'Status',
        type: 'select',
        options: SERVICE_STATUSES,
        defaultValue: 'active',
      },
      {
        name: 'port',
        label: 'Port',
        type: 'number',
        placeholder: '8080',
      },
      {
        name: 'is_public',
        label: 'Public service (accessible from internet)',
        type: 'checkbox',
        defaultValue: false,
      },
      {
        name: 'domains',
        label: 'Domains (one per line)',
        type: 'multiline',
        placeholder: 'api.example.com\napi-v2.example.com',
        rows: 2,
      },
      {
        name: 'paths',
        label: 'Paths (one per line)',
        type: 'multiline',
        placeholder: '/api/v1\n/api/v2',
        rows: 3,
      },
    ],
    submitLabel: editingService ? 'Update' : 'Create',
  })

  const handleCreateSubmit = (data: Record<string, any>) => {
    createMutation.mutate({
      ...data,
      organization_id: parseInt(data.organization_id),
    })
  }

  const handleEditSubmit = (data: Record<string, any>) => {
    updateMutation.mutate({
      ...data,
      organization_id: parseInt(data.organization_id),
    })
  }

  // Get initial values for edit form
  const getEditInitialValues = (service: any) => ({
    name: service.name || '',
    description: service.description || '',
    organization_id: service.organization_id?.toString() || '',
    language: service.language || 'python',
    deployment_method: service.deployment_method || 'kubernetes',
    status: service.status || 'active',
    port: service.port?.toString() || '',
    is_public: service.is_public || false,
    domains: service.domains?.join('\n') || '',
    paths: service.paths?.join('\n') || '',
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Services</h1>
          <p className="mt-2 text-slate-400">
            Track and manage microservices across your infrastructure
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Service
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex-1 min-w-[200px] max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <Input
              type="text"
              placeholder="Search services..."
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
          value={languageFilter}
          onChange={(e) => setLanguageFilter(e.target.value)}
          className="w-40"
        >
          <option value="">All Languages</option>
          {LANGUAGES.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </Select>
        <Select
          value={deploymentFilter}
          onChange={(e) => setDeploymentFilter(e.target.value)}
          className="w-44"
        >
          <option value="">All Deployments</option>
          {DEPLOYMENT_METHODS.map((method) => (
            <option key={method.value} value={method.value}>
              {method.label}
            </option>
          ))}
        </Select>
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-36"
        >
          <option value="">All Statuses</option>
          {SERVICE_STATUSES.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          ))}
        </Select>
      </div>

      {/* Services List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Server className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No services found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first service
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.items?.map((service: any) => (
            <Card
              key={service.id}
              className="cursor-pointer hover:border-primary-500/50 transition-colors"
              onClick={() => setViewingService(service)}
            >
              <CardContent>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <Server className="w-5 h-5 text-primary-400 flex-shrink-0" />
                    <h3 className="text-lg font-semibold text-white truncate">
                      {service.name}
                    </h3>
                    {service.is_public ? (
                      <Globe className="w-4 h-4 text-green-400 flex-shrink-0" title="Public" />
                    ) : (
                      <Lock className="w-4 h-4 text-slate-400 flex-shrink-0" title="Private" />
                    )}
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setEditingService(service)
                      }}
                      className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(service.id, service.name)
                      }}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {service.description && (
                  <p className="text-sm text-slate-400 mb-3 line-clamp-2">
                    {service.description}
                  </p>
                )}

                <div className="flex flex-wrap gap-2 mb-3">
                  <span className={`text-xs px-2 py-1 rounded ${getStatusColor(service.status)}`}>
                    {service.status}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${getLanguageColor(service.language)}`}>
                    {service.language}
                  </span>
                  <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">
                    {service.deployment_method}
                  </span>
                </div>

                {service.port && (
                  <div className="text-xs text-slate-500 mb-2">
                    Port: {service.port}
                  </div>
                )}

                {service.domains && service.domains.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {service.domains.slice(0, 2).map((domain: string, idx: number) => (
                      <span key={idx} className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
                        {domain}
                      </span>
                    ))}
                    {service.domains.length > 2 && (
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-400">
                        +{service.domains.length - 2} more
                      </span>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <ModalFormBuilder
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create Service"
        config={getServiceFormConfig()}
        onSubmit={handleCreateSubmit}
        isLoading={createMutation.isPending}
      />

      {/* Edit Modal */}
      <ModalFormBuilder
        isOpen={!!editingService}
        onClose={() => setEditingService(null)}
        title="Edit Service"
        config={getServiceFormConfig()}
        initialValues={editingService ? getEditInitialValues(editingService) : undefined}
        onSubmit={handleEditSubmit}
        isLoading={updateMutation.isPending}
      />

      {/* View Details Modal */}
      {viewingService && (
        <ServiceDetailsModal
          service={viewingService}
          onClose={() => setViewingService(null)}
          onEdit={() => {
            setEditingService(viewingService)
            setViewingService(null)
          }}
        />
      )}
    </div>
  )
}

interface ServiceDetailsModalProps {
  service: any
  onClose: () => void
  onEdit: () => void
}

function ServiceDetailsModal({ service, onClose, onEdit }: ServiceDetailsModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-primary-400" />
              <h2 className="text-xl font-semibold text-white">{service.name}</h2>
              {service.is_public ? (
                <Globe className="w-4 h-4 text-green-400" title="Public" />
              ) : (
                <Lock className="w-4 h-4 text-slate-400" title="Private" />
              )}
            </div>
            <button
              onClick={onEdit}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
            >
              <Edit className="w-4 h-4" />
            </button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {service.description && (
            <p className="text-sm text-slate-400">{service.description}</p>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-500 uppercase">Status</label>
              <div className="mt-1">
                <span className={`text-sm px-2 py-1 rounded ${getStatusColor(service.status)}`}>
                  {service.status}
                </span>
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-500 uppercase">Language</label>
              <p className="text-sm text-white mt-1">{service.language}</p>
            </div>
            <div>
              <label className="text-xs text-slate-500 uppercase">Deployment</label>
              <p className="text-sm text-white mt-1">{service.deployment_method}</p>
            </div>
            {service.port && (
              <div>
                <label className="text-xs text-slate-500 uppercase">Port</label>
                <p className="text-sm text-white mt-1">{service.port}</p>
              </div>
            )}
          </div>

          {service.domains && service.domains.length > 0 && (
            <div>
              <label className="text-xs text-slate-500 uppercase">Domains</label>
              <div className="flex flex-wrap gap-2 mt-2">
                {service.domains.map((domain: string, idx: number) => (
                  <span key={idx} className="text-sm px-2 py-1 rounded bg-primary-500/20 text-primary-400 flex items-center gap-1">
                    {domain}
                    <ExternalLink className="w-3 h-3" />
                  </span>
                ))}
              </div>
            </div>
          )}

          {service.paths && service.paths.length > 0 && (
            <div>
              <label className="text-xs text-slate-500 uppercase">Paths</label>
              <div className="flex flex-wrap gap-2 mt-2">
                {service.paths.map((path: string, idx: number) => (
                  <span key={idx} className="text-sm px-2 py-1 rounded bg-slate-700 text-slate-300">
                    {path}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-slate-700">
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
