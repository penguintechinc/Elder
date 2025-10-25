import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, User, Users, Bot, Shield } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

type IdentityType = 'human' | 'service' | 'bot'

export default function Identities() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<IdentityType | ''>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['identities', { search, type: typeFilter }],
    queryFn: () => api.getIdentities({
      search,
      identity_type: typeFilter || undefined,
    }),
  })

  const getIdentityIcon = (type: IdentityType) => {
    switch (type) {
      case 'human':
        return <User className="w-5 h-5 text-blue-400" />
      case 'service':
        return <Shield className="w-5 h-5 text-green-400" />
      case 'bot':
        return <Bot className="w-5 h-5 text-purple-400" />
      default:
        return <User className="w-5 h-5 text-slate-400" />
    }
  }

  const getTypeColor = (type: IdentityType) => {
    switch (type) {
      case 'human':
        return 'bg-blue-500/20 text-blue-400'
      case 'service':
        return 'bg-green-500/20 text-green-400'
      case 'bot':
        return 'bg-purple-500/20 text-purple-400'
      default:
        return 'bg-slate-500/20 text-slate-400'
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Identities</h1>
          <p className="mt-2 text-slate-400">
            Manage users, service accounts, and bots
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Identity
        </Button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            type="text"
            placeholder="Search identities..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as IdentityType | '')}
        >
          <option value="">All Types</option>
          <option value="human">Human</option>
          <option value="service">Service Account</option>
          <option value="bot">Bot</option>
        </Select>
      </div>

      {/* Identities List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data?.items?.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-400">No identities found</p>
            <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
              Create your first identity
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data?.items?.map((identity: any) => (
            <Card
              key={identity.id}
              className="cursor-pointer hover:ring-2 hover:ring-primary-500 transition-all"
              onClick={() => navigate(`/identities/${identity.id}`)}
            >
              <CardContent>
                <div className="flex items-start gap-3 mb-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getIdentityIcon(identity.identity_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-white mb-1 truncate">
                      {identity.full_name || identity.username}
                    </h3>
                    {identity.full_name && identity.username && (
                      <p className="text-sm text-slate-400 truncate">@{identity.username}</p>
                    )}
                  </div>
                  <div className="flex-shrink-0">
                    {identity.is_superuser && (
                      <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 bg-red-500/20 text-red-400 rounded">
                        <Shield className="w-3 h-3" />
                        Admin
                      </span>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${getTypeColor(identity.identity_type)}`}>
                      {identity.identity_type}
                    </span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        identity.is_active
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}
                    >
                      {identity.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  {identity.email && (
                    <p className="text-xs text-slate-500 truncate">{identity.email}</p>
                  )}

                  {identity.groups && identity.groups.length > 0 && (
                    <div className="flex items-center gap-1 text-xs text-slate-400">
                      <Users className="w-3 h-3" />
                      {identity.groups.length} group(s)
                    </div>
                  )}

                  <div className="pt-2 border-t border-slate-700">
                    <p className="text-xs text-slate-500">
                      Created {new Date(identity.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateIdentityModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['identities'] })
          }}
        />
      )}
    </div>
  )
}

interface CreateIdentityModalProps {
  onClose: () => void
  onSuccess: () => void
}

function CreateIdentityModal({ onClose, onSuccess }: CreateIdentityModalProps) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [identityType, setIdentityType] = useState<IdentityType>('human')
  const [password, setPassword] = useState('')

  const createMutation = useMutation({
    mutationFn: (data: {
      username: string
      email: string
      full_name?: string
      identity_type: string
      password: string
    }) => api.createIdentity(data),
    onSuccess: () => {
      toast.success('Identity created successfully')
      onSuccess()
    },
    onError: () => {
      toast.error('Failed to create identity')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      username,
      email,
      full_name: fullName || undefined,
      identity_type: identityType,
      password,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Create Identity</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Select
              label="Type"
              required
              value={identityType}
              onChange={(e) => setIdentityType(e.target.value as IdentityType)}
            >
              <option value="human">Human</option>
              <option value="service">Service Account</option>
              <option value="bot">Bot</option>
            </Select>
            <Input
              label="Username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
            />
            <Input
              label="Email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter email"
            />
            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Enter full name (optional)"
            />
            <Input
              label="Password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
            />
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
