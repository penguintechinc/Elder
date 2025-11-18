# Elder

[![Continuous Integration](https://github.com/penguintechinc/elder/actions/workflows/ci.yml/badge.svg)](https://github.com/penguintechinc/elder/actions/workflows/ci.yml)
[![Docker Build](https://github.com/penguintechinc/elder/actions/workflows/docker-build.yml/badge.svg)](https://github.com/penguintechinc/elder/actions/workflows/docker-build.yml)
[![Test Coverage](https://codecov.io/gh/penguintechinc/elder/branch/main/graph/badge.svg)](https://codecov.io/gh/penguintechinc/elder)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/penguintechinc/elder/releases)

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

<a href="docs/screenshots/elder-organization-map.png" target="_blank">
  <img src="docs/screenshots/elder-organization-map.png" alt="Organization Network Map" style="max-width: 100%; cursor: pointer;">
</a>

*Interactive network visualization showing organizational relationships with React Flow. Nodes represent organizations and entities, while edges show parent-child and dependency relationships. **Click to view full size.***

### Dashboard & Core Features

<table>
<tr>
<td width="50%">

<a href="docs/screenshots/elder-organizationunits.png" target="_blank">
  <img src="docs/screenshots/elder-organizationunits.png" alt="Organizations" style="max-width: 100%; cursor: pointer;">
</a>

*Hierarchical organization management with types, metadata, and relationship tracking. **Click to enlarge.***

</td>
<td width="50%">

<a href="docs/screenshots/elder-entities.png" target="_blank">
  <img src="docs/screenshots/elder-entities.png" alt="Entities" style="max-width: 100%; cursor: pointer;">
</a>

*Entity tracking for datacenters, compute, network devices, and more. **Click to enlarge.***

</td>
</tr>
<tr>
<td width="50%">

<a href="docs/screenshots/elder-dependencies.png" target="_blank">
  <img src="docs/screenshots/elder-dependencies.png" alt="Dependencies" style="max-width: 100%; cursor: pointer;">
</a>

*Dependency mapping and relationship visualization between entities. **Click to enlarge.***

</td>
<td width="50%">

<a href="docs/screenshots/elder-identities.png" target="_blank">
  <img src="docs/screenshots/elder-identities.png" alt="Identities" style="max-width: 100%; cursor: pointer;">
</a>

*User and group management with role-based access control. **Click to enlarge.***

</td>
</tr>
</table>

### Project Management Features

<table>
<tr>
<td width="33%">

<a href="docs/screenshots/elder-projects.png" target="_blank">
  <img src="docs/screenshots/elder-projects.png" alt="Projects" style="max-width: 100%; cursor: pointer;">
</a>

*Project tracking and organization. **Click to enlarge.***

</td>
<td width="33%">

<a href="docs/screenshots/elder-milestones.png" target="_blank">
  <img src="docs/screenshots/elder-milestones.png" alt="Milestones" style="max-width: 100%; cursor: pointer;">
</a>

*Milestone management for project planning. **Click to enlarge.***

</td>
<td width="33%">

<a href="docs/screenshots/elder-labels.png" target="_blank">
  <img src="docs/screenshots/elder-labels.png" alt="Labels" style="max-width: 100%; cursor: pointer;">
</a>

*Customizable labels for categorization. **Click to enlarge.***

</td>
</tr>
</table>

### Enterprise & Integration Features

<table>
<tr>
<td width="50%">

<a href="docs/screenshots/Elder-IAM.png" target="_blank">
  <img src="docs/screenshots/Elder-IAM.png" alt="IAM Integration" style="max-width: 100%; cursor: pointer;">
</a>

*AWS IAM integration for identity and access management. **Click to enlarge.***

</td>
<td width="50%">

<a href="docs/screenshots/Elder-Secrets.png" target="_blank">
  <img src="docs/screenshots/Elder-Secrets.png" alt="Secrets Management" style="max-width: 100%; cursor: pointer;">
</a>

*Secrets management with AWS Secrets Manager integration. **Click to enlarge.***

</td>
</tr>
<tr>
<td width="50%">

<a href="docs/screenshots/Elder-GoogleWorkspaces.png" target="_blank">
  <img src="docs/screenshots/Elder-GoogleWorkspaces.png" alt="Google Workspace" style="max-width: 100%; cursor: pointer;">
</a>

*Google Workspace integration for user and group synchronization. **Click to enlarge.***

</td>
<td width="50%">

<a href="docs/screenshots/Elder-AlertWebhooks.png" target="_blank">
  <img src="docs/screenshots/Elder-AlertWebhooks.png" alt="Webhooks" style="max-width: 100%; cursor: pointer;">
</a>

*Webhook integration for real-time event notifications. **Click to enlarge.***

</td>
</tr>
<tr>
<td width="50%">

<a href="docs/screenshots/Elder-Discovery.png" target="_blank">
  <img src="docs/screenshots/Elder-Discovery.png" alt="Discovery" style="max-width: 100%; cursor: pointer;">
</a>

*Automated infrastructure discovery and entity creation. **Click to enlarge.***

</td>
<td width="50%">

<a href="docs/screenshots/Elder-Updated-Org.png" target="_blank">
  <img src="docs/screenshots/Elder-Updated-Org.png" alt="Organization Detail" style="max-width: 100%; cursor: pointer;">
</a>

*Enhanced organization detail view with comprehensive metadata. **Click to enlarge.***

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

### Entity Types & Sub-Types (New in v1.2.0!)

Elder now supports **categorized entity types with sub-types** for more granular infrastructure tracking:

| Category | Sub-Types | Examples |
|----------|-----------|----------|
| **Network** | Router, Switch, Firewall, Load Balancer, VPN Gateway, DNS Server, Proxy | Cisco Router, F5 Load Balancer, pfSense Firewall |
| **Compute** | Physical Server, Virtual Machine, Container, Kubernetes Pod | EC2 instance, Docker container, bare metal server |
| **Storage** | SAN, NAS, Object Storage, Block Storage, File Share | AWS S3, NetApp NAS, iSCSI SAN |
| **Datacenter** | Physical Datacenter, Cloud Region, Availability Zone, VPC, On-Premises | us-east-1, Azure East US, Corporate HQ |
| **Security** | Firewall, IDS/IPS, WAF, Antivirus, DLP, SIEM | Palo Alto FW, Snort IDS, Cloudflare WAF |
| **Application** | Web Server, App Server, Database, Message Queue, Cache | Nginx, Tomcat, PostgreSQL, Redis, RabbitMQ |
| **Service** | API Gateway, CDN, Email Service, Monitoring, Backup | CloudFront CDN, SendGrid, Prometheus, Veeam |
| **Identity** | User, Service Account, Group, Role | Employee account, Jenkins SA, Security admins |

**Default Metadata Support**: Each entity type can have pre-configured metadata fields that appear automatically during entity creation.

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
- Database: PostgreSQL 15+ (recommended, via Docker), or MySQL, SQLite, Oracle, MSSQL, etc.
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

The Elder API will be available at `http://localhost:4000` and the Web UI at `http://localhost:3005`

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
- **Elder Web UI**: http://localhost:3005
- **Elder API**: http://localhost:4000
- **Prometheus**: http://localhost:9091
- **Grafana**: http://localhost:4001 (admin/admin)

## Configuration

Elder is configured via environment variables. Key settings:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database (PyDAL supports PostgreSQL, MySQL, SQLite, Oracle, MSSQL, and more)
DATABASE_URL=postgresql://elder:password@localhost:5432/elder
# Alternative examples:
# DATABASE_URL=mysql://user:password@localhost:3306/elder
# DATABASE_URL=sqlite://storage.db

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

## Database Support

Elder uses **PyDAL** (Python Database Abstraction Layer) for maximum database flexibility. This allows you to choose the database backend that best fits your needs without changing any application code.

### Supported Databases

- ✅ **PostgreSQL** (Recommended for production)
- ✅ **MySQL** / MariaDB
- ✅ **SQLite** (Perfect for development and small deployments)
- ✅ **Oracle**
- ✅ **Microsoft SQL Server**
- ✅ **Firebird**
- ✅ **DB2**
- ✅ **Informix**
- ✅ **Ingres**
- ✅ And many more via PyDAL adapters

### Database Configuration Examples

```bash
# PostgreSQL (Recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/elder

# MySQL
DATABASE_URL=mysql://user:password@localhost:3306/elder

# SQLite (Great for development)
DATABASE_URL=sqlite://storage.db

# Microsoft SQL Server
DATABASE_URL=mssql://user:password@localhost:1433/elder

# Oracle
DATABASE_URL=oracle://user:password@localhost:1521/elder
```

### Why PyDAL?

- **Database Agnostic**: Write once, run on any supported database
- **Automatic Migrations**: Schema changes are handled automatically
- **Security**: Built-in protection against SQL injection
- **Performance**: Connection pooling and query optimization
- **Simplicity**: Clean, Pythonic API for database operations
- **Validators**: Comprehensive input validation at the database layer

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

# Entity Types (New in v1.2.0)
GET    /api/v1/entity-types/
GET    /api/v1/entity-types/{type}
GET    /api/v1/entity-types/{type}/subtypes
GET    /api/v1/entity-types/{type}/metadata
GET    /api/v1/entity-types/{type}/{sub_type}/metadata

# Issue Types (New in v1.2.0)
GET    /api/v1/issue-types
POST   /api/v1/issue-types
GET    /api/v1/issue-types/{id}
PATCH  /api/v1/issue-types/{id}
DELETE /api/v1/issue-types/{id}

# Webhooks (New in v1.2.0)
GET    /api/v1/webhooks
POST   /api/v1/webhooks
GET    /api/v1/webhooks/{id}
PATCH  /api/v1/webhooks/{id}
DELETE /api/v1/webhooks/{id}
GET    /api/v1/webhooks/{id}/deliveries

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
│  Database via PyDAL (PostgreSQL, MySQL, SQLite, etc.)  │
│  Redis (Cache, Sessions, Real-time)                     │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: Flask (Python 3.13), PyDAL (Database Abstraction Layer)
- **Database**: Multi-database support via PyDAL
  - **Supported**: PostgreSQL, MySQL, SQLite, Oracle, MSSQL, Firebird, DB2, Informix, Ingres, and more
  - **Recommended**: PostgreSQL 15+ with connection pooling
  - **Development**: SQLite for quick local development
- **Cache**: Redis 7+ or Valkey for sessions and caching
- **APIs**: REST (OpenAPI 3.0), gRPC (protobuf)
- **Auth**: SAML (python3-saml), OAuth2 (Authlib), LDAP
- **Frontend**: Modern React UI (TypeScript, Vite, ReactFlow, React Query, Tailwind CSS)
- **Monitoring**: Prometheus, Grafana
- **Container**: Docker, docker-compose
- **Orchestration**: Kubernetes with Helm charts

## Security

Elder implements security best practices:

- ✅ **Authentication**: Multi-factor authentication support
- ✅ **Authorization**: Fine-grained RBAC with org-scoped permissions
- ✅ **TLS**: Enforce TLS 1.3 for all connections
- ✅ **Input Validation**: Comprehensive validation with PyDAL validators and marshmallow
- ✅ **SQL Injection Prevention**: PyDAL ORM with parameterized queries and automatic escaping
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

**Current Version:** 1.2.0 - Enhanced Entity Management 🚀

Elder v1.2.0 introduces comprehensive entity type categorization with sub-types, issue type management, webhook integration, and project-based views for improved infrastructure tracking and workflow automation.

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
- ✅ v1.2.0: Entity Type Categories, Issue Types, Webhook Integration, Project Views

**New in v1.2.0:**
- **Entity Type Categories with Sub-Types**: 8 main categories (Network, Compute, Storage, Datacenter, Security, Application, Service, Identity) with 30+ sub-types
- **Default Metadata Templates**: Pre-configured metadata fields for each entity type that appear automatically during creation
- **Issue Type Management**: Customizable issue types (Bug, Feature Request, Task, Documentation, etc.) with descriptions
- **Webhook Integration**: HTTP webhook support for real-time event notifications on entity changes, issue updates, and more
- **Project-Based Views**: Filter and view issues within the context of specific projects
- **Enhanced Entity Creation**: Category-based entity creation with dynamic sub-type selection and metadata fields
- **REST API Enhancements**: New endpoints for entity types, issue types, and webhook management

**v1.0.0 Highlights:**
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
- Advanced webhook retry logic and delivery tracking
- Custom entity type definitions

See [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md) for detailed release history.

## Acknowledgments

Elder is developed and maintained by [Penguin Tech Inc](https://www.penguintech.io).

---

**Elder** - Know Your Infrastructure, Understand Your Dependencies

© 2024 Penguin Tech Inc. All rights reserved.
