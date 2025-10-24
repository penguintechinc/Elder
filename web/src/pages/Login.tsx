import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Card, { CardHeader, CardContent } from '@/components/Card'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const loginMutation = useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      api.login(username, password),
    onSuccess: () => {
      toast.success('Login successful!')
      navigate('/')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Login failed')
    },
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    loginMutation.mutate({ username, password })
  }

  const handleSkip = () => {
    // Allow browsing without login (read-only mode)
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Elder</h1>
          <p className="text-slate-400">Entity Relationship Tracking System</p>
        </div>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold text-white">Sign In</h2>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                autoComplete="username"
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
              <div className="flex flex-col gap-3 pt-4">
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={loginMutation.isPending}
                >
                  Sign In
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full"
                  onClick={handleSkip}
                >
                  Continue as Guest (Read-Only)
                </Button>
              </div>
            </form>

            <div className="mt-6 pt-6 border-t border-slate-700">
              <p className="text-sm text-slate-400 text-center">
                Don't have an account?{' '}
                <button
                  onClick={() => navigate('/register')}
                  className="text-primary-400 hover:text-primary-300"
                >
                  Register here
                </button>
              </p>
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-slate-500 mt-6">
          Default credentials: admin / admin123
        </p>
      </div>
    </div>
  )
}
