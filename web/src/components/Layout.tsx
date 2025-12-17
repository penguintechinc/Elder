import { useState } from 'react'
import { Link, useLocation, Outlet } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  LayoutDashboard,
  Building2,
  Box,
  GitBranch,
  AlertCircle,
  Tag,
  Search as SearchIcon,
  Map as MapIcon,
  FolderKanban,
  Flag,
  User,
  LogOut,
  Key,
  FileKey,
  Shield,
  Compass,
  Webhook,
  Database,
  Network,
  Settings,
  FileText,
  Users,
  ChevronDown,
  ChevronRight,
  Package,
  Server,
  Globe,
  HardDrive,
  Repeat2,
  Lock,
  Bug,
  Route,
  Layers,
} from 'lucide-react'
import api from '@/lib/api'

// Navigation organized by categories
const navigationCategories = [
  {
    items: [
      { name: 'Dashboard', href: '/', icon: LayoutDashboard },
      { name: 'Search', href: '/search', icon: SearchIcon },
      { name: 'Map', href: '/map', icon: MapIcon },
    ],
  },
  {
    header: 'Assets',
    collapsible: true,
    items: [
      { name: 'Entities', href: '/entities', icon: Box },
      { name: 'Organizations', href: '/organizations', icon: Building2 },
    ],
  },
  {
    header: 'Software & Services',
    collapsible: true,
    items: [
      { name: 'Software', href: '/software', icon: Package },
      { name: 'Services', href: '/services', icon: Server },
      { name: 'SBOM Dashboard', href: '/sbom', icon: Layers },
      { name: 'Service Endpoints', href: '/service-endpoints', icon: Route },
      { name: 'Vulnerabilities', href: '/vulnerabilities', icon: Bug },
    ],
  },
  {
    header: 'Tracking',
    collapsible: true,
    items: [
      { name: 'Issues', href: '/issues', icon: AlertCircle },
      { name: 'Labels', href: '/labels', icon: Tag },
      { name: 'Milestones', href: '/milestones', icon: Flag },
      { name: 'Projects', href: '/projects', icon: FolderKanban },
      { name: 'Data Stores', href: '/data-stores', icon: HardDrive },
    ],
  },
  {
    header: 'Security',
    collapsible: true,
    items: [
      { name: 'Identity Center', href: '/iam', icon: Shield },
      { name: 'Keys', href: '/keys', icon: Key },
      { name: 'Secrets', href: '/secrets', icon: Key },
      { name: 'Certificates', href: '/certificates', icon: FileKey },
    ],
  },
  {
    header: 'Infrastructure',
    collapsible: true,
    items: [
      { name: 'Dependencies', href: '/dependencies', icon: GitBranch },
      { name: 'Discovery', href: '/discovery', icon: Compass },
      { name: 'Networking', href: '/networking', icon: Network },
      { name: 'IPAM', href: '/ipam', icon: Globe },
    ],
  },
  {
    header: 'Operations',
    collapsible: true,
    items: [
      { name: 'Backups', href: '/backups', icon: Database },
      { name: 'Webhooks', href: '/webhooks', icon: Webhook },
    ],
  },
]

// Admin navigation - shown based on user role
const adminNavigation = [
  { name: 'Audit Logs', href: '/admin/audit-logs', icon: FileText, roles: ['admin', 'support', 'tenant_admin'] },
  { name: 'Settings', href: '/admin/settings', icon: Settings, roles: ['admin'] },
  { name: 'SSO Config', href: '/admin/sso', icon: Shield, roles: ['admin', 'tenant_admin'] },
  { name: 'Sync Config', href: '/admin/sync-config', icon: Repeat2, roles: ['admin'] },
  { name: 'License Policies', href: '/admin/license-policies', icon: Lock, roles: ['admin'] },
  { name: 'Tenants', href: '/admin/tenants', icon: Users, roles: ['admin'] },
]

