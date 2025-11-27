import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Settings,
  Shield,
  Database,
  Clock,
  CheckCircle,
  XCircle,
  FileText,
  Search,
  RefreshCw,
} from 'lucide-react'
import api from '@/lib/api'
import Card, { CardHeader, CardContent } from '@/components/Card'

export default function AdminSettings() {
  const [logSearch, setLogSearch] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.health(),
    refetchInterval: 30000,
  })

  const { data: profile } = useQuery({
    queryKey: ['portal-profile'],
    queryFn: () => api.getPortalProfile(),
  })

  const isAdmin = profile?.global_role === 'admin'

  const {
    data: logs,
    isLoading: logsLoading,
    refetch: refetchLogs,
  } = useQuery({
    queryKey: ['admin-logs'],
    queryFn: () => api.getLogs(),
    enabled: isAdmin && !isSearching,
  })

  const {
    data: searchResults,
    isLoading: searchLoading,
    refetch: refetchSearch,
  } = useQuery({
    queryKey: ['admin-logs-search', logSearch],
    queryFn: () => api.searchLogs(logSearch),
    enabled: isAdmin && isSearching && logSearch.length > 0,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (logSearch.trim()) {
      setIsSearching(true)
      refetchSearch()
    }
  }

  const handleClearSearch = () => {
    setLogSearch('')
    setIsSearching(false)
    refetchLogs()
  }

  const displayedLogs = isSearching ? searchResults : logs
  const isLoadingLogs = isSearching ? searchLoading : logsLoading

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
                Upgrade to Professional or Enterprise for advanced features like SSO, SCIM, and
                priority support.
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

      {/* System Logs - Admin Only */}
      {isAdmin && (
        <div className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between w-full">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  System Logs
                </h2>
                <button
                  onClick={() => (isSearching ? refetchSearch() : refetchLogs())}
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded"
                  title="Refresh logs"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoadingLogs ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Search Bar */}
              <form onSubmit={handleSearch} className="flex gap-2 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={logSearch}
                    onChange={(e) => setLogSearch(e.target.value)}
                    placeholder="Search logs..."
                    className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-600 rounded text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  disabled={!logSearch.trim()}
                >
                  Search
                </button>
                {isSearching && (
                  <button
                    type="button"
                    onClick={handleClearSearch}
                    className="px-4 py-2 bg-slate-600 text-white rounded hover:bg-slate-500"
                  >
                    Clear
                  </button>
                )}
              </form>

              {/* Log Info */}
              <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
                <span>
                  {isSearching
                    ? `${searchResults?.total_matches || 0} matches for "${searchResults?.query}"`
                    : `${logs?.total || 0} total lines`}
                </span>
                <span>Showing last {displayedLogs?.lines?.length || 0} lines</span>
              </div>

              {/* Log Content */}
              <div className="bg-slate-900 rounded border border-slate-700 p-4 max-h-96 overflow-auto font-mono text-xs">
                {isLoadingLogs ? (
                  <div className="text-slate-400 text-center py-4">Loading logs...</div>
                ) : displayedLogs?.lines?.length ? (
                  <pre className="text-slate-300 whitespace-pre-wrap break-all">
                    {displayedLogs.lines.join('\n')}
                  </pre>
                ) : (
                  <div className="text-slate-500 text-center py-4">
                    {isSearching ? 'No matches found' : 'No logs available'}
                  </div>
                )}
              </div>

              {displayedLogs?.log_file && (
                <div className="mt-2 text-xs text-slate-500">Log file: {displayedLogs.log_file}</div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
