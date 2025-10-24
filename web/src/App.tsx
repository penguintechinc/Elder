import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Organizations from './pages/Organizations'
import Entities from './pages/Entities'
import Dependencies from './pages/Dependencies'
import Identities from './pages/Identities'
import Issues from './pages/Issues'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App() {
  // Check if user has a token
  const hasToken = localStorage.getItem('elder_token')

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="organizations" element={<Organizations />} />
        <Route path="entities" element={<Entities />} />
        <Route path="dependencies" element={<Dependencies />} />
        <Route path="identities" element={<Identities />} />
        <Route path="issues" element={<Issues />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
