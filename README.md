# Elder

[![CI/CD Pipeline](https://github.com/penguintechinc/elder/actions/workflows/build.yml/badge.svg)](https://github.com/penguintechinc/elder/actions)
[![Test Coverage](https://codecov.io/gh/penguintechinc/elder/branch/main/graph/badge.svg)](https://codecov.io/gh/penguintechinc/elder)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/penguintechinc/elder/releases)

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

- **Entity Tracking**: Datacenters, VPCs, Subnets, Compute Devices, Network Devices, Users, and Security Issues
- **Dependency Mapping**: Visualize "depends on" relationships between entities
- **Organizational Hierarchy**: Manage entities within Company → Department → Teams structure
- **LDAP/SAML Integration**: Sync organizational structure with directory services
- **Role-Based Access Control**: Granular permissions with super admin, org admin, editor, and viewer roles
- **Interactive Visualization**: Zoom, pan, and explore entity relationships with vis.js
- **Comprehensive APIs**: Both REST and gRPC for maximum flexibility
- **Enterprise Features**: Audit logging, MFA, SSO, and license management

## Screenshots

### Organization Network Map

![Organization Network Map](docs/screenshots/elder-organization-map.png)

*Interactive network visualization showing organizational relationships with React Flow. Nodes represent organizations and entities, while edges show parent-child and dependency relationships.*

### Dashboard & Core Features

<table>
<tr>
<td width="50%">

![Organizations](docs/screenshots/elder-organizationunits.png)
*Hierarchical organization management with types, metadata, and relationship tracking*

</td>
<td width="50%">

![Entities](docs/screenshots/elder-entities.png)
*Entity tracking for datacenters, compute, network devices, and more*

</td>
</tr>
<tr>
<td width="50%">

![Dependencies](docs/screenshots/elder-dependencies.png)
*Dependency mapping and relationship visualization between entities*

</td>
<td width="50%">

![Identities](docs/screenshots/elder-identities.png)
*User and group management with role-based access control*

</td>
</tr>
</table>

### Project Management Features

<table>
<tr>
<td width="33%">

![Projects](docs/screenshots/elder-projects.png)
*Project tracking and organization*

</td>
<td width="33%">

![Milestones](docs/screenshots/elder-milestones.png)
*Milestone management for project planning*

</td>
<td width="33%">

![Labels](docs/screenshots/elder-labels.png)
*Customizable labels for categorization*

</td>
</tr>
</table>

## Features

### Core Capabilities

- ✅ **Multi-Entity Support**: Track 7 entity types with custom metadata
- ✅ **Hierarchical Organizations**: Unlimited depth organizational structures
- ✅ **Dependency Graphs**: Visualize complex entity relationships
- ✅ **Full RBAC**: Role-based permissions with org-scoped access
- ✅ **Multi-Auth**: Local, SAML, OAuth2, and LDAP authentication
- ✅ **RESTful API**: Complete OpenAPI 3.0 documented REST API
- ✅ **gRPC API**: High-performance gRPC for machine-to-machine communication
- ✅ **Audit Logging**: Comprehensive audit trail for compliance
- ✅ **Real-time Updates**: WebSocket support for live graph updates
- ✅ **Import/Export**: JSON, YAML, and CSV data exchange

### Entity Types

| Type | Description | Examples |
|------|-------------|----------|
| **Datacenter/VPC** | Physical or virtual datacenter infrastructure | AWS VPC, Azure VNet, On-prem DC |
| **Subnet** | Network subnets and segments | 10.0.1.0/24, DMZ, Private Subnet |
| **Compute** | Servers, VMs, and compute resources | EC2 instances, bare metal servers, containers |
| **Network** | Network devices and services | Load balancers, VPNs, firewalls, proxies |
| **User** | Human and service accounts | Employees, service accounts, API keys |
| **Security Issue** | Vulnerabilities and security concerns | CVEs, misconfigurations, compliance gaps |

### License Tiers

Elder integrates with the [PenguinTech License Server](https://license.penguintech.io) for feature gating:

| Tier | Features | Limits |
|------|----------|--------|
| **Community** | Basic tracking, local auth | Up to 100 entities |
| **Professional** | SAML/OAuth2, advanced visualization | Unlimited entities |
| **Enterprise** | All features + LDAP sync, audit logging, gRPC API, SSO | Unlimited |

## Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- PostgreSQL 15+ (via Docker)
- Redis 7+ (via Docker)

### Installation

```bash
# Clone the repository
git clone https://github.com/penguintechinc/elder.git
cd elder

# Run setup (installs dependencies and creates .env)
make setup

# Edit .env with your configuration
nano .env

# Start development environment
make dev

# In another terminal, run database migrations
make db-migrate

# Start the API
make dev-api
```

The Elder API will be available at `http://localhost:5000`

### Docker Deployment

```bash
# Start all services with docker-compose
make dev-all

# Check service health
make health

# View logs
make dev-logs
```

Access the services:
- **Elder API**: http://localhost:5000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## Configuration

Elder is configured via environment variables. Key settings:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://elder:password@localhost:5432/elder

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# Authentication
SAML_ENABLED=true
SAML_METADATA_URL=https://your-idp.com/metadata
OAUTH2_ENABLED=true
OAUTH2_CLIENT_ID=your-client-id
LDAP_ENABLED=true
LDAP_HOST=ldap.example.com

# License (optional)
LICENSE_KEY=PENG-XXXX-XXXX-XXXX-XXXX-XXXX

# Admin User (created on first run if set)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
ADMIN_EMAIL=admin@example.com
```

See `.env` for full configuration options.

## API Documentation

### REST API

Elder provides a comprehensive REST API following OpenAPI 3.0 specification:

```bash
# Organizations
GET    /api/v1/organizations
POST   /api/v1/organizations
GET    /api/v1/organizations/{id}
PATCH  /api/v1/organizations/{id}
DELETE /api/v1/organizations/{id}

# Entities
GET    /api/v1/entities
POST   /api/v1/entities
GET    /api/v1/entities/{id}
PATCH  /api/v1/entities/{id}
DELETE /api/v1/entities/{id}

# Dependencies
GET    /api/v1/dependencies
POST   /api/v1/dependencies
DELETE /api/v1/dependencies/{id}

# Graph Visualization
GET    /api/v1/graph
GET    /api/v1/graph?organization_id={id}
GET    /api/v1/graph?entity_id={id}&depth=2

# Authentication
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/saml/login
GET    /api/v1/auth/oauth2/authorize

# Monitoring
GET    /healthz
GET    /metrics
```

Full API documentation available at `/api/docs` (Swagger UI).

### gRPC API

Elder also provides a gRPC API for high-performance integrations:

```protobuf
service ElderService {
  rpc ListEntities(ListEntitiesRequest) returns (ListEntitiesResponse);
  rpc GetEntity(GetEntityRequest) returns (Entity);
  rpc CreateEntity(CreateEntityRequest) returns (Entity);
  rpc UpdateEntity(UpdateEntityRequest) returns (Entity);
  rpc DeleteEntity(DeleteEntityRequest) returns (Empty);
  rpc GetDependencyGraph(GetDependencyGraphRequest) returns (DependencyGraph);
}
```

gRPC server runs on port `50051` by default.

## Development

### Common Commands

```bash
# Development
make dev                # Start postgres and redis
make dev-api            # Start Flask API locally
make dev-all            # Start all services
make dev-logs           # View logs
make dev-stop           # Stop all services

# Testing
make test               # Run all tests
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-coverage      # Generate coverage report
make lint               # Run linters
make format             # Format code

# Database
make db-migrate         # Run migrations
make db-create-migration # Create new migration
make db-reset           # Reset database (WARNING: destroys data)
make db-shell           # Open PostgreSQL shell
make db-backup          # Create backup

# Docker
make docker-build       # Build Docker image
make docker-scan        # Scan for vulnerabilities

# Version
make version            # Show current version
make version-bump-patch # Bump patch version
make version-bump-minor # Bump minor version
make version-bump-major # Bump major version
```

### Testing

Elder has comprehensive test coverage:

```bash
# Run all tests with coverage
make test

# Run specific test types
make test-unit
make test-integration

# Generate HTML coverage report
make test-coverage
# Open htmlcov/index.html
```

### Code Quality

Elder follows strict code quality standards:

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint
```

## Architecture

Elder is built on a modern, scalable architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  Web UI (vis.js) │ REST Clients │ gRPC Clients          │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   API Layer                             │
│  Flask REST API │ gRPC Server │ WebSocket               │
│  Authentication │ Authorization (RBAC) │ Rate Limiting  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                 Business Logic Layer                    │
│  Entity Management │ Dependency Tracking                │
│  Organization Hierarchy │ Audit Logging                 │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                            │
│  PostgreSQL (Entities, Orgs, Users, RBAC, Audit)       │
│  Redis (Cache, Sessions, Real-time)                     │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: Flask (Python 3.13), SQLAlchemy, Alembic
- **Database**: PostgreSQL 15+ with connection pooling
- **Cache**: Redis 7+ for sessions and caching
- **APIs**: REST (OpenAPI 3.0), gRPC (protobuf)
- **Auth**: SAML (python3-saml), OAuth2 (Authlib), LDAP
- **Frontend**: HTML5, JavaScript, vis.js Network
- **Monitoring**: Prometheus, Grafana
- **Container**: Docker, docker-compose
- **Orchestration**: Kubernetes with Helm charts

## Security

Elder implements security best practices:

- ✅ **Authentication**: Multi-factor authentication support
- ✅ **Authorization**: Fine-grained RBAC with org-scoped permissions
- ✅ **TLS**: Enforce TLS 1.3 for all connections
- ✅ **Input Validation**: Comprehensive validation with marshmallow
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- ✅ **XSS Prevention**: Jinja2 auto-escaping
- ✅ **CSRF Protection**: Flask-WTF CSRF tokens
- ✅ **Rate Limiting**: Request rate limiting to prevent abuse
- ✅ **Audit Logging**: Comprehensive audit trail
- ✅ **Secrets Management**: Environment variables, never in code
- ✅ **Container Scanning**: Trivy vulnerability scanning

## Deployment

### Production Deployment

```bash
# Build production Docker image
make docker-build

# Scan for vulnerabilities
make docker-scan

# Build multi-architecture images
make docker-build-multiarch

# Push to registry
make docker-push
```

### Kubernetes Deployment

Kubernetes manifests and Helm charts are available in `infrastructure/k8s/`:

```bash
# Deploy with kubectl
kubectl apply -f infrastructure/k8s/

# Or deploy with Helm
helm install elder infrastructure/helm/elder
```

## Monitoring

Elder includes built-in monitoring and observability:

- **Metrics**: Prometheus metrics at `/metrics`
- **Health Checks**: `/healthz` endpoint
- **Structured Logging**: JSON-formatted logs
- **Grafana Dashboards**: Pre-configured dashboards
- **Distributed Tracing**: OpenTelemetry support

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Elder is licensed under the Limited AGPL v3 with Fair Use Preamble. See [LICENSE.md](LICENSE.md) for details.

## Support

- **Company Homepage**: [www.penguintech.io](https://www.penguintech.io)
- **Documentation**: [docs.penguintech.io/elder](https://docs.penguintech.io/elder)
- **Issues**: [GitHub Issues](https://github.com/penguintechinc/elder/issues)
- **Email**: support@penguintech.io
- **License Server**: [license.penguintech.io](https://license.penguintech.io)

## Project Status

**Current Version:** 1.0.0 - Production Ready 🎉

Elder v1.0.0 represents the first production-ready release with comprehensive UI/UX improvements, enhanced issue management, and complete branding integration.

**Completed Phases:**
- ✅ Phase 1: Foundation & Core Models
- ✅ Phase 2: REST API (79 endpoints)
- ✅ Phase 3: Authentication & Authorization (JWT, SAML, OAuth2, RBAC)
- ✅ Phase 4: Modern React UI (TypeScript, React Query, ReactFlow)
- ✅ Phase 5: gRPC API (45 RPC methods, Envoy proxy)
- ✅ Phase 6: Enterprise Features (Issues, Projects, Milestones, Labels, Resource Roles, Metadata)
- ✅ Phase 8: Infrastructure & DevOps (CI/CD, Kubernetes, Helm)
- ✅ Phase 9: Websites & Documentation
- ✅ Phase 10: Testing & Polish
- ✅ v1.0.0: Production UI/UX, Enhanced Issue Management, Branding Integration

**Recent v1.0.0 Highlights:**
- Enhanced issue creation with organization/entity assignment and labels
- Modal-first UI pattern for improved workflow efficiency
- Clickable dashboard navigation and anchor link scrolling
- Organization type management (Department, Team, Collection, etc.)
- Complete Elder branding integration
- Network graph visualization with ReactFlow
- Comprehensive project management features

**Optional Future Enhancements:**
- Phase 6a: Advanced Features (LDAP sync, WebSocket updates, bulk operations)
- Phase 7: License Integration Refinement

See [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md) for detailed release history.

## Acknowledgments

Elder is developed and maintained by [Penguin Tech Inc](https://www.penguintech.io).

---

**Elder** - Know Your Infrastructure, Understand Your Dependencies

© 2024 Penguin Tech Inc. All rights reserved.
