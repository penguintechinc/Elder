# Elder Release Notes

All notable changes to the Elder project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.1] - 2025-10-29

### 🚀 Cloud Infrastructure Expansion Release

Major expansion of Elder's cloud infrastructure discovery capabilities with support for additional AWS services, Kubernetes/container orchestration, and comprehensive status tracking for operational visibility.

### ✨ New Features

#### Database Schema Enhancements
- **Status Metadata Tracking**: Added `status_metadata` JSON field to entities table
  - Captures operational status (Running, Stopped, Deleted, Creating, Error)
  - Includes epoch64 timestamp for status updates
  - Enables real-time operational monitoring and historical tracking
- **Namespace Sub-Entity Type**: Added `namespace` as network entity sub-type for Kubernetes support
  - Metadata template includes cluster, resource_quota, labels, annotations

#### AWS Connector Extensions
- **RDS/Aurora Database Discovery**:
  - Automatic Aurora detection (engine starts with "aurora")
  - Comprehensive database metadata (engine, version, instance class, storage)
  - Multi-AZ and encryption status tracking
  - Database endpoints and VPC associations
  - Status tracking: Available, Creating, Deleting, Failed, etc.
- **ElastiCache Cluster Discovery**:
  - Redis and Memcached cluster support
  - Node type, count, and endpoint information
  - Availability zone and VPC integration
  - Status tracking for cache lifecycle management
- **SQS Queue Discovery**:
  - Standard and FIFO queue detection
  - Queue configuration (retention, visibility timeout, delays)
  - Approximate message count monitoring
  - Queue ARN and URL tracking
- **Enhanced Status Tracking**: All AWS resources (EC2, VPCs, RDS, ElastiCache, SQS) now use status_metadata field

#### Kubernetes Connector (NEW)
- **Multi-Cluster Support**: Automatic cluster detection (in-cluster or kubeconfig)
- **Namespace Discovery**:
  - Resource quota tracking (CPU, memory, pods)
  - Labels, annotations, and UID tracking
  - Active/Terminating status monitoring
- **Secret Discovery** (Security-Focused):
  - Metadata-only approach - NEVER exposes secret values
  - Tracks secret names, types, and key counts
  - Security entity type classification
  - Helps identify secret sprawl without compromising security
- **Pod/Container Discovery**:
  - Running container inventory
  - Container images and port mappings
  - Node assignment and IP addresses
  - Pod lifecycle tracking (Running, Pending, Failed, etc.)
- **Persistent Volume Claim Discovery**:
  - Storage provisioning monitoring
  - Capacity vs requested storage tracking
  - Access modes and storage classes
  - Bound/Pending status tracking
- **Compatible with All K8S Distributions**: EKS, GKE, AKS, OpenShift, Rancher, K3s, Vanilla K8S

#### Backup System Enhancements
- **Per-Job S3 Configuration**:
  - Configure different S3 buckets per backup job
  - Job-specific S3 credentials and endpoints
  - Support for MinIO, Wasabi, Backblaze B2, DigitalOcean Spaces
  - Fallback to global S3 configuration
- **Web UI S3 Configuration**:
  - Expandable S3 configuration section in backup job creation
  - 6 input fields: endpoint, bucket, region, access key, secret key, prefix
  - Toggle checkbox to enable/disable S3 per job
  - Inline validation and helper text

### 🔧 Technical Improvements

#### Data Models
- **Entity Model Updates** (pydal_models.py):
  - Added `status_metadata` JSON field for operational status tracking
  - Field automatically migrated to existing entities (nullable)
- **Entity Types** (entity_types.py):
  - Added `NAMESPACE` constant to NetworkSubType
  - Created namespace metadata template with K8S-specific fields
  - Updated ENTITY_SUBTYPES mapping
- **Connector Client** (elder_client.py):
  - Extended Entity dataclass with `sub_type` and `status_metadata` fields
  - Support for v1.2.1 entity classification system

#### AWS Connector Architecture
- **Three New Sync Methods**:
  - `_sync_rds_instances()` - RDS and Aurora databases
  - `_sync_elasticache_clusters()` - Redis/Memcached caches
  - `_sync_sqs_queues()` - Message queues
- **Status Integration**: All sync methods capture real-time status with timestamps
- **Proper Entity Classification**:
  - RDS → storage/database
  - ElastiCache → storage/caching
  - SQS → storage/queue_system

