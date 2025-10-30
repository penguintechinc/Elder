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
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import Milestones from './pages/Milestones'
import Labels from './pages/Labels'
import Search from './pages/Search'
import Login from './pages/Login'
import Register from './pages/Register'
import RelationshipGraph from './pages/RelationshipGraph'
import Profile from './pages/Profile'
// v1.2.0 Pages
import Secrets from './pages/Secrets'
import Keys from './pages/Keys'
import IAM from './pages/IAM'
import Discovery from './pages/Discovery'
import GoogleWorkspace from './pages/GoogleWorkspace'
import Webhooks from './pages/Webhooks'
import Backups from './pages/Backups'
// v2.0.0 Pages
import Networking from './pages/Networking'

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
        <Route path="profile" element={<Profile />} />
        <Route path="organizations" element={<Organizations />} />
        <Route path="organizations/:id" element={<OrganizationDetail />} />
        <Route path="relationships/:id" element={<RelationshipGraph />} />
        <Route path="entities" element={<Entities />} />
        <Route path="entities/:id" element={<EntityDetail />} />
        <Route path="dependencies" element={<Dependencies />} />
        <Route path="identities" element={<Identities />} />
        <Route path="issues" element={<Issues />} />
        <Route path="issues/:id" element={<IssueDetail />} />
        <Route path="projects" element={<Projects />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="milestones" element={<Milestones />} />
        <Route path="labels" element={<Labels />} />
        <Route path="secrets" element={<Secrets />} />
        <Route path="keys" element={<Keys />} />
        <Route path="iam" element={<IAM />} />
        <Route path="discovery" element={<Discovery />} />
        <Route path="google-workspace" element={<GoogleWorkspace />} />
        <Route path="webhooks" element={<Webhooks />} />
        <Route path="backups" element={<Backups />} />
        <Route path="networking" element={<Networking />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
