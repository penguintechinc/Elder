import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Key, TestTube, Trash2, Edit, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const PROVIDER_TYPES = [
  { value: 'aws_secrets_manager', label: 'AWS Secrets Manager' },
  { value: 'gcp_secret_manager', label: 'GCP Secret Manager' },
  { value: 'infisical', label: 'Infisical' },
]

export default function Secrets() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState<number | null>(null)
  const [showSecrets, setShowSecrets] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['secretProviders'],
    queryFn: () => api.getSecretProviders(),
  })

  const testMutation = useMutation({
    mutationFn: (id: number) => api.testSecretProvider(id),
    onSuccess: (result) => {
      if (result.success) {
        toast.success('Provider connection successful')
      } else {
        toast.error(`Connection failed: ${result.message}`)
      }
    },
    onError: () => {
      toast.error('Failed to test provider')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteSecretProvider(id),
    onSuccess: () => {
      toast.success('Provider deleted')
      queryClient.invalidateQueries({ queryKey: ['secretProviders'] })
    },
    onError: () => {
      toast.error('Failed to delete provider')
    },
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Secrets Management</h1>
          <p className="mt-2 text-slate-400">Manage secret providers and access secrets securely</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Provider
        </Button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.providers?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Key className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No secret providers configured</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Add your first provider
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {data?.providers?.map((provider: any) => (
            <Card key={provider.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Key className="w-5 h-5 text-primary-400" />
                    <div>
                      <h3 className="text-lg font-semibold text-white">{provider.name}</h3>
                      <p className="text-sm text-slate-400">
                        {PROVIDER_TYPES.find(t => t.value === provider.provider_type)?.label || provider.provider_type}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    provider.enabled ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                  }`}>
                    {provider.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                {provider.description && (
                  <p className="text-sm text-slate-400 mb-4">{provider.description}</p>
                )}
                <div className="flex gap-2 flex-wrap">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setSelectedProvider(provider.id)
                      setShowSecrets(true)
                    }}
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    View Secrets
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => testMutation.mutate(provider.id)}
                    isLoading={testMutation.isPending}
                  >
                    <TestTube className="w-4 h-4 mr-2" />
                    Test
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => deleteMutation.mutate(provider.id)}
                    isLoading={deleteMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreateProviderModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['secretProviders'] })
          }}
        />
      )}

      {showSecrets && selectedProvider && (
        <SecretsListModal
          providerId={selectedProvider}
          onClose={() => {
            setShowSecrets(false)
            setSelectedProvider(null)
          }}
        />
      )}
    </div>
  )
}

function CreateProviderModal({ onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [providerType, setProviderType] = useState('aws_secrets_manager')
  const [description, setDescription] = useState('')
  const [orgId, setOrgId] = useState('')
  const [config, setConfig] = useState('{}')

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createSecretProvider(data),
    onSuccess: () => {
      toast.success('Provider created successfully')
      onSuccess()
    },
    onError: () => {
      toast.error('Failed to create provider')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const parsedConfig = JSON.parse(config)
      createMutation.mutate({
        name,
        provider_type: providerType,
        organization_id: parseInt(orgId),
        config: parsedConfig,
        description: description || undefined,
      })
    } catch (err) {
      toast.error('Invalid JSON configuration')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Add Secret Provider</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Production Secrets"
            />
            <Select
              label="Provider Type"
              required
              value={providerType}
              onChange={(e) => setProviderType(e.target.value)}
              options={PROVIDER_TYPES}
            />
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
                rows={2}
                className="block w-full px-4 py-2 text-sm bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Configuration (JSON)
              </label>
              <textarea
                value={config}
                onChange={(e) => setConfig(e.target.value)}
                rows={8}
                className="block w-full px-4 py-2 text-sm font-mono bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500"
                placeholder={'{\n  "region": "us-east-1",\n  "access_key_id": "...",\n  "secret_access_key": "..."\n}'}
              />
              <p className="text-xs text-slate-500 mt-1">
                {providerType === 'aws_secrets_manager' && 'AWS: region, access_key_id, secret_access_key'}
                {providerType === 'gcp_secret_manager' && 'GCP: project_id, credentials (JSON key)'}
                {providerType === 'infisical' && 'Infisical: site_url, client_id, client_secret'}
              </p>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" isLoading={createMutation.isPending}>
                Create Provider
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

function SecretsListModal({ providerId, onClose }: any) {
  const [showValues, setShowValues] = useState<Record<string, boolean>>({})

  const { data, isLoading } = useQuery({
    queryKey: ['secrets', providerId],
    queryFn: () => api.listSecrets(providerId),
  })

  const getSecretMutation = useMutation({
    mutationFn: ({ secretName }: { secretName: string }) =>
      api.getSecret(providerId, secretName),
  })

  const toggleSecret = async (secretName: string) => {
    if (showValues[secretName]) {
      setShowValues(prev => ({ ...prev, [secretName]: false }))
    } else {
      try {
        await getSecretMutation.mutateAsync({ secretName })
        setShowValues(prev => ({ ...prev, [secretName]: true }))
      } catch (err) {
        toast.error('Failed to fetch secret value')
      }
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Secrets</h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : data?.secrets?.length === 0 ? (
            <p className="text-center text-slate-400 py-8">No secrets found</p>
          ) : (
            <div className="space-y-2">
              {data?.secrets?.map((secret: any) => (
                <div
                  key={secret.name}
                  className="flex items-center justify-between p-3 bg-slate-800 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="text-white font-medium">{secret.name}</p>
                    {showValues[secret.name] && getSecretMutation.data && (
                      <p className="text-sm text-slate-400 mt-1 font-mono break-all">
                        {getSecretMutation.data.value}
                      </p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => toggleSecret(secret.name)}
                  >
                    {showValues[secret.name] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