#### Kubernetes Connector Architecture
- **Four Resource Sync Methods**:
  - `_sync_namespaces()` - Network namespace entities
  - `_sync_secrets()` - Security/config entities (metadata only)
  - `_sync_pods()` - Compute/kubernetes_node entities
  - `_sync_pvcs()` - Storage/virtual_disk entities
- **Security Best Practices**: Secret discovery NEVER exposes values
- **Cluster-Level Organization**: Hierarchical organization structure per cluster

#### Backup Service Architecture
- **Per-Job S3 Override Pattern**:
  - Temporary configuration override during backup execution
  - Job-specific S3 settings with fallback to global
  - Original configuration restoration after upload
- **Database Schema**: 7 new S3 fields in backup_jobs table
- **API Integration**: Extended create_backup_job endpoint with S3 parameters

### 📊 API Enhancements

- **Backup API**:
  - Enhanced `POST /api/v1/backup/jobs` to accept 7 S3 configuration parameters
  - Per-job S3 override support
- **Entity Types API**: Namespace now available as valid network sub-type

### 🎯 Integration Benefits

#### Operational Visibility
- **Real-Time Status Monitoring**: Track resource states during discovery syncs
- **Historical Tracking**: Timestamp-based status history
- **Lifecycle Management**: Identify stuck, failed, or transitioning resources

#### Comprehensive Cloud Coverage
Elder now discovers and tracks:
- **AWS**: EC2, VPCs, S3, RDS, Aurora, ElastiCache, SQS
- **Kubernetes**: Namespaces, Secrets, Pods, Containers, PVCs
- **All major K8S distributions**: EKS, GKE, AKS, OpenShift, Rancher

#### Enhanced Classification
- **Entity Sub-Types**: Proper classification (database, caching, queue_system, namespace, kubernetes_node)
- **Entity Types**: Correct categorization (storage, network, compute, security)
- **Status Metadata**: Uniform status tracking across all cloud resources

#### Flexible Backup Strategy
- **Multi-Destination Backups**: Different backup jobs → different S3 buckets
- **Provider Flexibility**: Mix AWS S3, MinIO, Wasabi, Backblaze B2 per job
- **Global + Local Configuration**: Per-job overrides with global defaults

### 📝 Files Modified

**Models & Schema**:
- `apps/api/models/pydal_models.py` - Added status_metadata field to entities
- `apps/api/models/entity_types.py` - Added namespace sub-type and metadata

**Connectors**:
- `apps/connector/connectors/aws_connector.py` - Added RDS, ElastiCache, SQS sync methods
- `apps/connector/connectors/k8s_connector.py` - NEW: Complete Kubernetes connector (518 lines)
- `apps/connector/utils/elder_client.py` - Extended Entity dataclass

**Backup System**:
- `apps/api/api/v1/backup.py` - Enhanced create_backup_job endpoint
- `apps/api/services/backup/service.py` - Per-job S3 configuration support
- `web/src/pages/Backups.tsx` - S3 configuration UI

**Documentation**:
- `docs/README.md` - Added Backup & Data Management section
- `docs/RELEASE_NOTES.md` - This file

### 🔍 Breaking Changes

None. All changes are backward compatible:
- Existing entities work without status_metadata (nullable field)
- Global S3 configuration still works for backup jobs
- Existing AWS connector resources continue to sync normally

### 📦 Dependencies

**New Requirements**:
- `kubernetes` - Python Kubernetes client library (for K8S connector)

**Existing Dependencies** (already present):
- `boto3` - AWS SDK (extended usage for RDS, ElastiCache, SQS)
- `botocore` - AWS core library

### 🎓 Migration Notes

#### Database Migration
PyDAL automatically migrates the schema (migrate=True):
- `status_metadata` field added to entities table
- No manual migration required
- Existing entities remain unchanged (null status_metadata)

#### Backup Jobs
Existing backup jobs without S3 configuration:
- Continue using global S3 settings (if configured)
- Can be updated to use per-job S3 settings via API or UI

#### Kubernetes Integration
To enable K8S discovery:
1. Install kubernetes library: `pip install kubernetes`
2. Configure kubeconfig or run connector in-cluster
3. Set appropriate RBAC permissions for resource discovery
4. Run connector with K8S support enabled

### 🔐 Security Notes

#### Kubernetes Secrets
- Secret values are NEVER retrieved from K8S API
- Only metadata and key names are stored
- Provides inventory visibility without compromising security
- Helps identify secret sprawl and unused secrets

#### S3 Credentials
- Per-job S3 credentials stored in database
- Consider using Secret Manager integration (future enhancement)
- Credentials encrypted at rest (database-level encryption recommended)

