import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Key, TestTube, Trash2, Lock, Unlock } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const PROVIDER_TYPES = [
  { value: 'aws_kms', label: 'AWS KMS' },
  { value: 'gcp_kms', label: 'GCP Cloud KMS' },
  { value: 'infisical', label: 'Infisical' },
]

export default function Keys() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEncryptModal, setShowEncryptModal] = useState(false)
  const [showDecryptModal, setShowDecryptModal] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['keyProviders'],
    queryFn: () => api.getKeyProviders(),
  })

  const testMutation = useMutation({
    mutationFn: (id: number) => api.testKeyProvider(id),
    onSuccess: () => toast.success('Connection test successful'),
    onError: () => toast.error('Connection test failed'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteKeyProvider(id),
    onSuccess: () => {
      toast.success('Key provider deleted')
      queryClient.invalidateQueries({ queryKey: ['keyProviders'] })
    },
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Key Management</h1>
          <p className="mt-2 text-slate-400">Manage encryption keys and KMS providers</p>
        </div>
        <div className="flex gap-3">
          <Button variant="ghost" onClick={() => setShowEncryptModal(true)}>
            <Lock className="w-4 h-4 mr-2" />
            Encrypt Data
          </Button>
          <Button variant="ghost" onClick={() => setShowDecryptModal(true)}>
            <Unlock className="w-4 h-4 mr-2" />
            Decrypt Data
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Provider
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.providers?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Key className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No key providers configured</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Add your first key provider
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
                        {PROVIDER_TYPES.find(t => t.value === provider.provider_type)?.label}
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
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setSelectedProvider(provider.id)
                      setShowEncryptModal(true)
                    }}
                  >
                    <Lock className="w-4 h-4 mr-2" />
                    Encrypt
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setSelectedProvider(provider.id)
                      setShowDecryptModal(true)
                    }}
                  >
                    <Unlock className="w-4 h-4 mr-2" />
                    Decrypt
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => testMutation.mutate(provider.id)}>
                    <TestTube className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => deleteMutation.mutate(provider.id)}>
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
            queryClient.invalidateQueries({ queryKey: ['keyProviders'] })
          }}
        />
      )}

      {showEncryptModal && (
        <EncryptModal
          providerId={selectedProvider}
          onClose={() => {
            setShowEncryptModal(false)
            setSelectedProvider(null)
          }}
        />
      )}

      {showDecryptModal && (
        <DecryptModal
          providerId={selectedProvider}
          onClose={() => {
            setShowDecryptModal(false)
            setSelectedProvider(null)
          }}
        />
      )}
    </div>
  )
}

function CreateProviderModal({ onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [providerType, setProviderType] = useState('')
  const [config, setConfig] = useState('{}')
  const [orgId, setOrgId] = useState('')

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createKeyProvider(data),
    onSuccess: () => {
      toast.success('Key provider created')
      onSuccess()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create provider')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const configObj = JSON.parse(config)
      createMutation.mutate({
        name,
        provider_type: providerType,
        organization_id: parseInt(orgId),
        config: configObj,
        enabled: true,
      })
    } catch (err) {
      toast.error('Invalid JSON configuration')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Add Key Provider</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Production KMS"
            />
            <Select
              label="Provider Type"
              required
              value={providerType}
              onChange={(e) => setProviderType(e.target.value)}
              options={[
                { value: '', label: 'Select provider type' },
                ...PROVIDER_TYPES,
              ]}
            />
            <Select
              label="Organization"
              required
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              options={[
                { value: '', label: 'Select organization' },
                ...(orgs?.items || []).map((o: any) => ({ value: o.id, label: o.name })),
              ]}
            />
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Configuration (JSON)
              </label>
              <textarea
                value={config}
                onChange={(e) => setConfig(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono text-sm"
                rows={8}
                placeholder='{"key_id": "...", "region": "us-east-1"}'
              />
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
              <Button type="submit" isLoading={createMutation.isPending}>Create</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

function EncryptModal({ providerId, onClose }: any) {
  const [plaintext, setPlaintext] = useState('')
  const [keyId, setKeyId] = useState('')
  const [ciphertext, setCiphertext] = useState('')

  const encryptMutation = useMutation({
    mutationFn: (data: any) => api.encryptData(data),
    onSuccess: (data) => {
      setCiphertext(data.ciphertext)
      toast.success('Data encrypted successfully')
    },
    onError: () => toast.error('Encryption failed'),
  })

  const handleEncrypt = () => {
    encryptMutation.mutate({
      provider_id: providerId,
      plaintext,
      key_id: keyId || undefined,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Encrypt Data</h2>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            label="Key ID (optional)"
            value={keyId}
            onChange={(e) => setKeyId(e.target.value)}
            placeholder="key-12345"
          />
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Plaintext</label>
            <textarea
              value={plaintext}
              onChange={(e) => setPlaintext(e.target.value)}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white"
              rows={4}
              placeholder="Enter data to encrypt..."
            />
          </div>
          {ciphertext && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Ciphertext</label>
              <textarea
                value={ciphertext}
                readOnly
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono text-sm"
                rows={4}
              />
            </div>
          )}
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={onClose}>Close</Button>
            <Button onClick={handleEncrypt} isLoading={encryptMutation.isPending}>
              <Lock className="w-4 h-4 mr-2" />
              Encrypt
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function DecryptModal({ providerId, onClose }: any) {
  const [ciphertext, setCiphertext] = useState('')
  const [keyId, setKeyId] = useState('')
  const [plaintext, setPlaintext] = useState('')

  const decryptMutation = useMutation({
    mutationFn: (data: any) => api.decryptData(data),
    onSuccess: (data) => {
      setPlaintext(data.plaintext)
      toast.success('Data decrypted successfully')
    },
    onError: () => toast.error('Decryption failed'),
  })

  const handleDecrypt = () => {
    decryptMutation.mutate({
      provider_id: providerId,
      ciphertext,
      key_id: keyId || undefined,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Decrypt Data</h2>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            label="Key ID (optional)"
            value={keyId}
            onChange={(e) => setKeyId(e.target.value)}
            placeholder="key-12345"
          />
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Ciphertext</label>
            <textarea
              value={ciphertext}
              onChange={(e) => setCiphertext(e.target.value)}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono text-sm"
              rows={4}
              placeholder="Enter encrypted data..."
            />
          </div>
          {plaintext && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Plaintext</label>
              <textarea
                value={plaintext}
                readOnly
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white"
                rows={4}
              />
            </div>
          )}
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={onClose}>Close</Button>
            <Button onClick={handleDecrypt} isLoading={decryptMutation.isPending}>
              <Unlock className="w-4 h-4 mr-2" />
              Decrypt
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
