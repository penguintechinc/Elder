import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileText, Download, Filter, CheckCircle, XCircle } from 'lucide-react'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Card, { CardHeader, CardContent } from '@/components/Card'
import type { AuditLog } from '@/types'

export default function AuditLogs() {
  const [filters, setFilters] = useState({
    action: '',
    resource_type: '',
    start_date: '',
    end_date: '',
    success: '' as '' | 'true' | 'false',
  })
  const [limit] = useState(50)
  const [offset, setOffset] = useState(0)

  const { data, isLoading } = useQuery({
    queryKey: ['audit-logs', filters, limit, offset],
    queryFn: () => api.getAuditLogs({
      action: filters.action || undefined,
      resource_type: filters.resource_type || undefined,
      start_date: filters.start_date || undefined,
      end_date: filters.end_date || undefined,
      success: filters.success === '' ? undefined : filters.success === 'true',
      limit,
      offset,
    }),
  })

  const logs = data?.logs || []
  const total = data?.total || 0

  const handleExport = async () => {
    try {
      const result = await api.exportAuditLogs({
        start_date: filters.start_date || undefined,
        end_date: filters.end_date || undefined,
        format: 'json',
      })
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  const getActionColor = (action: string) => {
    if (action.includes('create')) return 'text-green-400'
    if (action.includes('delete')) return 'text-red-400'
    if (action.includes('update')) return 'text-blue-400'
    if (action.includes('login')) return 'text-yellow-400'
    return 'text-slate-400'
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">Audit Logs</h1>
        <p className="text-slate-400">View and export system audit logs for compliance</p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-300">Filters</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Input
              placeholder="Action"
              value={filters.action}
              onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            />
            <Input
              placeholder="Resource Type"
              value={filters.resource_type}
              onChange={(e) => setFilters({ ...filters, resource_type: e.target.value })}
            />
            <Input
              type="date"
              placeholder="Start Date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            />
            <Input
              type="date"
              placeholder="End Date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            />
            <select
              value={filters.success}
              onChange={(e) => setFilters({ ...filters, success: e.target.value as '' | 'true' | 'false' })}
              className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white"
            >
              <option value="">All Status</option>
              <option value="true">Success</option>
              <option value="false">Failed</option>
            </select>
          </div>
          <div className="flex justify-end mt-4">
            <Button variant="ghost" onClick={handleExport}>
              <Download className="w-4 h-4 mr-2" />
              Export JSON
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">
              Audit Events ({total} total)
            </h2>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-slate-400">Loading logs...</div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-slate-500 mx-auto mb-4" />
              <p className="text-slate-400">No audit logs found</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Timestamp</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Action</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Resource</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Status</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">IP Address</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log: AuditLog) => (
                      <tr key={log.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                        <td className="py-3 px-4 text-sm text-slate-300">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                        <td className={`py-3 px-4 text-sm font-medium ${getActionColor(log.action)}`}>
                          {log.action}
                        </td>
                        <td className="py-3 px-4 text-sm text-slate-300">
                          {log.resource_type}
                          {log.resource_id && ` #${log.resource_id}`}
                        </td>
                        <td className="py-3 px-4">
                          {log.success ? (
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-400" />
                          )}
                        </td>
                        <td className="py-3 px-4 text-sm text-slate-400">
                          {log.ip_address || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {total > limit && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700">
                  <p className="text-sm text-slate-400">
                    Showing {offset + 1} to {Math.min(offset + limit, total)} of {total}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={offset === 0}
                      onClick={() => setOffset(Math.max(0, offset - limit))}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={offset + limit >= total}
                      onClick={() => setOffset(offset + limit)}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
