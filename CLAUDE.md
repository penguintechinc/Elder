# Elder - Claude Code Context

## Project Overview

Elder is a comprehensive infrastructure and asset management platform incorporating best practices and patterns from Penguin Tech Inc projects. It provides a standardized foundation for multi-language applications with enterprise-grade infrastructure and integrated licensing.

**Project Features:**
- Multi-language support (Go 1.23.x, Python 3.12/3.13, Node.js 18+)
- Enterprise security and licensing integration
- Comprehensive CI/CD pipeline
- Production-ready containerization
- Monitoring and observability
- Version management system
- PenguinTech License Server integration

## Elder Domain Terminology

Elder uses specific terminology for organizing tracked items:

- **Resources**: Items with dedicated database models and specialized schemas (Identity, Software, Services, Network objects, IPAM entries). These are structured data types with type-specific fields and relationships. Resources are gradually replacing generic Entities for better data modeling.

- **Entities**: Items stored in the generic `entities` table with a basic, flexible structure. These represent infrastructure components that don't yet have dedicated Resource models. Over time, common entity types may be promoted to Resources.

- **Elements**: Supporting items that provide context and metadata for Resources and Entities. Examples include:
  - Issues (tracking problems/tasks)
  - Labels (categorization)
  - Metadata fields (custom properties)
  - Dependencies (relationships between items)
  - Comments and attachments

- **Village ID**: A unique 64-bit hierarchical hexadecimal identifier assigned to all trackable items.
  - Format: `TTTT-OOOO-IIIIIIII` (18 chars with dashes)
  - `TTTT`: 16-bit tenant segment (4 hex chars) - randomized, unique per tenant
  - `OOOO`: 16-bit organization segment (4 hex chars) - randomized, unique per org
  - `IIIIIIII`: 32-bit item segment (8 hex chars) - randomized
  - Tenants: `a1b2-0000-00000000` (org and item zeroed)
  - Organizations: `a1b2-c3d4-00000000` (item zeroed)
  - Items: `a1b2-c3d4-e5f67890` (full hierarchy)
  - Enables sharing/referencing any item via `/id/{village_id}` without knowing its type
  - Instantly shows tenant/org ownership from the ID itself

## Technology Stack

### Languages & Frameworks
- **Go**: 1.23.x (latest patch version)
- **Python**: 3.13+ for all applications
  - **Flask**: Primary web framework for REST APIs
  - **Flask-RESTful / Flask-RESTX**: REST API development
  - **SQLAlchemy & PyDAL**: Hybrid approach - SQLAlchemy for initialization, PyDAL for day-to-day operations
  - **Marshmallow**: Schema validation and serialization
- **Node.js**: 18+ for sales/marketing websites and tooling only
- **JavaScript/TypeScript**: Modern ES2022+ standards

### Infrastructure & DevOps
- **Containers**: Docker with multi-stage builds, Docker Compose
- **Orchestration**: Kubernetes with Helm charts
- **Configuration Management**: Ansible for infrastructure automation
- **CI/CD**: GitHub Actions with comprehensive pipelines
- **Monitoring**: Prometheus metrics, Grafana dashboards
- **Logging**: Structured logging with configurable levels

### Databases & Storage
- **Primary**: PostgreSQL (default), MySQL, or SQLite - with connection pooling, non-root user/password, dedicated database
- **MariaDB Galera Cluster**: Optional high-availability configuration for MySQL deployments
- **Cache**: Redis/Valkey with optional TLS and authentication
- **ORMs**: SQLAlchemy for Python initialization, PyDAL for day-to-day operations; GORM for Go
- **Migrations**: Alembic for Python database migrations, automated schema management
- **Database Support**: Supports PostgreSQL, MySQL, SQLite (via DB_TYPE configuration)

### Security & Authentication
- **TLS**: Enforce TLS 1.2 minimum, prefer TLS 1.3
- **HTTP3/QUIC**: Utilize UDP with TLS for high-performance connections where possible
- **Authentication**: JWT and MFA (standard), mTLS where applicable; uses Flask-Security-Too
- **SSO**: SAML/OAuth2 SSO as enterprise-only features
- **Guest Login**: Optional read-only guest access (disabled by default)
  - Controlled by `ENABLE_GUEST_LOGIN` environment variable
  - Provides viewer role with read-only permissions
  - Configurable username and password via environment variables
  - Creates guest user automatically on database initialization when enabled
- **Secrets**: Environment variable management
- **Scanning**: Trivy vulnerability scanning, CodeQL analysis

## License & Legal

**License File**: `LICENSE.md` (located at project root)

**License Type**: Limited AGPL-3.0 with commercial use restrictions and Contributor Employer Exception

The `LICENSE.md` file is located at the project root following industry standards. This project uses a modified AGPL-3.0 license with additional exceptions for commercial use and special provisions for companies employing contributors.

- **License Server**: https://license.penguintech.io
- **Company Website**: www.penguintech.io
- **Support**: support@penguintech.io

---

**Current Version**: See `.version` file
**Last Updated**: 2025-12-18
**Maintained by**: Penguin Tech Inc
