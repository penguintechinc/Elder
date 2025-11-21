import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Shield, Key, Plus, Trash2, Edit, RefreshCw, Copy } from 'lucide-react'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Card, { CardHeader, CardContent } from '@/components/Card'
import type { IdPConfiguration, SCIMConfiguration } from '@/types'

export default function SSOConfiguration() {
  const [activeTab, setActiveTab] = useState<'idp' | 'scim'>('idp')
  const [showCreateIdP, setShowCreateIdP] = useState(false)
  const [editingIdP, setEditingIdP] = useState<IdPConfiguration | null>(null)
  const [idpFormData, setIdpFormData] = useState({
    name: '',
    idp_type: 'saml',
    entity_id: '',
    metadata_url: '',
    sso_url: '',
    slo_url: '',
    certificate: '',
    jit_provisioning_enabled: true,
    default_role: 'reader',
  })
  const queryClient = useQueryClient()

  const { data: idpConfigs, isLoading: idpLoading } = useQuery({
    queryKey: ['idp-configs'],
    queryFn: () => api.getIdPConfigs(),
  })

  const createIdPMutation = useMutation({
    mutationFn: (data: typeof idpFormData) => api.createIdPConfig(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['idp-configs'] })
      toast.success('IdP configuration created')
      setShowCreateIdP(false)
      resetIdPForm()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create IdP config')
    },
  })

  const updateIdPMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<typeof idpFormData> }) =>
      api.updateIdPConfig(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['idp-configs'] })
      toast.success('IdP configuration updated')
      setEditingIdP(null)
      resetIdPForm()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update IdP config')
    },
  })

  const deleteIdPMutation = useMutation({
    mutationFn: (id: number) => api.deleteIdPConfig(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['idp-configs'] })
      toast.success('IdP configuration deleted')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete IdP config')
    },
  })

  const resetIdPForm = () => {
    setIdpFormData({
      name: '',
      idp_type: 'saml',
      entity_id: '',
      metadata_url: '',
      sso_url: '',
      slo_url: '',
      certificate: '',
      jit_provisioning_enabled: true,
      default_role: 'reader',
    })
  }

  const handleEditIdP = (config: IdPConfiguration) => {
    setEditingIdP(config)
    setIdpFormData({
      name: config.name,
      idp_type: config.idp_type,
      entity_id: config.entity_id || '',
      metadata_url: config.metadata_url || '',
      sso_url: config.sso_url || '',
      slo_url: config.slo_url || '',
      certificate: config.certificate || '',
      jit_provisioning_enabled: config.jit_provisioning_enabled,
      default_role: config.default_role,
    })
  }

  const handleCreateIdP = (e: React.FormEvent) => {
    e.preventDefault()
    createIdPMutation.mutate(idpFormData)
  }

  const handleUpdateIdP = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingIdP) {
      updateIdPMutation.mutate({ id: editingIdP.id, data: idpFormData })
    }
  }

  const handleDeleteIdP = (config: IdPConfiguration) => {
    if (confirm(`Delete IdP configuration "${config.name}"?`)) {
      deleteIdPMutation.mutate(config.id)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">SSO Configuration</h1>
        <p className="text-slate-400">Configure SAML/OIDC identity providers and SCIM provisioning</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={activeTab === 'idp' ? 'primary' : 'ghost'}
          onClick={() => setActiveTab('idp')}
        >
          <Shield className="w-4 h-4 mr-2" />
          Identity Providers
        </Button>
        <Button
          variant={activeTab === 'scim' ? 'primary' : 'ghost'}
          onClick={() => setActiveTab('scim')}
        >
          <Key className="w-4 h-4 mr-2" />
          SCIM Provisioning
        </Button>
      </div>

      {/* IdP Tab */}
      {activeTab === 'idp' && (
        <div>
          <div className="flex justify-end mb-4">
            <Button onClick={() => setShowCreateIdP(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add IdP Configuration
            </Button>
          </div>

          {idpLoading ? (
            <div className="text-center py-8 text-slate-400">Loading configurations...</div>
          ) : !idpConfigs || idpConfigs.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <Shield className="w-12 h-12 text-slate-500 mx-auto mb-4" />
                <p className="text-slate-400">No identity providers configured</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {idpConfigs.map((config: IdPConfiguration) => (
                <Card key={config.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-white">{config.name}</h3>
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-500/20 text-blue-400">
                            {config.idp_type.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-slate-400 mt-1">
                          Entity ID: {config.entity_id || 'Not set'} •
                          JIT: {config.jit_provisioning_enabled ? 'Enabled' : 'Disabled'} •
                          Default Role: {config.default_role}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => handleEditIdP(config)}>
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteIdP(config)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* SCIM Tab */}
      {activeTab === 'scim' && (
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-white">SCIM 2.0 Provisioning</h2>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400 mb-4">
              SCIM (System for Cross-domain Identity Management) enables automatic user provisioning
              from your identity provider.
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  SCIM Endpoint URL
                </label>
                <div className="flex gap-2">
                  <Input
                    value={`${window.location.origin}/api/v1/scim`}
                    readOnly
                    className="flex-1"
                  />
                  <Button
                    variant="ghost"
                    onClick={() => copyToClipboard(`${window.location.origin}/api/v1/scim`)}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Bearer Token
                </label>
                <p className="text-sm text-slate-400">
                  Configure SCIM in Tenant Settings to generate a bearer token for your IdP.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create/Edit IdP Modal */}
      {(showCreateIdP || editingIdP) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 w-full max-w-lg my-8">
            <h3 className="text-xl font-semibold text-white mb-4">
              {editingIdP ? 'Edit IdP Configuration' : 'Add IdP Configuration'}
            </h3>
            <form onSubmit={editingIdP ? handleUpdateIdP : handleCreateIdP} className="space-y-4">
              <Input
                label="Name"
                required
                value={idpFormData.name}
                onChange={(e) => setIdpFormData({ ...idpFormData, name: e.target.value })}
                placeholder="Okta, Azure AD, etc."
              />
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Type</label>
                <select
                  value={idpFormData.idp_type}
                  onChange={(e) => setIdpFormData({ ...idpFormData, idp_type: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white"
                >
                  <option value="saml">SAML 2.0</option>
                  <option value="oidc">OpenID Connect</option>
                </select>
              </div>
              <Input
                label="Entity ID"
                value={idpFormData.entity_id}
                onChange={(e) => setIdpFormData({ ...idpFormData, entity_id: e.target.value })}
                placeholder="https://idp.example.com/..."
              />
              <Input
                label="Metadata URL"
                value={idpFormData.metadata_url}
                onChange={(e) => setIdpFormData({ ...idpFormData, metadata_url: e.target.value })}
                placeholder="https://idp.example.com/metadata"
              />
              <Input
                label="SSO URL"
                value={idpFormData.sso_url}
                onChange={(e) => setIdpFormData({ ...idpFormData, sso_url: e.target.value })}
                placeholder="https://idp.example.com/sso"
              />
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Default Role</label>
                <select
                  value={idpFormData.default_role}
                  onChange={(e) => setIdpFormData({ ...idpFormData, default_role: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white"
                >
                  <option value="reader">Reader</option>
                  <option value="editor">Editor</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="jit"
                  checked={idpFormData.jit_provisioning_enabled}
                  onChange={(e) => setIdpFormData({ ...idpFormData, jit_provisioning_enabled: e.target.checked })}
                  className="rounded border-slate-600"
                />
                <label htmlFor="jit" className="text-sm text-slate-300">
                  Enable JIT (Just-in-Time) Provisioning
                </label>
              </div>
              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  className="flex-1"
                  isLoading={createIdPMutation.isPending || updateIdPMutation.isPending}
                >
                  {editingIdP ? 'Save Changes' : 'Create Configuration'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="flex-1"
                  onClick={() => {
                    setShowCreateIdP(false)
                    setEditingIdP(null)
                    resetIdPForm()
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
