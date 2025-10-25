import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Edit, Trash2, ChevronRight, ChevronDown, Folder, FolderOpen, Box } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import type { Organization, Entity } from '@/types'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'

interface TreeNode {
  type: 'organization' | 'entity'
  id: number
  name: string
  data: Organization | Entity
  children: TreeNode[]
}

export default function OrganizationDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

  const { data: organization, isLoading: orgLoading } = useQuery({
    queryKey: ['organization', id],
    queryFn: () => api.getOrganization(parseInt(id!)),
    enabled: !!id,
  })

  const { data: childOrgs } = useQuery({
    queryKey: ['organizations', { parent_id: id }],
    queryFn: () => api.getOrganizations({ parent_id: parseInt(id!) }),
    enabled: !!id,
  })

  const { data: entities } = useQuery({
    queryKey: ['entities', { organization_id: id }],
    queryFn: () => api.getEntities({ organization_id: parseInt(id!) }),
    enabled: !!id,
  })

  const { data: metadata } = useQuery({
    queryKey: ['organization-metadata', id],
    queryFn: () => api.getOrganizationMetadata(parseInt(id!)),
    enabled: !!id,
  })

  const { data: issues } = useQuery({
    queryKey: ['issues', { organization_id: id }],
    queryFn: () => api.getIssues({ organization_id: parseInt(id!) }),
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteOrganization(parseInt(id!)),
    onSuccess: () => {
      toast.success('Organization deleted successfully')
      navigate('/organizations')
    },
    onError: () => {
      toast.error('Failed to delete organization')
    },
  })

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${organization?.name}"?`)) {
      deleteMutation.mutate()
    }
  }

  const toggleNode = (nodeKey: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeKey)) {
      newExpanded.delete(nodeKey)
    } else {
      newExpanded.add(nodeKey)
    }
    setExpandedNodes(newExpanded)
  }

  const buildTree = (): TreeNode[] => {
    const tree: TreeNode[] = []

    // Add child organizations
    if (childOrgs?.items) {
      for (const org of childOrgs.items) {
        tree.push({
          type: 'organization',
          id: org.id,
          name: org.name,
          data: org,
          children: [], // Would need recursive fetching for deeper trees
        })
      }
    }

    // Add entities
    if (entities?.items) {
      for (const entity of entities.items) {
        tree.push({
          type: 'entity',
          id: entity.id,
          name: entity.name,
          data: entity,
          children: [],
        })
      }
    }

    return tree
  }

  const renderTreeNode = (node: TreeNode, level: number = 0) => {
    const nodeKey = `${node.type}-${node.id}`
    const isExpanded = expandedNodes.has(nodeKey)
    const hasChildren = node.children.length > 0

    return (
      <div key={nodeKey} style={{ marginLeft: `${level * 24}px` }}>
        <div
          className="flex items-center gap-2 py-2 px-3 hover:bg-slate-800/50 rounded cursor-pointer group"
          onClick={() => {
            if (node.type === 'organization') {
              navigate(`/organizations/${node.id}`)
            } else {
              navigate(`/entities/${node.id}`)
            }
          }}
        >
          {hasChildren ? (
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleNode(nodeKey)
              }}
              className="p-0.5 hover:bg-slate-700 rounded"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
            </button>
          ) : (
            <div className="w-5" />
          )}

          {node.type === 'organization' ? (
            isExpanded ? (
              <FolderOpen className="w-4 h-4 text-primary-400" />
            ) : (
              <Folder className="w-4 h-4 text-primary-400" />
            )
          ) : (
            <Box className="w-4 h-4 text-blue-400" />
          )}

          <span className="text-sm text-white group-hover:text-primary-400 transition-colors">
            {node.name}
          </span>

          {node.type === 'entity' && (
            <span className="text-xs text-slate-500 ml-2">
              {(node.data as Entity).entity_type}
            </span>
          )}
        </div>

        {isExpanded && hasChildren && (
          <div>
            {node.children.map((child) => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  if (orgLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!organization) {
    return (
      <div className="p-8">
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-400">Organization not found</p>
            <Button className="mt-4" onClick={() => navigate('/organizations')}>
              Back to Organizations
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const tree = buildTree()

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/organizations')}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-slate-400" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white">{organization.name}</h1>
            <p className="mt-1 text-slate-400">Organization Unit Details</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Button
            variant="ghost"
            onClick={() => navigate(`/organizations/${id}/edit`)}
          >
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Button>
          <Button
            variant="ghost"
            onClick={handleDelete}
            className="text-red-500 hover:text-red-400 hover:bg-red-500/10"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Organization Info Card */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-white">Information</h2>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-1 gap-4">
                <div>
                  <dt className="text-sm font-medium text-slate-400">Name</dt>
                  <dd className="mt-1 text-sm text-white">{organization.name}</dd>
                </div>
                {organization.description && (
                  <div>
                    <dt className="text-sm font-medium text-slate-400">Description</dt>
                    <dd className="mt-1 text-sm text-white">{organization.description}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-sm font-medium text-slate-400">ID</dt>
                  <dd className="mt-1 text-sm text-white">{organization.id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-slate-400">Created</dt>
                  <dd className="mt-1 text-sm text-white">
                    {new Date(organization.created_at).toLocaleString()}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-slate-400">Last Updated</dt>
                  <dd className="mt-1 text-sm text-white">
                    {new Date(organization.updated_at).toLocaleString()}
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {/* Metadata Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Metadata</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/organizations/${id}/metadata`)}
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Manage
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {metadata?.items && metadata.items.length > 0 ? (
                <dl className="grid grid-cols-1 gap-4">
                  {metadata.items.map((field: any) => (
                    <div key={field.id}>
                      <dt className="text-sm font-medium text-slate-400">{field.key}</dt>
                      <dd className="mt-1 text-sm text-white">
                        {typeof field.value === 'object'
                          ? JSON.stringify(field.value)
                          : String(field.value)}
                      </dd>
                    </div>
                  ))}
                </dl>
              ) : (
                <p className="text-sm text-slate-400">No metadata defined</p>
              )}
            </CardContent>
          </Card>

          {/* Issues Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Issues</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/issues?organization_id=${id}`)}
                >
                  View All
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {issues?.items && issues.items.length > 0 ? (
                <div className="space-y-3">
                  {issues.items.slice(0, 5).map((issue: any) => (
                    <div
                      key={issue.id}
                      className="p-3 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/issues/${issue.id}`)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-white truncate">
                            {issue.title}
                          </h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span
                              className={`text-xs px-2 py-0.5 rounded ${
                                issue.status === 'open'
                                  ? 'bg-green-500/20 text-green-400'
                                  : issue.status === 'in_progress'
                                  ? 'bg-blue-500/20 text-blue-400'
                                  : 'bg-slate-500/20 text-slate-400'
                              }`}
                            >
                              {issue.status}
                            </span>
                            <span className="text-xs text-slate-500">
                              #{issue.id}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {issues.items.length > 5 && (
                    <p className="text-xs text-slate-500 text-center">
                      +{issues.items.length - 5} more
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-slate-400">No issues</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Hierarchy Tree */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-white">Hierarchy</h2>
            </CardHeader>
            <CardContent>
              {tree.length > 0 ? (
                <div className="space-y-1">
                  {tree.map((node) => renderTreeNode(node))}
                </div>
              ) : (
                <p className="text-sm text-slate-400">
                  No child organizations or entities
                </p>
              )}
              <div className="mt-6 pt-6 border-t border-slate-700">
                <p className="text-xs text-slate-500 mb-3">
                  {childOrgs?.items?.length || 0} sub-organization(s)
                  <br />
                  {entities?.items?.length || 0} entity/entities
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/organizations/create?parent_id=${id}`)}
                  className="w-full justify-center"
                >
                  Add Sub-Organization
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(`/entities/create?organization_id=${id}`)}
                  className="w-full justify-center mt-2"
                >
                  Add Entity
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
