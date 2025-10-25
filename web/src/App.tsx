import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Organizations from './pages/Organizations'
import OrganizationDetail from './pages/OrganizationDetail'
import Entities from './pages/Entities'
import EntityDetail from './pages/EntityDetail'
import Dependencies from './pages/Dependencies'
import Identities from './pages/Identities'
import Issues from './pages/Issues'
import IssueDetail from './pages/IssueDetail'
import Labels from './pages/Labels'
import Search from './pages/Search'
import Login from './pages/Login'
import Register from './pages/Register'

// Protected route wrapper component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const hasToken = localStorage.getItem('elder_token')

  if (!hasToken) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="search" element={<Search />} />
        <Route path="organizations" element={<Organizations />} />
        <Route path="organizations/:id" element={<OrganizationDetail />} />
        <Route path="entities" element={<Entities />} />
        <Route path="entities/:id" element={<EntityDetail />} />
        <Route path="dependencies" element={<Dependencies />} />
        <Route path="identities" element={<Identities />} />
        <Route path="issues" element={<Issues />} />
        <Route path="issues/:id" element={<IssueDetail />} />
        <Route path="labels" element={<Labels />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
