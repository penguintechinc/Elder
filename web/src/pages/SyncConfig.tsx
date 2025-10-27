/**
 * Sync Configuration Page
 *
 * Provides UI for managing two-way synchronization with external platforms:
 * - GitHub
 * - GitLab
 * - Jira
 * - Trello
 * - OpenProject
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface SyncConfig {
  id: number;
  name: string;
  platform: string;
  enabled: boolean;
  sync_interval: number;
  batch_fallback_enabled: boolean;
  two_way_create: boolean;
  last_sync_at?: string;
}

interface SyncStatus {
  configs: {
    total: number;
    enabled: number;
  };
  recent_activity: {
    syncs_24h: number;
    failures_24h: number;
  };
  conflicts: {
    unresolved: number;
  };
}

export default function SyncConfig() {
  const [configs, setConfigs] = useState<SyncConfig[]>([]);
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchConfigs();
    fetchStatus();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await fetch('/api/v1/sync/configs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setConfigs(data.configs);
    } catch (error) {
      console.error('Failed to fetch sync configs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/v1/sync/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch sync status:', error);
    }
  };

  const toggleConfig = async (id: number, enabled: boolean) => {
    try {
      await fetch(`/api/v1/sync/configs/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ enabled: !enabled }),
      });
      fetchConfigs();
    } catch (error) {
      console.error('Failed to toggle config:', error);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Synchronization Configuration</h1>

        {/* Status Summary */}
        {status && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-500 text-sm">Total Configs</div>
              <div className="text-3xl font-bold">{status.configs.total}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-500 text-sm">Enabled</div>
              <div className="text-3xl font-bold text-green-600">{status.configs.enabled}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-500 text-sm">Syncs (24h)</div>
              <div className="text-3xl font-bold">{status.recent_activity.syncs_24h}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-500 text-sm">Unresolved Conflicts</div>
              <div className="text-3xl font-bold text-red-600">{status.conflicts.unresolved}</div>
            </div>
          </div>
        )}

        {/* Configurations Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">Sync Configurations</h2>
          </div>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Interval
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Sync
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {configs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No sync configurations found
                  </td>
                </tr>
              ) : (
                configs.map((config) => (
                  <tr key={config.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{config.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {config.platform}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          config.enabled
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {config.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {config.sync_interval}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {config.last_sync_at
                        ? new Date(config.last_sync_at).toLocaleString()
                        : 'Never'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => toggleConfig(config.id, config.enabled)}
                        className="text-indigo-600 hover:text-indigo-900 mr-4"
                      >
                        {config.enabled ? 'Disable' : 'Enable'}
                      </button>
                      <button
                        onClick={() => navigate(`/sync/${config.id}`)}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
