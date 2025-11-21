import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Compass, Play, Trash2, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

const DISCOVERY_TYPES = [
  { value: 'aws', label: 'AWS Discovery' },
  { value: 'gcp', label: 'GCP Discovery' },
  { value: 'azure', label: 'Azure Discovery' },
  { value: 'kubernetes', label: 'Kubernetes Discovery' },
  { value: 'network', label: 'Network Scan' },
]

export default function Discovery() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedJob, setSelectedJob] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: jobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['discoveryJobs'],
    queryFn: () => api.getDiscoveryJobs(),
  })

  const { data: history } = useQuery({
    queryKey: ['discoveryHistory', selectedJob],
    queryFn: () => api.getDiscoveryJobHistory(selectedJob!),
    enabled: !!selectedJob,
  })

  const runJobMutation = useMutation({
    mutationFn: (id: number) => api.runDiscoveryJob(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['discoveryHistory'],
        refetchType: 'all'
      })
      toast.success('Discovery job started')
    },
  })

  const deleteJobMutation = useMutation({
    mutationFn: (id: number) => api.deleteDiscoveryJob(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['discoveryJobs'],
        refetchType: 'all'
      })
      toast.success('Discovery job deleted')
      if (selectedJob) {
        setSelectedJob(null)
      }
    },
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />
      case 'running':
        return <Clock className="w-5 h-5 text-yellow-400 animate-pulse" />
      default:
        return <AlertCircle className="w-5 h-5 text-slate-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400'
      case 'failed':
        return 'bg-red-500/20 text-red-400'
      case 'running':
        return 'bg-yellow-500/20 text-yellow-400'
      default:
        return 'bg-slate-500/20 text-slate-400'
    }
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Cloud Discovery</h1>
          <p className="mt-2 text-slate-400">Automatically discover and track cloud resources</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Discovery Job
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Discovery Jobs */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">Discovery Jobs</h2>
          {jobsLoading ? (
            <div className="flex justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : jobs?.jobs?.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Compass className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No discovery jobs configured</p>
                <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
                  Create your first discovery job
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {jobs?.jobs?.map((job: any) => (
                <Card
                  key={job.id}
                  className={selectedJob === job.id ? 'ring-2 ring-primary-500' : ''}
                >
                  <CardContent>
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 cursor-pointer" onClick={() => setSelectedJob(job.id)}>
                        <h3 className="text-lg font-semibold text-white">{job.name}</h3>
                        <p className="text-sm text-slate-400 mt-1">
                          {DISCOVERY_TYPES.find(t => t.value === job.discovery_type)?.label}
                        </p>
                        {job.schedule && (
                          <p className="text-sm text-slate-400">
                            <Clock className="w-4 h-4 inline mr-1" />
                            {job.schedule}
                          </p>
                        )}
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        job.enabled ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {job.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => runJobMutation.mutate(job.id)}>
                        <Play className="w-4 h-4 mr-2" />
                        Run Now
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => deleteJobMutation.mutate(job.id)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Job History */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">Run History</h2>
          {!selectedJob ? (
            <Card>
              <CardContent className="text-center py-12">
                <Clock className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">Select a discovery job to view run history</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {history?.runs?.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-12">
                    <Clock className="w-8 h-8 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400">No runs yet</p>
                  </CardContent>
                </Card>
              ) : (
                history?.runs?.map((run: any) => (
                  <Card key={run.id}>
                    <CardContent>
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(run.status)}
                          <div>
                            <p className="text-white font-medium">
                              {new Date(run.started_at).toLocaleString()}
                            </p>
                            {run.completed_at && (
                              <p className="text-sm text-slate-400">
                                Duration: {Math.round((new Date(run.completed_at).getTime() - new Date(run.started_at).getTime()) / 1000)}s
                              </p>
                            )}
                          </div>
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(run.status)}`}>
                          {run.status}
                        </span>
                      </div>
                      {run.entities_discovered > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-slate-300">
                            Discovered: <span className="font-semibold text-primary-400">{run.entities_discovered}</span> entities
                          </p>
                        </div>
                      )}
                      {run.error_message && (
                        <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded">
                          <p className="text-sm text-red-400">{run.error_message}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {showCreateModal && (
        <CreateJobModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={async () => {
            await queryClient.invalidateQueries({
              queryKey: ['discoveryJobs'],
              refetchType: 'all'
            })
            setShowCreateModal(false)
          }}
        />
      )}
    </div>
  )
}

function CreateJobModal({ onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [discoveryType, setDiscoveryType] = useState('')
  const [schedule, setSchedule] = useState('')
  const [config, setConfig] = useState('{}')
  const [orgId, setOrgId] = useState('')
  // v2.0.0: Credential integration
  const [credentialType, setCredentialType] = useState('static')
  const [credentialId, setCredentialId] = useState('')

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const { data: secrets } = useQuery({
    queryKey: ['secrets', orgId],
    queryFn: () => api.getSecrets({ organization_id: parseInt(orgId) }),
    enabled: credentialType === 'secret' && !!orgId,
  })

  const { data: keys } = useQuery({
    queryKey: ['keys', orgId],
    queryFn: () => api.getKeys({ organization_id: parseInt(orgId) }),
    enabled: credentialType === 'key' && !!orgId,
  })

  const { data: builtinSecrets } = useQuery({
    queryKey: ['builtinSecrets', orgId],
    queryFn: () => api.listBuiltinSecrets({ organization_id: parseInt(orgId) }),
    enabled: credentialType === 'builtin_secret' && !!orgId,
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createDiscoveryJob(data),
    onSuccess: () => {
      toast.success('Discovery job created')
      onSuccess()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create job')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const configObj = JSON.parse(config)
      const data: any = {
        name,
        provider_type: discoveryType,
        organization_id: parseInt(orgId),
        config: configObj,
        schedule: schedule || undefined,
        enabled: true,
      }

      // v2.0.0: Add credential information
      if (credentialType !== 'static') {
        data.credential_type = credentialType
        data.credential_id = parseInt(credentialId)
      }

      createMutation.mutate(data)
    } catch (err) {
      toast.error('Invalid JSON configuration')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Create Discovery Job</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="AWS Production Discovery"
            />
            <Select
              label="Discovery Type"
              required
              value={discoveryType}
              onChange={(e) => setDiscoveryType(e.target.value)}
              options={[
                { value: '', label: 'Select discovery type' },
                ...DISCOVERY_TYPES,
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
            <Input
              label="Schedule (Cron, optional)"
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              placeholder="0 2 * * *"
            />

            {/* v2.0.0: Credential Selection - Not needed for network scans */}
            {discoveryType !== 'network' && (
            <div className="pt-4 border-t border-slate-700">
              <h3 className="text-sm font-semibold text-white mb-3">Credentials (v2.0.0)</h3>
              <Select
                label="Credential Type"
                value={credentialType}
                onChange={(e) => {
                  setCredentialType(e.target.value)
                  setCredentialId('')
                }}
                options={[
                  { value: 'static', label: 'Static (in config JSON)' },
                  { value: 'secret', label: 'Secret Provider' },
                  { value: 'key', label: 'Key Provider' },
                  { value: 'builtin_secret', label: 'Built-in Secret' },
                ]}
              />

              {credentialType === 'secret' && (
                <Select
                  label="Select Secret"
                  value={credentialId}
                  onChange={(e) => setCredentialId(e.target.value)}
                  options={[
                    { value: '', label: 'Select a secret' },
                    ...(secrets?.secrets || []).map((s: any) => ({ value: s.id, label: s.name })),
                  ]}
                />
              )}

              {credentialType === 'key' && (
                <Select
                  label="Select Key"
                  value={credentialId}
                  onChange={(e) => setCredentialId(e.target.value)}
                  options={[
                    { value: '', label: 'Select a key' },
                    ...(keys?.keys || []).map((k: any) => ({ value: k.id, label: k.name })),
                  ]}
                />
              )}

              {credentialType === 'builtin_secret' && (
                <Select
                  label="Select Built-in Secret"
                  value={credentialId}
                  onChange={(e) => setCredentialId(e.target.value)}
                  options={[
                    { value: '', label: 'Select a built-in secret' },
                    ...(builtinSecrets?.secrets || []).map((s: any) => ({ value: s.id, label: s.name })),
                  ]}
                />
              )}

              {credentialType === 'static' && (
                <p className="text-sm text-slate-400 mt-2">
                  Credentials will be stored directly in the configuration JSON below
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Configuration (JSON)
              </label>
              <textarea
                value={config}
                onChange={(e) => setConfig(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono text-sm"
                rows={8}
                placeholder='{"region": "us-east-1", "services": ["ec2", "rds", "s3"]}'
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