---

## [1.0.0] - 2025-10-25

### 🎉 Production Release - v1.0.0

First production-ready release of Elder with comprehensive UI/UX improvements, enhanced issue management, and complete branding integration.

### ✨ New Features

#### Enhanced Issue Creation
- **Organization/Entity Assignment**: Issues can now be assigned to either an organization OR entities (mutually exclusive)
- **Radio button toggle** for choosing between Organization and Entity assignment modes
- **Multi-select entity assignment**: Ability to assign issues to multiple entities simultaneously
- **Label selection during creation**: Apply multiple labels when creating an issue via checkbox list
- **Visual label indicators**: Colored dots showing label colors in selection interface
- **Scrollable selection lists**: Clean UI with max-height containers for large entity/label lists

#### UI/UX Improvements
- **Organization Type Management**:
  - Edit organization type (Department, Organization, Team, Collection, Other) via modal
  - Type field displayed in organization detail information card
  - Type selection dropdown in create/edit organization modals
- **Clickable Dashboard Items**:
  - Recent Organizations list items now navigate to organization detail pages
  - Recent Entities list items now navigate to entity detail pages
  - Hover effects and visual feedback on all clickable items
- **Anchor Link Navigation**:
  - Overview bubbles now scroll to corresponding sections
  - Smooth scroll behavior for better UX
  - Section IDs for Issues, Projects, Identities, and Hierarchy
  - Quick navigation from statistics to detailed views

#### Branding & Visual Identity
- **Elder Logo Integration**:
  - Elder-Logo.png used as sidebar logo (48px height)
  - Elder-Logo.png used as browser favicon
  - Professional branding throughout the application
  - Consistent visual identity across all pages

#### Modal-First UI Pattern
- **Edit Organization Modal**: Inline editing without navigation disruption
- Follows CLAUDE.md modal-first approach for secondary actions
- Keeps users focused on main organizational views
- Improved workflow efficiency

### 🐛 Bug Fixes

- **Async Decorator Support**: Fixed metadata endpoint 500 errors by making `@resource_role_required` and `@org_permission_required` decorators async-aware
- **Network Graph Edge Rendering**: Added `Handle` components to ReactFlow custom nodes to fix missing edge visualization
- **Edge Direction**: Implemented proper top-to-bottom hierarchical flow for organizational charts
- **Tree Depth Calculation**: Recursive algorithm for accurate multi-level organization hierarchies
- **Entity Positioning**: Entities now correctly placed one level below their containing organization

### 🔧 Technical Improvements

#### Frontend (React/TypeScript)
- Added `organization_type` field to Organization interface
- Created `OrganizationType` type definition
- Enhanced CreateIssueModal with assignment type selection
- Implemented entity and label multiselect components
- Added smooth scroll functionality for section navigation
- React Query integration for entities and labels fetching

#### Backend (Flask/Python)
- Async/await support in authentication decorators
- Proper coroutine handling with `inspect.iscoroutinefunction()`
- Support for `entity_ids` and `label_ids` in issue creation API

#### Network Graph
- Custom ReactFlow nodes with proper Handle components
- Top-to-bottom layout with configurable spacing
- Tree depth calculation for hierarchical positioning
- Colored edges based on relationship types
- Animated edges with arrow markers

### 📊 API Enhancements

- **Issues API**: Enhanced createIssue endpoint to support:
  - `entity_ids` array for multi-entity assignment
  - `label_ids` array for label application
  - Mutually exclusive `organization_id` or `entity_ids`
- **Organizations API**: Support for `organization_type` field in create/update operations

### 🎨 UI Components

- **EditOrganizationModal**: Full organization editing with type selection
- **CreateIssueModal**: Comprehensive issue creation with assignment and label options
- **Radio Button Groups**: Clean assignment type selection
- **Checkbox Lists**: Multi-select for entities and labels
- **Scrollable Containers**: Better handling of long lists
- **Visual Indicators**: Label color dots and hover effects

### 📦 Container Updates

- Web container rebuilt with all UI/UX improvements
- Elder logo properly integrated into build pipeline
- Multi-stage builds optimized for production
- Nginx serving static assets efficiently

### 🔄 Upgrade Notes from v0.1.0

1. **Database**: No schema changes required
2. **API**: Backward compatible - new optional fields in issue creation
3. **Frontend**: Complete rebuild - clear browser cache after update
4. **Assets**: New logo file added to public directory

### 🙏 Acknowledgments

