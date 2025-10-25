import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { User, Mail, Building2, Save, X } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Card, { CardHeader, CardContent } from '@/components/Card'
import Input from '@/components/Input'
import Select from '@/components/Select'

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    organization_id: null as number | null,
  })
  const queryClient = useQueryClient()

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.getProfile(),
  })

  const { data: orgsData } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations({ per_page: 1000 }),
  })

  const updateMutation = useMutation({
    mutationFn: (data: Partial<typeof formData>) => api.updateProfile(data),
    onSuccess: () => {
      toast.success('Profile updated successfully')
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setIsEditing(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update profile')
    },
  })

  const handleEdit = () => {
    if (profile) {
      setFormData({
        email: profile.email || '',
        full_name: profile.full_name || '',
        organization_id: profile.organization_id,
      })
      setIsEditing(true)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    setFormData({
      email: '',
      full_name: '',
      organization_id: null,
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  if (profileLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Profile</h1>
        <p className="mt-2 text-slate-400">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Profile Information Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center">
                <User className="w-6 h-6 text-primary-400" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Profile Information</h2>
                <p className="text-sm text-slate-400">Your personal details and organization</p>
              </div>
            </div>
            {!isEditing && (
              <Button onClick={handleEdit} variant="outline">
                Edit Profile
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username (read-only) */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Username
                </label>
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-400">
                  <User className="w-4 h-4" />
                  <span>{profile?.username}</span>
                  <span className="ml-auto text-xs text-slate-500">Read-only</span>
                </div>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="pl-10"
                    placeholder="your.email@example.com"
                  />
                </div>
              </div>

              {/* Full Name */}
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-slate-300 mb-2">
                  Full Name
                </label>
                <Input
                  id="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="John Doe"
                />
              </div>

              {/* Organization */}
              <div>
                <label htmlFor="organization" className="block text-sm font-medium text-slate-300 mb-2">
                  Organization
                </label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none z-10" />
                  <Select
                    id="organization"
                    value={formData.organization_id?.toString() || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      organization_id: e.target.value ? parseInt(e.target.value) : null
                    })}
                    className="pl-10"
                  >
                    <option value="">No Organization</option>
                    {orgsData?.items?.map((org: any) => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCancel}
                  disabled={updateMutation.isPending}
                  className="flex items-center gap-2"
                >
                  <X className="w-4 h-4" />
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              {/* Username */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Username
                </label>
                <div className="flex items-center gap-2 text-white">
                  <User className="w-4 h-4 text-slate-400" />
                  <span>{profile?.username}</span>
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Email
                </label>
                <div className="flex items-center gap-2 text-white">
                  <Mail className="w-4 h-4 text-slate-400" />
                  <span>{profile?.email || 'Not set'}</span>
                </div>
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Full Name
                </label>
                <div className="flex items-center gap-2 text-white">
                  <User className="w-4 h-4 text-slate-400" />
                  <span>{profile?.full_name || 'Not set'}</span>
                </div>
              </div>

              {/* Organization */}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">
                  Organization
                </label>
                <div className="flex items-center gap-2 text-white">
                  <Building2 className="w-4 h-4 text-slate-400" />
                  <span>{profile?.organization_name || 'No organization assigned'}</span>
                </div>
              </div>

              {/* Additional Info */}
              <div className="grid grid-cols-2 gap-6 pt-6 border-t border-slate-700">
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">
                    Identity Type
                  </label>
                  <div className="inline-flex px-3 py-1 rounded-full text-sm font-medium bg-blue-500/20 text-blue-400">
                    {profile?.identity_type}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">
                    Authentication Provider
                  </label>
                  <div className="text-white">
                    {profile?.auth_provider}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">
                    Account Status
                  </label>
                  <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                    profile?.is_active
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {profile?.is_active ? 'Active' : 'Inactive'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-400 mb-2">
                    MFA Status
                  </label>
                  <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                    profile?.mfa_enabled
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-slate-500/20 text-slate-400'
                  }`}>
                    {profile?.mfa_enabled ? 'Enabled' : 'Disabled'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
