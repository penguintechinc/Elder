# Elder

[![Continuous Integration](https://github.com/penguintechinc/elder/actions/workflows/ci.yml/badge.svg)](https://github.com/penguintechinc/elder/actions/workflows/ci.yml)
[![Docker Build](https://github.com/penguintechinc/elder/actions/workflows/docker-build.yml/badge.svg)](https://github.com/penguintechinc/elder/actions/workflows/docker-build.yml)
[![Test Coverage](https://codecov.io/gh/penguintechinc/elder/branch/main/graph/badge.svg)](https://codecov.io/gh/penguintechinc/elder)
[![Version](https://img.shields.io/badge/version-2.0.1-green.svg)](https://github.com/penguintechinc/elder/releases)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)*
[![Docker](https://img.shields.io/badge/docker-latest-blue.svg)](https://hub.docker.com/r/penguintechinc/elder)

_*Personal and Internal Use Only_

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
- **Dependency Mapping**: Visualize relationships between entities
- **Organizational Hierarchy**: Manage Company → Department → Team structures
- **Unified IAM**: Manage identities across AWS, Azure, GCP, Okta, LDAP
- **Secrets Management**: Integrate with Vault, AWS Secrets Manager, GCP Secret Manager
- **Network Topology**: Track VPCs, subnets, peering, VPN connections
- **Project Sync**: Bi-directional sync with GitHub, GitLab, Jira, Trello, OpenProject
- **Enterprise Features**: Audit logging, RBAC, MFA, SSO, license management

## Screenshots

### Organization Network Map

<a href="docs/screenshots/elder-organization-map.png" target="_blank">
  <img src="docs/screenshots/elder-organization-map.png" alt="Organization Network Map" style="max-width: 100%; cursor: pointer;">
</a>

*Interactive network visualization showing organizational relationships with React Flow.*

### Dashboard & Core Features

<table>
<tr>
<td width="50%">
<a href="docs/screenshots/elder-organizationunits.png" target="_blank">
  <img src="docs/screenshots/elder-organizationunits.png" alt="Organizations" style="max-width: 100%;">
</a>
</td>
<td width="50%">
<a href="docs/screenshots/elder-entities.png" target="_blank">
  <img src="docs/screenshots/elder-entities.png" alt="Entities" style="max-width: 100%;">
</a>
</td>
</tr>
<tr>
<td width="50%">
<a href="docs/screenshots/Elder-IAM.png" target="_blank">
  <img src="docs/screenshots/Elder-IAM.png" alt="IAM Integration" style="max-width: 100%;">
</a>
</td>
<td width="50%">
<a href="docs/screenshots/Elder-Secrets.png" target="_blank">
  <img src="docs/screenshots/Elder-Secrets.png" alt="Secrets Management" style="max-width: 100%;">
</a>
</td>
</tr>
</table>

## Key Features

### Core Capabilities
- ✅ **Multi-Entity Support**: 8 entity categories with 30+ sub-types
- ✅ **Hierarchical Organizations**: Unlimited depth organizational structures
- ✅ **Dependency Graphs**: Visualize complex entity relationships
- ✅ **Full RBAC**: Role-based permissions with org-scoped access
- ✅ **Multi-Auth**: Local, SAML, OAuth2, and LDAP authentication
- ✅ **RESTful & gRPC APIs**: Complete API coverage
- ✅ **Audit Logging**: Comprehensive audit trail for compliance

### v2.0 Highlights
- **Unified Identity Center**: Single page for all identity types (Users, Groups, Service Accounts, API Keys)
- **Multi-backend Secrets**: HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, Infisical
- **Network Topology**: VPCs, Subnets, Firewalls, Load Balancers with connection mapping
- **Project Sync**: Bi-directional sync with GitHub, GitLab, Jira, Trello, OpenProject
- **Cloud Connectors**: AWS, GCP, Kubernetes, Google Workspace, LDAP

### License Tiers

| Tier | Features | Limits |
|------|----------|--------|
| **Community** | Basic tracking, local auth | Up to 100 entities |
| **Professional** | SAML/OAuth2, advanced visualization | Unlimited entities |
| **Enterprise** | All features + LDAP sync, audit logging, gRPC API, SSO | Unlimited |

## Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- PostgreSQL 15+ (or MySQL, SQLite via PyDAL)
- Redis 7+

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
docker-compose up -d

# Check health
curl http://localhost:4000/healthz
```

## Configuration

Key environment variables:

```bash
# Database (PyDAL supports PostgreSQL, MySQL, SQLite, Oracle, MSSQL)
DATABASE_URL=postgresql://elder:password@localhost:5432/elder

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# Authentication
SAML_ENABLED=true
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
- **Auth**: JWT, SAML, OAuth2, LDAP
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

## Support

- **Company Homepage**: [www.penguintech.io](https://www.penguintech.io)
- **Documentation**: [docs.penguintech.io/elder](https://docs.penguintech.io/elder)
- **Issues**: [GitHub Issues](https://github.com/penguintechinc/elder/issues)
- **Email**: support@penguintech.io

---

**Elder** - Know Your Infrastructure, Understand Your Dependencies

© 2025 Penguin Tech Inc. All rights reserved.
