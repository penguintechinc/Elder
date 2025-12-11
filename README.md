# Elder

[![Continuous Integration](https://github.com/penguintechinc/elder/actions/workflows/ci.yml/badge.svg)](https://github.com/penguintechinc/elder/actions/workflows/ci.yml)
[![Docker Build](https://github.com/penguintechinc/elder/actions/workflows/docker-build.yml/badge.svg)](https://github.com/penguintechinc/elder/actions/workflows/docker-build.yml)
[![Test Coverage](https://codecov.io/gh/penguintechinc/elder/branch/main/graph/badge.svg)](https://codecov.io/gh/penguintechinc/elder)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/penguintechinc/elder/releases)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![License: Limited AGPL v3](https://img.shields.io/badge/License-Limited_AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)*
[![Docker](https://img.shields.io/badge/docker-latest-blue.svg)](https://hub.docker.com/r/penguintechinc/elder)

_*Limited AGPL v3 with preamble for fair use - Personal and Internal Use Only_

```
███████╗██╗     ██████╗ ███████╗██████╗
██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗
█████╗  ██║     ██║  ██║█████╗  ██████╔╝
██╔══╝  ██║     ██║  ██║██╔══╝  ██╔══██╗
███████╗███████╗██████╔╝███████╗██║  ██║
╚══════╝╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝

Entity, Element, and Relationship Tracking System
```

<p align="center">
  <img src="Elder-Logo.png" alt="Elder Logo" width="200">
</p>

> **Enterprise-grade infrastructure dependency tracking and visualization**

**Elder** is a comprehensive entity, element, and relationship tracking system designed for modern infrastructure management. Track dependencies, visualize relationships, and maintain control across complex organizational structures.

🌐 **[Website](https://elder.penguintech.io)** | 📚 **[Documentation](https://elder-docs.penguintech.io)** | 💬 **[Discussions](https://github.com/penguintechinc/elder/discussions)**

## Overview

Elder provides visibility into your infrastructure and organizational relationships through:

- **Entity Tracking**: Datacenters, VPCs, Compute, Network, Storage, Security, and Applications
- **Data Store Tracking**: S3, GCS, Azure Blob, NAS, SAN, databases with compliance metadata
- **Dependency Mapping**: Visualize relationships between entities
- **Organizational Hierarchy**: Manage Company → Department → Team structures
- **Unified IAM**: Manage identities across AWS, Azure, GCP, Okta, LDAP with group management
- **SSO Integration**: SAML 2.0, OpenID Connect (OIDC), and SCIM 2.0 provisioning
- **Secrets Management**: Integrate with Vault, AWS Secrets Manager, GCP Secret Manager
- **Network Topology**: Track VPCs, subnets, peering, VPN connections
- **Project Sync**: Bi-directional sync with GitHub, GitLab, Jira, Trello, OpenProject
- **Enterprise Features**: Audit logging, RBAC, MFA, SSO, multi-tenant, license management

## Screenshots

### Login & Dashboard

<table>
<tr>
<td width="50%">
<a href="docs/screenshots/login.png" target="_blank">
  <img src="docs/screenshots/login.png" alt="Login" style="max-width: 100%;">
</a>
<p align="center"><em>Login</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/dashboard.png" target="_blank">
  <img src="docs/screenshots/dashboard.png" alt="Dashboard" style="max-width: 100%;">
</a>
<p align="center"><em>Dashboard</em></p>
</td>
</tr>
</table>

### Asset Management

<table>
<tr>
<td width="50%">
<a href="docs/screenshots/organizations.png" target="_blank">
  <img src="docs/screenshots/organizations.png" alt="Organizations" style="max-width: 100%;">
</a>
<p align="center"><em>Organizations</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/entities.png" target="_blank">
  <img src="docs/screenshots/entities.png" alt="Entities" style="max-width: 100%;">
</a>
<p align="center"><em>Entities</em></p>
</td>
</tr>
<tr>
<td width="50%">
<a href="docs/screenshots/software.png" target="_blank">
  <img src="docs/screenshots/software.png" alt="Software" style="max-width: 100%;">
</a>
<p align="center"><em>Software</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/services.png" target="_blank">
  <img src="docs/screenshots/services.png" alt="Services" style="max-width: 100%;">
</a>
<p align="center"><em>Services</em></p>
</td>
</tr>
<tr>
<td width="50%">
<a href="docs/screenshots/data-stores.png" target="_blank">
  <img src="docs/screenshots/data-stores.png" alt="Data Stores" style="max-width: 100%;">
</a>
<p align="center"><em>Data Stores (v3.0.0)</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/dependencies.png" target="_blank">
  <img src="docs/screenshots/dependencies.png" alt="Dependencies" style="max-width: 100%;">
</a>
<p align="center"><em>Dependencies</em></p>
</td>
</tr>
</table>

### Project Tracking

<table>
<tr>
<td width="50%">
<a href="docs/screenshots/projects.png" target="_blank">
  <img src="docs/screenshots/projects.png" alt="Projects" style="max-width: 100%;">
</a>
<p align="center"><em>Projects</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/issues.png" target="_blank">
  <img src="docs/screenshots/issues.png" alt="Issues" style="max-width: 100%;">
</a>
<p align="center"><em>Issues</em></p>
</td>
</tr>
</table>

### Security & Identity

<table>
<tr>
<td width="50%">
<a href="docs/screenshots/identities.png" target="_blank">
  <img src="docs/screenshots/identities.png" alt="Identity Center" style="max-width: 100%;">
</a>
<p align="center"><em>Identity Center</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/secrets.png" target="_blank">
  <img src="docs/screenshots/secrets.png" alt="Secrets Management" style="max-width: 100%;">
</a>
<p align="center"><em>Secrets Management</em></p>
</td>
</tr>
<tr>
<td width="50%">
<a href="docs/screenshots/keys.png" target="_blank">
  <img src="docs/screenshots/keys.png" alt="API Keys" style="max-width: 100%;">
</a>
<p align="center"><em>API Keys</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/certificates.png" target="_blank">
  <img src="docs/screenshots/certificates.png" alt="Certificates" style="max-width: 100%;">
</a>
<p align="center"><em>Certificates</em></p>
</td>
</tr>
</table>

### Discovery & Profile

<table>
<tr>
<td width="50%">
<a href="docs/screenshots/discovery.png" target="_blank">
  <img src="docs/screenshots/discovery.png" alt="Discovery" style="max-width: 100%;">
</a>
<p align="center"><em>Discovery</em></p>
</td>
<td width="50%">
<a href="docs/screenshots/profile.png" target="_blank">
  <img src="docs/screenshots/profile.png" alt="Profile" style="max-width: 100%;">
</a>
<p align="center"><em>Profile</em></p>
</td>
</tr>
</table>

## Key Features

### Core Capabilities
- ✅ **Multi-Entity Support**: 8 entity categories with 30+ sub-types
- ✅ **Hierarchical Organizations**: Unlimited depth organizational structures
- ✅ **Dependency Graphs**: Visualize complex entity relationships
- ✅ **Full RBAC**: Role-based permissions with org-scoped access
- ✅ **Multi-Auth**: Local, SAML, OAuth2, OIDC, and LDAP authentication
- ✅ **RESTful & gRPC APIs**: Complete API coverage
- ✅ **Audit Logging**: Comprehensive audit trail for compliance

### v3.0.0 Highlights (Latest)
- **OpenID Connect (OIDC)**: Full OIDC support alongside SAML for SSO integration
- **Data Stores Tracking**: Track S3, GCS, Azure Blob, NAS, SAN, databases, and data lakes with compliance metadata (PII, PHI, PCI flags)
- **Group Membership Management**: Approval workflows, access requests, owner reviews, and multi-provider write-back (LDAP + Okta)
- **Okta Connector**: Full Okta identity provider with bidirectional sync and group management
- **SCIM 2.0 Provisioning**: Complete SCIM user provisioning with JIT provisioning support
- **Enhanced Key Management**: Improved crypto key schema with provider ARN, key types, and state tracking

### v2.x Highlights
- **Unified Identity Center**: Single page for all identity types (Users, Groups, Service Accounts, API Keys)
- **Multi-backend Secrets**: HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, Infisical
- **Network Topology**: VPCs, Subnets, Firewalls, Load Balancers with connection mapping
- **Project Sync**: Bi-directional sync with GitHub, GitLab, Jira, Trello, OpenProject
- **Cloud Connectors**: AWS, GCP, Kubernetes, Google Workspace, LDAP, iBoss, vCenter, FleetDM
- **SSL/TLS Certificate Management**: Track certificates with expiration, renewal, and compliance
- **Village ID System**: Universal hierarchical identifiers for all resources

### License Tiers

Elder uses a fair-use licensing model with the Limited AGPL v3 license:

- **Personal & Internal Use**: Free for individual and internal organizational use
- **Commercial Use**: Requires a commercial license from Penguin Tech Inc
- **Modifications**: Must be shared under the same license terms (AGPL)
- **SaaS Deployment**: Requires commercial license if providing Elder as a service

For commercial licensing inquiries: sales@penguintech.io

## Quick Start

### Prerequisites

- **Docker & Docker Compose V2**: Required for all services
- **Python 3.12+**: Backend API (included in Docker)
- **Node.js 18+**: Web UI build (included in Docker)
- **PostgreSQL 17**: Database (included in Docker Compose)
- **Redis 7**: Cache and session storage (included in Docker Compose)

### Installation

```bash
# Clone the repository
git clone https://github.com/penguintechinc/elder.git
cd elder

# Run setup
make setup

# Edit configuration
nano .env

# Start development environment
make dev
```

Access the services:
- **Elder Web UI**: http://localhost:3005
- **Elder API**: http://localhost:4000
- **API Docs**: http://localhost:4000/api/docs

### Docker Deployment

```bash
# Start all services
docker compose up -d

# Check health
curl http://localhost:4000/healthz
```

### Kubernetes Deployment

Elder supports deployment to Kubernetes clusters (MicroK8s, kind, k3s, or standard Kubernetes) using Helm.

**Quick Local Deployment:**

```bash
# Install to local Kubernetes cluster
cd infrastructure/helm/elder
helm dependency update
helm install elder . \
  --set config.secretKey="$(openssl rand -base64 32)" \
  --set postgresql.auth.password="$(openssl rand -base64 32)" \
  --set redis.auth.password="$(openssl rand -base64 32)"

# Wait for deployment
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=elder --timeout=5m

# Access via port-forward
kubectl port-forward svc/elder-api 8080:80
kubectl port-forward svc/elder-web 3000:80
```

**GitHub Actions CI/CD:**

Elder includes automated Kubernetes deployment via GitHub Actions. To set up:

```bash
# 1. Run the setup script on your cluster
./scripts/k8s/setup-github-serviceaccount.sh

# 2. Add the output secrets to GitHub:
#    - KUBE_CONFIG
#    - K8S_NAMESPACE
#    - SECRET_KEY
#    - POSTGRES_PASSWORD
#    - REDIS_PASSWORD

# 3. Push to main branch - automatic deployment!
```

**Resources:**
- 📖 [Local Kubernetes Setup Guide](docs/deployment/local-kubernetes-setup.md)
- 🔧 [GitHub Actions Kubernetes Deployment](docs/deployment/github-actions-k8s.md)
- ⚙️ [Helm Chart Documentation](infrastructure/helm/elder/README.md)

## Configuration

Key environment variables:

```bash
# Database (PyDAL supports PostgreSQL, MySQL, SQLite, Oracle, MSSQL)
DATABASE_URL=postgresql://elder:password@localhost:5432/elder

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# Authentication
SAML_ENABLED=true
OIDC_ENABLED=true
OAUTH2_ENABLED=true
LDAP_ENABLED=true

# License (optional)
LICENSE_KEY=PENG-XXXX-XXXX-XXXX-XXXX-XXXX

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
ADMIN_EMAIL=admin@example.com
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  React UI │ REST Clients │ gRPC Clients                 │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   API Layer                             │
│  Flask REST │ gRPC Server │ WebSocket                   │
│  JWT Auth │ RBAC │ Rate Limiting                        │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                            │
│  PyDAL (PostgreSQL, MySQL, SQLite, etc.)               │
│  Redis (Cache, Sessions)                                │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: Flask (Python 3.13), PyDAL
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, ReactFlow
- **Database**: PostgreSQL (recommended), MySQL, SQLite, Oracle, MSSQL
- **Cache**: Redis / Valkey
- **APIs**: REST (OpenAPI 3.0), gRPC
- **Auth**: JWT, SAML, OIDC, OAuth2, LDAP, SCIM 2.0
- **Connectors**: AWS, GCP, Kubernetes, Okta, LDAP, vCenter, FleetDM, iBoss
- **Monitoring**: Prometheus, Grafana

## Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | REST & gRPC API documentation |
| [Database Schema](docs/DATABASE.md) | Database structure and PyDAL usage |
| [Sync Documentation](docs/SYNC.md) | Project management sync setup |
| [Backup Configuration](docs/S3_BACKUP_CONFIGURATION.md) | S3 backup setup |
| [Usage Guide](docs/USAGE.md) | User guide and workflows |
| [Contributing](docs/CONTRIBUTING.md) | Contribution guidelines |
| [Release Notes](docs/RELEASE_NOTES.md) | Version history |

## Development

```bash
# Development
make dev              # Start postgres and redis
make dev-api          # Start Flask API
make dev-all          # Start all services

# Testing
make test             # Run all tests
make lint             # Run linters
make format           # Format code

# Docker
make docker-build     # Build Docker image
make docker-scan      # Scan for vulnerabilities
```

## Security

- ✅ Multi-factor authentication
- ✅ Fine-grained RBAC with org-scoped permissions
- ✅ TLS 1.3 enforcement
- ✅ Input validation with PyDAL validators
- ✅ SQL injection prevention
- ✅ Audit logging
- ✅ Container scanning with Trivy

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

Elder is licensed under the Limited AGPL v3 with Fair Use Preamble. See [LICENSE.md](docs/LICENSE.md) for details.

**License Highlights:**
- **Personal & Internal Use**: Free under AGPL-3.0
- **Commercial Use**: Requires commercial license
- **SaaS Deployment**: Requires commercial license if providing Elder as a service

### Contributor Employer Exception (GPL-2.0 Grant)

Companies employing official contributors receive GPL-2.0 access to community features:

- **Perpetual for Contributed Versions**: GPL-2.0 rights to versions where the employee contributed remain valid permanently, even after the employee leaves the company
- **Attribution Required**: Employee must be credited in CONTRIBUTORS, AUTHORS, commit history, or release notes
- **Future Versions**: New versions released after employment ends require standard licensing
- **Community Only**: Enterprise features still require a commercial license

This exception rewards contributors by providing lasting fair use rights to their employers. See [LICENSE.md](docs/LICENSE.md) for full terms.

## Support

- **Company Homepage**: [www.penguintech.io](https://www.penguintech.io)
- **Documentation**: [docs.penguintech.io/elder](https://docs.penguintech.io/elder)
- **Issues**: [GitHub Issues](https://github.com/penguintechinc/elder/issues)
- **Email**: support@penguintech.io

## Default Login Credentials

For local development and testing, Elder creates a default admin user:

| Field | Value |
|-------|-------|
| **URL** | http://localhost:3005 |
| **Email** | admin@localhost |
| **Password** | admin123 |
| **Tenant** | System (ID: 1) |

> **Warning**: Change the default password immediately in production environments by setting the `ADMIN_PASSWORD` environment variable before first startup.

---

**Elder** - Know Your Infrastructure, Understand Your Dependencies

© 2025 Penguin Tech Inc. All rights reserved.
