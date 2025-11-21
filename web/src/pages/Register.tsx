import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Card, { CardHeader, CardContent } from '@/components/Card'

export default function Register() {
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [tenant, setTenant] = useState('Global')
  const navigate = useNavigate()

  const registerMutation = useMutation({
    mutationFn: (data: { email: string; password: string; full_name?: string; tenant?: string }) =>
      api.portalRegister(data),
    onSuccess: () => {
      toast.success('Registration successful! Please login.')
      navigate('/login')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Registration failed')
    },
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    registerMutation.mutate({
      email,
      password,
      full_name: fullName,
      tenant: tenant === 'Global' ? 'system' : tenant,
    })
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
            <h2 className="text-xl font-semibold text-gray-300">Create Account</h2>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                autoComplete="email"
              />
              <Input
                label="Full Name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your full name"
                autoComplete="name"
              />
              <Input
                label="Password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a password"
                autoComplete="new-password"
              />
              <Input
                label="Confirm Password"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your password"
                autoComplete="new-password"
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
                  isLoading={registerMutation.isPending}
                >
                  Create Account
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full text-gray-400 hover:text-gray-300 hover:bg-gray-800/50"
                  onClick={() => navigate('/login')}
                >
                  Back to Login
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