This release represents a significant UI/UX milestone, transforming Elder from a functional system into a polished, production-ready enterprise application.

**Development Timeline**: October 23-25, 2025
**Major Focus**: User experience, visual polish, and workflow optimization

---

## [0.1.0] - 2024-10-23

### 🎉 Initial Release

First production-ready release of Elder - Entity, Element, and Relationship Tracking System.

### ✨ Features Added

#### Core Infrastructure (Phase 1)
- Database models for Organizations, Entities, Dependencies, Identities, and RBAC
- SQLAlchemy ORM with Alembic migrations
- PostgreSQL 15+ and Redis 7+ integration
- Unique 64-bit ID generation for all entities
- Hierarchical organization structures with unlimited nesting
- Six entity types: Datacenters/VPCs, Subnets, Compute, Network, Users, Security Issues
- Metadata support (JSONB) for all entities and organizations

#### REST API (Phase 2)
- 79 RESTful API endpoints with OpenAPI 3.0 documentation
- Organizations API (9 endpoints): Full CRUD + hierarchy operations
- Entities API (8 endpoints): Full CRUD + dependency tracking
- Dependencies API (9 endpoints): Full CRUD + bulk operations
- Graph API (3 endpoints): Visualization with filters
- Authentication API (7 endpoints): Login, logout, refresh, token management
- Identities API (13 endpoints): User and group management
- Lookup API (2 endpoints): Unique ID lookups
- Pagination, filtering, and field selection support
- Request validation with marshmallow schemas
- Rate limiting with Flask-Limiter

#### Authentication & Authorization (Phase 3)
- JWT token-based authentication (access + refresh tokens)
- SAML 2.0 SSO integration (python3-saml)
- OAuth2 provider integration (Authlib)
- Local authentication with password hashing
- Multi-factor authentication support
- Role-Based Access Control (RBAC) with 4 global roles
- Organization-scoped permissions
- Permission decorators (@login_required, @permission_required)
- Audit logging for all authentication events

#### Web UI (Phase 4)
- Bootstrap 5.3.2 responsive interface
- Interactive dependency graph visualization (vis.js Network 9.1.9)
- 22 web routes covering full application functionality
- Dashboard with real-time statistics
- Organization management UI (list, create, edit, delete)
- Entity management UI
- Graph visualization with filters (org, type, depth)
- Authentication pages (login, register, logout)
- License tier display in navigation
- Dark mode CSS support

#### gRPC API (Phase 5 - Enterprise)
- High-performance gRPC server with 45 RPC methods
- Protocol Buffers 3 (proto3) schema definitions
- gRPC-Web support via Envoy proxy
- Enterprise license validation requirement
- 100MB message size limits
- Server reflection for debugging
- Graceful shutdown handling
- Organization servicers (7 methods fully implemented)
- 5 additional service categories (38 methods stubbed)

#### Enterprise Features (Phase 6)
- **GitHub-Style Issues System**:
  - Issue tracking with labels, priorities, assignments
  - Comment threads and entity linking
  - 14 REST endpoints with role-based permissions
  - Default issue labels (bug, enhancement, documentation, etc.)
- **Resource-Level Roles**:
  - Maintainer, Operator, Viewer roles per entity/org
  - 6 REST endpoints for role management
  - Hierarchical permission checking
- **Typed Metadata**:
  - Custom metadata fields with type validation
  - Support for string, number, date, boolean, JSON types
  - System metadata (read-only) support
  - 8 REST endpoints (4 for entities, 4 for organizations)

#### Infrastructure & DevOps (Phase 8)
- **GitHub Actions CI/CD**:
  - Comprehensive test pipeline (lint, security, unit, integration)
  - Multi-arch Docker builds (amd64 + arm64)
  - Security scanning (Trivy + Safety)
  - Code coverage tracking (Codecov)
- **Kubernetes Manifests**:
  - Production-ready deployments
  - Resource limits and health checks
  - Secret management
- **Helm Charts**:
  - Complete Helm chart with 14 templates
  - 50+ configurable parameters
  - Bitnami PostgreSQL and Redis dependencies
  - Ingress, HPA, ServiceMonitor, NetworkPolicy support
  - 400+ line README with examples
- **Structured Logging**:
  - Multi-destination logging (console, syslog, Kafka, CloudWatch, GCP)
  - Verbosity levels (-v, -vv, -vvv)
  - HTTP3/QUIC support for Kafka
  - 600+ line documentation
