import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Card, { CardHeader, CardContent } from '@/components/Card'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [tenant, setTenant] = useState('Global')
  const navigate = useNavigate()

  // Check if guest login is enabled
  const { data: guestConfig } = useQuery({
    queryKey: ['guest-enabled'],
    queryFn: async () => {
      const response = await api.client.get('/auth/guest-enabled')
      return response.data
    },
    staleTime: 60000, // Cache for 1 minute
  })

  const loginMutation = useMutation({
    mutationFn: ({ email, password, tenant }: { email: string; password: string; tenant: string }) =>
      api.portalLogin(email, password, tenant === 'Global' ? 'system' : tenant),
    onSuccess: () => {
      toast.success('Login successful!')
      navigate('/')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Login failed')
    },
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    loginMutation.mutate({ email, password, tenant })
  }

  const handleGuestLogin = () => {
    // Login as guest user
    if (guestConfig?.username) {
      loginMutation.mutate({
        email: `${guestConfig.username}@localhost`,
        password: guestConfig.username, // Guest password defaults to same as username
        tenant: 'Global',
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-blue-950/20 to-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <img
            src="/elder-logo.png"
            alt="Elder Logo"
            className="w-32 h-32 mx-auto mb-4 drop-shadow-2xl"
          />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-yellow-500 to-amber-400 bg-clip-text text-transparent mb-2">Elder</h1>
          <p className="text-gray-500">Entity Relationship Tracking System</p>
        </div>

        <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
          <CardHeader>
            <h2 className="text-xl font-semibold text-gray-300">Sign In</h2>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                autoComplete="email"
              />
              <Input
                label="Password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
              />
              <Input
                label="Tenant"
                type="text"
                value={tenant}
                onChange={(e) => setTenant(e.target.value)}
                placeholder="Global"
                autoComplete="off"
              />
              <p className="text-xs text-gray-500 -mt-2">
                Leave as "Global" for system-wide access
              </p>
              <div className="flex flex-col gap-3 pt-4">
                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-yellow-600 to-amber-600 hover:from-yellow-500 hover:to-amber-500 text-gray-900 font-semibold"
                  isLoading={loginMutation.isPending}
                >
                  Sign In
                </Button>
                {guestConfig?.enabled && (
                  <Button
                    type="button"
                    variant="ghost"
                    className="w-full text-gray-400 hover:text-gray-300 hover:bg-gray-800/50"
                    onClick={handleGuestLogin}
                    disabled={loginMutation.isPending}
                  >
                    Continue as Guest (Read-Only)
                  </Button>
                )}
              </div>
            </form>

            <div className="mt-6 pt-6 border-t border-gray-800/50">
              <p className="text-sm text-gray-500 text-center">
                Don't have an account?{' '}
                <button
                  onClick={() => navigate('/register')}
                  className="text-yellow-500 hover:text-yellow-400 transition-colors font-medium"
                >
                  Register here
                </button>
              </p>
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-gray-600 mt-6">
          Default credentials: <span className="text-yellow-600">admin / admin123</span>
        </p>
      </div>
    </div>
  )
}