export default function Layout() {
  const location = useLocation()

  // Track collapsed state for each category
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>({})

  // Fetch user profile for role-based navigation
  const { data: userProfile } = useQuery({
    queryKey: ['portal-profile'],
    queryFn: () => api.getPortalProfile(),
    staleTime: 60000, // Cache for 1 minute
    retry: false,
  })

  // Determine user roles for admin navigation visibility
  const globalRole = userProfile?.global_role
  const tenantRole = userProfile?.tenant_role

  // Filter admin navigation based on user roles
  const visibleAdminNav = adminNavigation.filter(item => {
    if (globalRole === 'admin') return item.roles.includes('admin')
    if (globalRole === 'support') return item.roles.includes('support')
    if (tenantRole === 'admin') return item.roles.includes('tenant_admin')
    return false
  })

  const toggleCategory = (header: string) => {
    setCollapsedCategories(prev => ({
      ...prev,
      [header]: !prev[header]
    }))
  }

  const handleLogout = () => {
    localStorage.removeItem('elder_token')
    localStorage.removeItem('elder_refresh_token')
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-slate-800 border-r border-slate-700">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-6 border-b border-slate-700">
            <img src="/elder-logo.png" alt="Elder Logo" className="h-12 w-auto" />
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 overflow-y-auto">
            {navigationCategories.map((category, categoryIndex) => {
              const isCollapsed = category.header ? collapsedCategories[category.header] : false

              return (
                <div key={categoryIndex} className={category.header ? 'mt-4' : ''}>
                  {category.header && (
                    <button
                      onClick={() => toggleCategory(category.header!)}
                      className="w-full flex items-center justify-between px-4 pb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider hover:text-slate-400 transition-colors"
                    >
                      <span>{category.header}</span>
                      {isCollapsed ? (
                        <ChevronRight className="w-3 h-3" />
                      ) : (
                        <ChevronDown className="w-3 h-3" />
                      )}
                    </button>
                  )}
                  {!isCollapsed && (
                    <div className="space-y-1">
                      {category.items.map((item) => {
                        const Icon = item.icon
                        const isActive = location.pathname === item.href ||
                          (item.href !== '/' && location.pathname.startsWith(item.href))

                        return (
                          <Link
                            key={item.name}
                            to={item.href}
                            className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                              isActive
                                ? 'bg-primary-600 text-white'
                                : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                            }`}
                          >
                            <Icon className="w-5 h-5 mr-3" />
                            {item.name}
                          </Link>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            })}

            {/* Admin Navigation - Role-based */}
            {visibleAdminNav.length > 0 && (
              <div className="mt-4">
                <button
                  onClick={() => toggleCategory('Administration')}
                  className="w-full flex items-center justify-between px-4 pb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider hover:text-slate-400 transition-colors"
                >
                  <span>Administration</span>
                  {collapsedCategories['Administration'] ? (
                    <ChevronRight className="w-3 h-3" />
                  ) : (
                    <ChevronDown className="w-3 h-3" />
                  )}
                </button>
                {!collapsedCategories['Administration'] && (
                  <div className="space-y-1">
                    {visibleAdminNav.map((item) => {
                      const Icon = item.icon
                      const isActive = location.pathname === item.href ||
                        location.pathname.startsWith(item.href)

                      return (
                        <Link
                          key={item.name}
                          to={item.href}
                          className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                            isActive
                              ? 'bg-yellow-600/20 text-yellow-500 border border-yellow-600/30'
                              : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                          }`}
                        >
                          <Icon className="w-5 h-5 mr-3" />
                          {item.name}
                        </Link>
                      )
                    })}
                  </div>
                )}
              </div>
            )}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-slate-700 space-y-1">
            <Link
              to="/profile"
              className={`flex items-center w-full px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                location.pathname === '/profile'
                  ? 'bg-primary-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              <User className="w-5 h-5 mr-3" />
              Profile
            </Link>
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-slate-300 rounded-lg hover:bg-slate-700 hover:text-white transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="min-h-screen">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