- **Monitoring**:
  - Prometheus metrics endpoint
  - Custom Grafana dashboard (11 panels)
  - HTTP, gRPC, database, and infrastructure metrics

#### Websites & Documentation (Phase 9)
- **Marketing Website** (elder.penguintech.io):
  - Modern design with subtle purple/indigo gradients
  - Multi-page structure (Home, Features, Pricing)
  - Fully responsive design
  - Interactive SVG graph visualization
  - 3 HTML pages, 600+ lines of CSS
- **Documentation Website** (elder-docs.penguintech.io):
  - MkDocs Material theme
  - 8-section navigation structure
  - Quick start guide (5-minute setup)
  - License tier information
  - Dark/light mode toggle

#### Testing & Quality (Phase 10)
- Unit tests for models (Organization, Entity)
- Unit tests for API endpoints (Organizations)
- Integration tests for complete workflows
- Comprehensive test fixtures and mocking
- 80%+ code coverage target
- Security-focused testing (no network calls in unit tests)

### 🔐 Security

- TLS 1.2 minimum, TLS 1.3 preferred
- Input validation with marshmallow schemas
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention with Jinja2 auto-escaping
- CSRF protection with Flask-WTF
- Rate limiting to prevent abuse
- Comprehensive audit logging
- Environment variable-based secrets management
- Container vulnerability scanning
- Multi-factor authentication support

### 📦 Deployment

- Docker multi-stage builds with debian-slim base images
- Docker Compose for development and production
- Kubernetes manifests for production deployment
- Helm charts for easy Kubernetes installation
- Multi-architecture support (amd64/arm64)
- Production-ready configuration templates

### 🏢 License Tiers

- **Community**: Up to 100 entities, local auth, basic features
- **Professional** ($99/mo): Unlimited entities, SAML/OAuth2, advanced features
- **Enterprise** (Custom): All features + gRPC API, LDAP sync, 24/7 support

### 📊 API Summary

- **REST Endpoints**: 79 total
  - Organizations: 9
  - Entities: 8
  - Dependencies: 9
  - Graph: 3
  - Auth: 7
  - Identities: 13
  - Lookup: 2
  - Resource Roles: 6
  - Issues: 14
  - Metadata: 8

- **gRPC Methods**: 45 total
  - Authentication: 11
  - Organizations: 7
  - Entities: 7
  - Dependencies: 7
  - Graph: 4
  - Health: 1
  - Resource Roles: 6
  - Issues: 14 (future)
  - Metadata: 8 (future)

### 🛠️ Technical Stack

- **Backend**: Python 3.13, Flask, SQLAlchemy, Alembic
- **APIs**: REST (OpenAPI 3.0), gRPC (protobuf)
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Frontend**: HTML5, Bootstrap 5, vis.js Network
- **Auth**: SAML (python3-saml), OAuth2 (Authlib), JWT
- **Monitoring**: Prometheus, Grafana
- **Container**: Docker, docker-compose
- **Orchestration**: Kubernetes, Helm

### 📝 Documentation

- Comprehensive README.md with badges and ASCII art
- Complete .PLAN file documenting all implementation phases
- API documentation via OpenAPI/Swagger
- gRPC API documentation (600+ lines)
- Helm chart README (400+ lines)
- Logging documentation (600+ lines)
- Marketing website with features and pricing
- MkDocs-based documentation site

### 🐛 Known Issues

- gRPC servicers: 40 of 45 methods are stubs (5 fully implemented)
- Sparse checkout submodule not implemented (skipped due to complexity)
- Website deployment pending (sites created but not yet deployed)
- Some enterprise features require additional polish

### 🔄 Upgrade Notes

This is the initial release. No upgrade path required.

### 🙏 Acknowledgments

Built with these excellent open-source projects:
- Flask, SQLAlchemy, gRPC, vis.js, Bootstrap, PostgreSQL, Redis

Developed by **Penguin Tech Inc** - https://www.penguintech.io

---

## Future Releases

### [0.2.0] - Planned

**Optional Enhancements (Phase 6a)**:
- LDAP/SAML group synchronization
- Import/export functionality (JSON, YAML, CSV)
- WebSocket real-time updates for graph changes
- Advanced search and filtering
- Bulk operations
- Complete remaining gRPC servicer implementations

**License Integration Refinement (Phase 7)**:
- Enhanced license server integration
- Keepalive reporting
- License management UI for admins
- Stricter tier enforcement

---

For detailed implementation history, see [.PLAN](.PLAN) in the repository root.

Copyright © 2024 Penguin Tech Inc. All rights reserved.
