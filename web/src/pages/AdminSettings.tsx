import { useQuery } from '@tanstack/react-query'
import { Settings, Shield, Database, Clock, CheckCircle, XCircle } from 'lucide-react'
import api from '@/lib/api'
import Card, { CardHeader, CardContent } from '@/components/Card'

export default function AdminSettings() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.health(),
    refetchInterval: 30000,
  })

  const { data: profile } = useQuery({
    queryKey: ['portal-profile'],
    queryFn: () => api.getPortalProfile(),
  })

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">Admin Settings</h1>
        <p className="text-slate-400">System configuration and health status</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* System Health */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Shield className="w-5 h-5" />
              System Health
            </h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-300">API Status</span>
                {health?.status === 'healthy' ? (
                  <span className="flex items-center gap-2 text-green-400">
                    <CheckCircle className="w-4 h-4" />
                    Healthy
                  </span>
                ) : (
                  <span className="flex items-center gap-2 text-red-400">
                    <XCircle className="w-4 h-4" />
                    Unhealthy
                  </span>
                )}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Service</span>
                <span className="text-slate-400">{health?.service || 'Elder'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* License Info */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Database className="w-5 h-5" />
              License Information
            </h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Tier</span>
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400">
                  Community
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Status</span>
                <span className="text-green-400">Active</span>
              </div>
              <p className="text-sm text-slate-500 pt-2 border-t border-slate-700">
                Upgrade to Professional or Enterprise for advanced features like SSO, SCIM, and priority support.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* User Info */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Current User
            </h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Email</span>
                <span className="text-slate-400">{profile?.email || '-'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Global Role</span>
                <span className="text-slate-400">{profile?.global_role || 'None'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Tenant Role</span>
                <span className="text-slate-400">{profile?.tenant_role || '-'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">MFA</span>
                <span className="text-slate-400">
                  {profile?.mfa_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Feature Flags */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Enterprise Features
            </h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Multi-Tenancy</span>
                <XCircle className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Portal Users</span>
                <XCircle className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">SAML SSO</span>
                <XCircle className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">SCIM Provisioning</span>
                <XCircle className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Audit Logging</span>
                <XCircle className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-300">Compliance Reports</span>
                <XCircle className="w-4 h-4 text-slate-500" />
              </div>
            </div>
            <p className="text-sm text-slate-500 pt-3 mt-3 border-t border-slate-700">
              Add a license key to enable enterprise features.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
