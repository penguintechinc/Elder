import { Link, useLocation, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  Building2,
  Box,
  GitBranch,
  Users,
  AlertCircle,
  Tag,
  Search as SearchIcon,
  Settings,
  LogOut,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Search', href: '/search', icon: SearchIcon },
  { name: 'Organizations', href: '/organizations', icon: Building2 },
  { name: 'Entities', href: '/entities', icon: Box },
  { name: 'Dependencies', href: '/dependencies', icon: GitBranch },
  { name: 'Identities', href: '/identities', icon: Users },
  { name: 'Issues', href: '/issues', icon: AlertCircle },
  { name: 'Labels', href: '/labels', icon: Tag },
]

export default function Layout() {
  const location = useLocation()

  const handleLogout = () => {
    localStorage.removeItem('elder_token')
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-slate-800 border-r border-slate-700">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-6 border-b border-slate-700">
            <h1 className="text-2xl font-bold text-white">
              Elder
            </h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
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
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-slate-700">
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
