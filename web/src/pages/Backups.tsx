import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Database, Play, Trash2, RotateCcw, Calendar } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

export default function Backups() {
  const [showCreateJobModal, setShowCreateJobModal] = useState(false)
  const [selectedBackup, setSelectedBackup] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: jobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['backupJobs'],
    queryFn: () => api.getBackupJobs(),
  })

  const { data: backups } = useQuery({
    queryKey: ['backups'],
    queryFn: () => api.getBackups(),
  })

  const runJobMutation = useMutation({
    mutationFn: (id: number) => api.runBackupJob(id),
    onSuccess: () => {
      toast.success('Backup job started')
      queryClient.invalidateQueries({ queryKey: ['backups'] })
    },
  })

  const deleteJobMutation = useMutation({
    mutationFn: (id: number) => api.deleteBackupJob(id),
    onSuccess: () => {
      toast.success('Backup job deleted')
      queryClient.invalidateQueries({ queryKey: ['backupJobs'] })
    },
  })

  const restoreMutation = useMutation({
    mutationFn: ({ id, dryRun }: { id: number; dryRun?: boolean }) =>
      api.restoreBackup(id, { dry_run: dryRun }),
    onSuccess: (data) => {
      if (data.dry_run) {
        toast.success('Dry run completed successfully')
      } else {
        toast.success('Restore completed successfully')
      }
    },
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Backup Management</h1>
          <p className="mt-2 text-slate-400">Configure backup jobs and restore data</p>
        </div>
        <Button onClick={() => setShowCreateJobModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Backup Job
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Backup Jobs */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">Backup Jobs</h2>
          {jobsLoading ? (
            <div className="flex justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <div className="space-y-4">
              {jobs?.jobs?.map((job: any) => (
                <Card key={job.id}>
                  <CardContent>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{job.name}</h3>
                        <p className="text-sm text-slate-400 mt-1">
                          <Calendar className="w-4 h-4 inline mr-1" />
                          {job.schedule}
                        </p>
                        <p className="text-sm text-slate-400">
                          Retention: {job.retention_days} days
                        </p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        job.enabled ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {job.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="ghost" onClick={() => runJobMutation.mutate(job.id)}>
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

        {/* Backups */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-4">Available Backups</h2>
          <div className="space-y-4">
            {backups?.backups?.map((backup: any) => (
              <Card key={backup.id}>
                <CardContent>
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-white font-medium">
                        {new Date(backup.created_at).toLocaleString()}
                      </h3>
                      <p className="text-sm text-slate-400">
                        Size: {(backup.size_bytes / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <span className={`inline-block mt-2 px-2 py-1 text-xs font-medium rounded ${
                        backup.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        backup.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {backup.status}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => restoreMutation.mutate({ id: backup.id, dryRun: true })}
                    >
                      <RotateCcw className="w-4 h-4 mr-2" />
                      Dry Run
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => {
                        if (confirm('Are you sure you want to restore this backup?')) {
                          restoreMutation.mutate({ id: backup.id })
                        }
                      }}
                    >
                      <RotateCcw className="w-4 h-4 mr-2" />
                      Restore
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {showCreateJobModal && (
        <CreateJobModal
          onClose={() => setShowCreateJobModal(false)}
          onSuccess={() => {
            setShowCreateJobModal(false)
            queryClient.invalidateQueries({ queryKey: ['backupJobs'] })
          }}
        />
      )}
    </div>
  )
}

function CreateJobModal({ onClose, onSuccess }: any) {
  const [name, setName] = useState('')
  const [schedule, setSchedule] = useState('0 2 * * *')
  const [retentionDays, setRetentionDays] = useState('30')
  const [orgId, setOrgId] = useState('')

  const { data: orgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.createBackupJob(data),
    onSuccess: () => {
      toast.success('Backup job created')
      onSuccess()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      name,
      schedule,
      retention_days: parseInt(retentionDays),
      organization_id: orgId ? parseInt(orgId) : undefined,
      enabled: true,
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">Create Backup Job</h2>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Daily Backup"
            />
            <Input
              label="Schedule (Cron)"
              required
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              placeholder="0 2 * * *"
            />
            <Input
              label="Retention Days"
              type="number"
              required
              value={retentionDays}
              onChange={(e) => setRetentionDays(e.target.value)}
            />
            <Select
              label="Organization (optional)"
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              options={[
                { value: '', label: 'All organizations' },
                ...(orgs?.items || []).map((o: any) => ({ value: o.id, label: o.name })),
              ]}
            />
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
