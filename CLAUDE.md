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

## PenguinTech License Server Integration

All projects should integrate with the centralized PenguinTech License Server at `https://license.penguintech.io` for feature gating and enterprise functionality.

**See full documentation:** [docs/development/license-server-integration.md](docs/development/license-server-integration.md)

Key features:
- License key format: `PENG-XXXX-XXXX-XXXX-XXXX-ABCD`
- Universal JSON response format
- API endpoints: `/api/v2/validate`, `/api/v2/features`, `/api/v2/keepalive`
- Python and Go client examples

## WaddleAI Integration (Optional)

For projects requiring AI capabilities, integrate with WaddleAI located at `~/code/WaddleAI`.

**When to Use WaddleAI:**
- Natural language processing (NLP)
- Machine learning model inference
- AI-powered features and automation
- Intelligent data analysis
- Chatbots and conversational interfaces

**Integration Pattern:**
- WaddleAI runs as separate microservice container
- Communicate via REST API or gRPC
- Environment variable configuration for API endpoints
- License-gate AI features as enterprise functionality

**WaddleAI Documentation**: See WaddleAI project at `~/code/WaddleAI` for integration details

## Project Structure

```
project-name/
├── .github/
│   ├── workflows/           # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/      # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── apps/                    # Application code
│   ├── api/                 # API services (Go/Python)
│   ├── web/                 # Web applications (Python/Node.js)
│   └── cli/                 # CLI tools (Go)
├── services/                # Microservices
│   ├── service-name/
│   │   ├── cmd/             # Go main packages
│   │   ├── internal/        # Private application code
│   │   ├── pkg/             # Public library code
│   │   ├── Dockerfile       # Service container
│   │   └── go.mod           # Go dependencies
├── shared/                  # Shared components
│   ├── auth/                # Authentication utilities
│   ├── config/              # Configuration management
│   ├── database/            # Database utilities
│   ├── licensing/           # License server integration
│   ├── monitoring/          # Metrics and logging
│   └── types/               # Shared types/schemas
├── web/                     # Frontend applications
│   ├── public/              # Static assets
│   ├── src/                 # Source code
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile           # Web container
├── infrastructure/          # Infrastructure as code
│   ├── docker/              # Docker configurations
│   ├── k8s/                 # Kubernetes manifests
│   ├── helm/                # Helm charts
│   └── monitoring/          # Prometheus/Grafana configs
├── scripts/                 # Utility scripts
│   ├── build/               # Build automation
│   ├── deploy/              # Deployment scripts
│   ├── test/                # Testing utilities
│   └── version/             # Version management
├── tests/                   # Test suites
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── e2e/                 # End-to-end tests
│   └── performance/         # Performance tests
├── docs/                    # Documentation
│   ├── api/                 # API documentation
│   ├── deployment/          # Deployment guides
│   ├── development/         # Development setup
│   ├── licensing/           # License integration guide
│   ├── architecture/        # System architecture
│   └── RELEASE_NOTES.md     # Version release notes (prepend new releases)
├── config/                  # Configuration files
│   ├── development/         # Dev environment configs
│   ├── production/          # Production configs
│   └── testing/             # Test environment configs
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── Makefile                 # Build automation
├── go.mod                   # Go workspace
├── requirements.txt         # Python dependencies
├── package.json             # Node.js workspace
├── .version                 # Version tracking
├── VERSION.md               # Versioning guidelines
├── README.md                # Project documentation
├── CONTRIBUTING.md          # Contribution guidelines
├── SECURITY.md              # Security policies
├── LICENSE.md               # License information
└── CLAUDE.md                # This file
```

## Container Architecture

### Multi-Database Container Architecture
Elder supports multiple database backends with containerized deployments optimized for each:

**PostgreSQL (Default)**
- Primary database for all deployments
- Container: Official `postgres:latest` (Debian-slim based)
- Features: Full ACID compliance, JSON support, advanced indexing
- Connection pooling: Via SQLAlchemy pool settings and pgBouncer
- Environment: `DB_TYPE=postgres`

**MySQL/MariaDB**
- Alternative for existing MySQL installations
- Container: `mariadb:latest` or `mysql:latest`
- MariaDB Galera Cluster: Optional high-availability configuration
  - Multi-master replication across cluster nodes
  - Synchronous replication with transaction consistency
  - Automatic node failure detection and recovery
  - Load balancing via ProxySQL or HAProxy
- Container Networking: Galera nodes communicate via dedicated network overlay
- Environment: `DB_TYPE=mysql` or `DB_TYPE=mariadb`

**SQLite (Development/Embedded)**
- Lightweight option for single-server deployments or development
- No external container required (file-based in-app storage)
- Environment: `DB_TYPE=sqlite`

### Database Configuration
- **DB_TYPE**: Required environment variable - must be one of: `postgres`, `mysql`, `sqlite`
- **Connection Pool**: Configured per database type
  - PostgreSQL: SQLAlchemy pool with pgBouncer integration
  - MySQL/MariaDB: SQLAlchemy pool with connection multiplexing
  - SQLite: Direct file-based connections
- **Migration Strategy**: Alembic migrations compatible with all three database backends
- **ORM Configuration**: SQLAlchemy for schema initialization, PyDAL for daily operations

### Container Networking
- **Service discovery**: All services accessible via Docker Compose service names
- **Internal communication**: Services communicate over internal bridge network
- **Database connectivity**: Each application container has direct database access
- **Galera cluster**: Dedicated overlay network for multi-master replication (MariaDB HA)
- **Persistent volumes**: Database data persists across container restarts

## Version Management System

### Format: vMajor.Minor.Patch.build
- **Major**: Breaking changes, API changes, removed features
- **Minor**: Significant new features and functionality additions
- **Patch**: Minor updates, bug fixes, security patches
- **Build**: Epoch64 timestamp of build time (used between releases for automatic chronological ordering)

### Version Update Process
```bash
# Update version using provided scripts
./scripts/version/update-version.sh          # Increment build timestamp
./scripts/version/update-version.sh patch    # Increment patch version
./scripts/version/update-version.sh minor    # Increment minor version
./scripts/version/update-version.sh major    # Increment major version
./scripts/version/update-version.sh 1 2 3    # Set specific version
```

### Version Integration
- Embedded in applications and API responses
- Docker images tagged with full version for dev, semantic for releases
- Automated version bumping in CI/CD pipeline
- Version validation in build processes

## Development Workflow

### Local Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd project-name
make setup                    # Install dependencies and setup environment
make dev                      # Start development environment
```

### Essential Commands
```bash
# Development
make dev                      # Start development services
make test                     # Run all tests
make lint                     # Run linting and code quality checks
make build                    # Build all services
make clean                    # Clean build artifacts

# Production
make docker-build             # Build production containers
make docker-push              # Push to registry
make deploy-dev               # Deploy to development
make deploy-prod              # Deploy to production

# Testing
make test-unit               # Run unit tests
make test-integration        # Run integration tests
make test-e2e                # Run end-to-end tests
make test-performance        # Run performance tests

# License Management
make license-validate        # Validate license configuration
make license-check-features  # Check available features
```

### Docker Compose Usage

**IMPORTANT**: Use Docker Compose V2 (`docker compose` with a space) for managing containers. V2 is faster, has better error handling, and avoids compatibility issues with newer Docker images.

**Note**: The legacy `docker-compose` (with hyphen) v1.29.2 has known issues like `ContainerConfig` KeyError. Always use the V2 plugin syntax.

**Installing Docker Compose V2** (if not already installed):
```bash
# Install as Docker CLI plugin
mkdir -p ~/.docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

# Verify installation
docker compose version
```

```bash
# Start all services
docker compose up -d

# Start specific services
docker compose up -d postgres redis
docker compose up -d api web

# Stop all services
docker compose down

# Stop specific services
docker compose stop api web

# Restart services (WARNING: does NOT load new images - use recreate instead)
docker compose restart api

# Rebuild AND recreate a single container (USE THIS to deploy code changes)
docker compose down web && docker compose up -d --build web
docker compose down api && docker compose up -d --build api

# View logs
docker compose logs -f api
docker compose logs -f postgres

# Check running services
docker compose ps

# Rebuild and restart services
docker compose up -d --build api web

# Remove all containers and volumes (DESTRUCTIVE)
docker compose down -v
```

**Never use these commands**:
- ❌ `docker run -d --name elder-api ...` (Use `docker compose up -d api` instead)
- ❌ `docker stop elder-api` (Use `docker compose stop api` instead)
- ❌ `docker rm elder-api` (Use `docker compose down` instead)
- ❌ `docker ps` for Elder services (Use `docker compose ps` instead)
- ❌ `docker-compose` (legacy v1 with hyphen - use `docker compose` v2 instead)
- ❌ `docker compose restart` after code changes (Use `docker compose down && docker compose up -d --build` instead - restart only restarts the existing container, it does NOT rebuild or load new images)

**Service Names** (use these with docker compose):
- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `api` - Flask REST API
- `web` - React web UI
- `grpc-server` - gRPC server (enterprise)
- `prometheus` - Prometheus monitoring
- `grafana` - Grafana dashboards

**Container Names** (for `docker exec` only):
- `elder-postgres`
- `elder-redis`
- `elder-api`
- `elder-web`
- `elder-grpc-server`
- `elder-prometheus`
- `elder-grafana`

## Security Requirements

### Input Validation
- ALL inputs MUST have appropriate validators
- Use framework-native validation (pydal validators, Go validation libraries)
- Implement XSS and SQL injection prevention
- Server-side validation for all client input
- CSRF protection using framework native features

### Authentication & Authorization
- Multi-factor authentication support
- Role-based access control (RBAC)
- API key management with rotation
- JWT token validation with proper expiration
- Session management with secure cookies

### Security Scanning
- Automated dependency vulnerability scanning
- Container image security scanning
- Static code analysis for security issues
- Regular security audit logging
- Secrets scanning in CI/CD pipeline

## Enterprise Features

### Licensing Integration
- PenguinTech License Server integration
- Feature gating based on license tiers
- Usage tracking and reporting
- Compliance audit logging
- Enterprise support escalation

### Multi-Tenant Architecture
- Customer isolation and data segregation
- Per-tenant configuration management
- Usage-based billing integration
- White-label capabilities
- Compliance reporting (SOC2, ISO27001)

### Monitoring & Observability
- Prometheus metrics collection
- Grafana dashboards for visualization
- Structured logging with correlation IDs
- Distributed tracing support
- Real-time alerting and notifications

## CI/CD Pipeline Features

### Testing Pipeline
- Multi-language testing (Go, Python, Node.js)
- Parallel test execution for performance
- Code coverage reporting
- Security scanning integration (bandit, Safety, Trivy)
- Performance regression testing
- **See detailed workflow documentation:** [docs/WORKFLOWS.md](docs/WORKFLOWS.md)

### Build Pipeline
- **Multi-architecture Docker builds** (amd64/arm64) using separate parallel workflows
- **Debian-slim base images** for all container builds to minimize size and attack surface
- **Parallel workflow execution** to minimize total build time without removing functionality
- **Optimized build times**: Prioritize speed while maintaining full functionality
- Dependency caching for faster builds
- Artifact management and versioning
- Container registry integration (ghcr.io)
- Build optimization and layer caching

### Deployment Pipeline
- Environment-specific deployment configs
- Blue-green deployment support
- Rollback capabilities
- Health check validation
- Automated database migrations

### Version Management & Release Automation
- **Version File Monitoring**: `.version` file path triggers automated releases
- **Epoch64 Timestamp Detection**: Extracts Unix timestamp from version (vMajor.Minor.Patch.epoch64)
- **Semantic Version Extraction**: Intelligently parses version components
- **Pre-release Creation**: Automatic GitHub pre-release generation
- **Release Notes Generation**: Version, epoch64, and commit details included
- **Duplicate Prevention**: Checks for existing releases before creation
- **Example Version Format**: `3.0.0.1764083000` (Major.Minor.Patch.epoch64)

### Security Scanning
- **Code Security**:
  - bandit for Python security analysis
  - Safety for Python dependencies
  - Trivy for container images and filesystem
  - SARIF report generation for GitHub Security tab

- **Dependency Security**:
  - Pre-commit hooks block vulnerable dependencies
  - GitHub Dependabot alerts monitoring
  - Regular security audits

### Quality Gates
- Required code review process (2+ approvals)
- Automated testing requirements
- Security scan pass requirements
- Code quality standards (see [docs/STANDARDS.md](docs/STANDARDS.md))
- Performance benchmark validation
- Documentation update verification

## Critical Development Rules

### Development Philosophy: Safe, Stable, and Feature-Complete

**NEVER take shortcuts or the "easy route" - ALWAYS prioritize safety, stability, and feature completeness**

#### Core Principles
- **No Quick Fixes**: Resist quick workarounds or partial solutions
- **Complete Features**: Fully implemented with proper error handling and validation
- **Safety First**: Security, data integrity, and fault tolerance are non-negotiable
- **Stable Foundations**: Build on solid, tested components
- **Future-Proof Design**: Consider long-term maintainability and scalability
- **No Technical Debt**: Address issues properly the first time

#### Red Flags (Never Do These)
- Skipping input validation "just this once"
- Hardcoding credentials or configuration
- Ignoring error returns or exceptions
- Commenting out failing tests to make CI pass
- Deploying without proper testing
- Using deprecated or unmaintained dependencies
- Implementing partial features with "TODO" placeholders
- Bypassing security checks for convenience
- Assuming data is valid without verification
- Leaving debug code or backdoors in production

#### Quality Checklist Before Completion
- All error cases handled properly
- Unit tests cover all code paths
- Integration tests verify component interactions
- Security requirements fully implemented
- Performance meets acceptable standards
- Documentation complete and accurate
- Code review standards met
- No hardcoded secrets or credentials
- Logging and monitoring in place
- Build passes in containerized environment
- No security vulnerabilities in dependencies
- Edge cases and boundary conditions tested

### Git Workflow
- **NEVER commit automatically** unless explicitly requested by the user
- **NEVER push to remote repositories** under any circumstances
- **ONLY commit when explicitly asked** - never assume commit permission
- **UPDATE RELEASE_NOTES.md**: Update `docs/RELEASE_NOTES.md` on every version update or significant feature push
  - Prepend new entries to the top of the file (newest first)
  - Follow Keep a Changelog format
  - Include: New Features, Bug Fixes, Breaking Changes, Security Fixes
  - Reference related commits or PRs where applicable
- Always use feature branches for development
- Require pull request reviews for main branch
- Automated testing must pass before merge

### Local State Management (Crash Recovery)
- **ALWAYS maintain local .PLAN and .TODO files** for crash recovery
- **Keep .PLAN file updated** with current implementation plans and progress
- **Keep .TODO file updated** with task lists and completion status
- **Update these files in real-time** as work progresses to prevent data loss
- **Add to .gitignore**: Both .PLAN and .TODO files must be in .gitignore as they can expose sensitive information
- **File format**: Use simple text format for easy recovery and readability
- **Automatic recovery**: Upon restart, check for existing .PLAN and .TODO files to resume work

### Dependency Security Requirements
- **ALWAYS check for Dependabot alerts** before every commit using GitHub CLI or API
- **Monitor vulnerabilities via Socket.dev** for all Python, Go, and Node.js dependencies
- **Socket.dev MCP Tool**: Available locally via `.mcp.json` for pre-commit dependency scanning
  - API key configured in `~/.bashrc` as `SOCKET_API_KEY`
  - Run scans before pushing dependency changes to catch supply chain risks
  - Socket.dev is also integrated in CI/CD for automated scanning
- **Mandatory security scanning** before any dependency changes are committed
- **Fix all security alerts immediately** - no commits with outstanding vulnerabilities
- **Automated dependency updates**: Use tools like Dependabot, Renovate, or custom scripts
- **Version pinning strategy**: Use exact versions for security-critical dependencies
- **Regular security audits**:
  - `npm audit` for Node.js projects
  - `go mod audit` or equivalent tools for Go projects
  - `safety check` or equivalent for Python projects
- **Vulnerability response process**:
  1. Identify affected packages and severity
  2. Update to patched versions immediately
  3. Test updated dependencies thoroughly
  4. Document security fixes in commit messages
  5. Verify no new vulnerabilities introduced

### Build & Deployment Requirements
- **NEVER mark tasks as completed until successful build verification**
- All Go and Python builds MUST be executed within Docker containers for consistency
- Use containerized builds for both local development and CI/CD pipelines
- Build failures must be resolved before task completion
- Container builds ensure environment consistency across development and production

### Database Schema Change Policy
- **ONLY change database schema when absolutely necessary** - schema changes can break other components and backwards compatibility
- **Prefer code-level solutions** - store extra fields in JSON columns (like `config_json`, `metadata`) rather than adding new columns
- **Migration requirements if schema change is needed**:
  1. Create proper Alembic migration
  2. Test migration on copy of production data
  3. Ensure rollback capability
  4. Update all dependent code paths
  5. Coordinate with frontend and other services
- **Schema freezes during releases** - no schema changes in release branches
- **Document schema changes** - update ERD diagrams and data model documentation

### Docker Build Standards

**CRITICAL: ALWAYS use `--no-cache` flag for production rebuilds**

```bash
# Correct workflow
docker compose build --no-cache api && docker compose restart api
docker compose build --no-cache web && docker compose restart web
```

**See full documentation:** [docs/development/ci-cd-patterns.md](docs/development/ci-cd-patterns.md)

Key points:
- Prevents stale frontend builds and cached outdated code
- Use debian-slim base images for all containers
- Multi-arch builds (amd64/arm64) in GitHub Actions

### Linting & Code Quality Requirements
- **ALL code must pass linting** before commit - no exceptions
- **Python**: flake8, black, isort, mypy (type checking), bandit (security)
- **JavaScript/TypeScript**: ESLint, Prettier
- **Go**: golangci-lint (includes staticcheck, gosec, etc.)
- **Ansible**: ansible-lint
- **Docker**: hadolint
- **YAML**: yamllint
- **Markdown**: markdownlint
- **Shell**: shellcheck
- **CodeQL**: All code must pass CodeQL security analysis
- **PEP Compliance**: Python code must follow PEP 8, PEP 257 (docstrings), PEP 484 (type hints)

### Code Quality
- Follow language-specific style guides
- Comprehensive test coverage (80%+ target)
- No hardcoded secrets or credentials
- Proper error handling and logging
- Security-first development approach

### DRY Principle - Shared Resources
- **Rule of Two**: If the same or nearly identical code appears in 2+ places, convert it to a shared resource
- **Create shared utilities** in `src/lib/` for frontend, `shared/` for backend
- **Examples of shared resources**:
  - Query keys and cache invalidation utilities (React Query)
  - API client functions
  - Form validation schemas
  - Type definitions
  - UI components with consistent patterns
- **Benefits**: Consistent behavior, single point of maintenance, reduced bugs

### API Design Principles
- **Avoid duplicative APIs**: Prefer updating existing APIs to be more flexible rather than creating new endpoints for similar functionality
- **Maintain backwards compatibility**: When extending APIs, ensure existing clients continue to work
- **Use optional parameters**: Add optional parameters to existing endpoints instead of creating variant endpoints
- **Consolidate similar operations**: One flexible endpoint is better than multiple specialized ones
- **Shared modals**: Make modals shared resources in `components/` as they may be reused across multiple pages (e.g., CreateIdentityModal can be used on IAM, Tenant, and Organization pages with different defaults)

### Unit Testing Requirements
- **All applications MUST have comprehensive unit tests**
- **Network isolation**: Unit tests must NOT require external network connections
- **No external dependencies**: Cannot reach databases, APIs, or external services
- **Use mocks/stubs**: Mock all external dependencies and I/O operations
- **KISS principle**: Keep unit tests simple, focused, and fast
- **Test isolation**: Each test should be independent and repeatable
- **Fast execution**: Unit tests should complete in milliseconds, not seconds

### Performance Best Practices
- **Always implement async/concurrent patterns** to maximize CPU and memory utilization
- **Python**: Use asyncio, threading, multiprocessing where appropriate
  - **Modern Python optimizations**: Leverage dataclasses, typing, and memory-efficient features from Python 3.12+
  - **Dataclasses**: Use @dataclass for structured data to reduce memory overhead and improve performance
  - **Type hints**: Use comprehensive typing for better optimization and IDE support
  - **Advanced features**: Utilize slots, frozen dataclasses, and other memory-efficient patterns
- **Go**: Leverage goroutines, channels, and the Go runtime scheduler
- **Networking Applications**: Implement high-performance networking optimizations:
  - eBPF/XDP for kernel-level packet processing and filtering
  - AF_XDP for high-performance user-space packet processing
  - NUMA-aware memory allocation and CPU affinity
  - Zero-copy networking techniques where applicable
  - Connection pooling and persistent connections
  - Load balancing with CPU core pinning
- **Memory Management**: Optimize for cache locality and minimize allocations
- **I/O Operations**: Use non-blocking I/O, buffering, and batching strategies
- **Database Access**: Implement connection pooling, prepared statements, and query optimization

### Documentation Standards
- **README.md**: Keep as overview and pointer to comprehensive docs/ folder
- **docs/ folder**: ONLY user guides, admin guides, API documentation, and architecture docs
- **NEVER put implementation notes in docs/**: Implementation summaries, task tracking, and developer notes go in /tmp
- **RELEASE_NOTES.md**: Maintain in docs/ folder, prepend new version releases to top
- Update CLAUDE.md when adding significant context
- API documentation must be comprehensive
- Architecture decisions should be documented
- Security procedures must be documented
- **Build status badges**: Always include in README.md
- **ASCII art**: Include catchy, project-appropriate ASCII art in README
- **Company homepage**: Point to www.penguintech.io
- **License**: All projects use Limited AGPL3 with preamble for fair use

### File Size Limits
- **Maximum file size**: 25,000 characters for ALL code and markdown files
- **Split large files**: Decompose into modules, libraries, or separate documents
- **CLAUDE.md exception**: Maximum 39,000 characters (only exception to 25K rule)
- **High-level approach**: CLAUDE.md contains high-level context and references detailed docs
- **Documentation strategy**: Create detailed documentation in `docs/` folder and link to them from CLAUDE.md
- **Keep focused**: Critical context, architectural decisions, and workflow instructions only
- **User approval required**: ALWAYS ask user permission before splitting CLAUDE.md files
- **Use Task Agents**: Utilize task agents (subagents) to be more expedient and efficient when making changes to large files, updating or reviewing multiple files, or performing complex multi-step operations

### README.md Standards
- **ALWAYS include build status badges** at the top of every README.md:
  - CI/CD pipeline status (GitHub Actions)
  - Test coverage status (Codecov)
  - Go Report Card (for Go projects)
  - Version badge
  - License badge (Limited AGPL3 with preamble for fair use)
- **ALWAYS include catchy ASCII art** below the build status badges
  - Use project-appropriate ASCII art that reflects the project's identity
  - Keep ASCII art clean and professional
  - Place in code blocks for proper formatting
- **Company homepage reference**: All project READMEs and sales websites should point to **www.penguintech.io** as the company's homepage
- **License standard**: All projects use Limited AGPL3 with preamble for fair use, not MIT

### CLAUDE.md File Management
- **Primary file**: Maintain main CLAUDE.md at project root
- **Split files when necessary**: For large/complex projects, create app-specific CLAUDE.md files
- **File structure for splits**:
  - `projectroot/CLAUDE.md` - Main context and cross-cutting concerns
  - `projectroot/app-folder/CLAUDE.md` - App-specific context and instructions
- **Root file linking**: Main CLAUDE.md should reference and link to app-specific files
- **User approval required**: ALWAYS ask user permission before splitting CLAUDE.md files
- **Split criteria**: Only split for genuinely large situations where single file becomes unwieldy

### Application Architecture Requirements

#### Web Framework Standards
- **Flask primary**: Use Flask for ALL REST API applications
  - **Flask-CORS**: For cross-origin resource sharing
  - **Flask-RESTful/RESTX**: For REST API development
  - **Flask-SQLAlchemy**: For database initialization and schema management
  - **Flask-Security-Too**: For authentication and user management (replaces Flask-Login)
  - **CSRF Protection**: Disable for REST APIs using JWT (use Flask-WTF `WTF_CSRF_CHECK_DEFAULT = False`)
- **Health endpoints**: ALL applications must implement `/healthz` endpoint
- **Metrics endpoints**: ALL applications must implement Prometheus metrics endpoint using `prometheus-flask-exporter`

#### Logging & Monitoring
- **Console logging**: Always implement console output
- **Multi-destination logging**: Support multiple log destinations:
  - UDP syslog to remote log collection servers (legacy)
  - HTTP3/QUIC to Kafka clusters for high-performance log streaming
  - Cloud-native logging services (AWS CloudWatch, GCP Cloud Logging) via HTTP3
- **Logging levels**: Implement standardized verbosity levels:
  - `-v`: Warnings and criticals only
  - `-vv`: Info level (default)
  - `-vvv`: Debug logging
- **getopts**: Use Python getopts library instead of params where possible

#### Database & Caching Standards
- **PostgreSQL default**: Default to PostgreSQL with connection pooling, non-root user/password, and dedicated database
- **SQLAlchemy usage**: Use SQLAlchemy as the primary ORM for Python applications
  - **Flask-SQLAlchemy**: Flask integration for database operations
  - **Alembic**: Database migration management
- **Redis/Valkey**: Utilize Redis/Valkey with optional TLS and authentication where appropriate
  - **Flask-Caching**: Flask integration for caching

#### Security Implementation
- **TLS enforcement**: Enforce TLS 1.2 minimum, prefer TLS 1.3
- **Connection security**: Use HTTPS connections where possible, WireGuard where HTTPS not available
- **Modern logging transport**: HTTP3/QUIC for Kafka and cloud logging services (AWS/GCP)
- **Legacy syslog**: UDP syslog maintained for compatibility
- **Standard security**: Implement JWT, MFA, and mTLS in all versions where applicable
- **Enterprise SSO**: SAML/OAuth2 SSO as enterprise-only features
- **HTTP3/QUIC**: Use UDP with TLS for high-performance connections where possible

### Ansible Integration Requirements
- **Documentation Research**: ALWAYS research Ansible modules on https://docs.ansible.com before implementation
- **Module verification**: Check official documentation for:
  - Correct module names and syntax
  - Required and optional parameters
  - Return values and data structures
  - Version compatibility and requirements
- **Best practices**: Follow Ansible community standards and idempotency principles
- **Testing**: Ensure playbooks are idempotent and properly handle error conditions

### Website Integration Requirements

**See full documentation:** [docs/development/website-integration.md](docs/development/website-integration.md)

Key principles:
- Each project needs marketing (Node.js) and documentation (Markdown) websites
- **Modal-first approach** - prefer modals over routes for secondary actions
- **Clickable cards** - all object cards should open detail modals on click
- Use sparse checkout submodule from `github.com/penguintechinc/website`

## Common Integration Patterns

Common code patterns for database, API, and monitoring integration.

**See full documentation:** [docs/development/integration-patterns.md](docs/development/integration-patterns.md)

Includes examples for:
- License-gated features (Python decorators, Go feature checking)
- Database integration (SQLAlchemy, GORM)
- API development (Flask blueprints, Gin routes)
- Monitoring integration (Prometheus metrics)

## User Environment

### Screenshots
- **Location**: `~/Pictures/Screenshots/`
- When the user mentions taking a screenshot, check this directory for the most recent file
- Use `ls -lt ~/Pictures/Screenshots/ | head -5` to find recent screenshots

## Troubleshooting & Support

### Common Issues
1. **Port Conflicts**: Check docker-compose port mappings
2. **Database Connections**: Verify connection strings and permissions
3. **License Validation Failures**: Check license key format and network connectivity
4. **Build Failures**: Check dependency versions and compatibility
5. **Test Failures**: Review test environment setup

### Debug Commands
```bash
# Container debugging
docker-compose logs -f service-name
docker exec -it container-name /bin/bash

# Application debugging
make debug                    # Start with debug flags
make logs                     # View application logs
make health                   # Check service health

# License debugging
make license-debug            # Test license server connectivity
make license-validate         # Validate current license
```

### License Server Support
- **Technical Documentation**: Complete API reference available
- **Integration Support**: support@penguintech.io
- **Sales Inquiries**: sales@penguintech.io
- **License Server Status**: https://status.penguintech.io

## Template Customization

### Adding New Languages
1. Create language-specific directory structure
2. Add Dockerfile and build scripts
3. Update CI/CD pipeline configuration
4. Add language-specific linting and testing
5. Update documentation and examples

### Adding New Services
1. Use service template in `services/` directory
2. Configure service discovery and networking
3. Add monitoring and logging integration
4. Integrate license checking for service features
5. Create service-specific tests
6. Update deployment configurations

### Enterprise Integration
- Configure license server integration
- Set up multi-tenant data isolation
- Implement usage tracking and reporting
- Add compliance audit logging
- Configure enterprise monitoring

---

**Project Version**: 1.0.0
**Last Updated**: 2025-12-18
**Maintained by**: Penguin Tech Inc
**License Server**: https://license.penguintech.io

*This project provides a production-ready foundation for enterprise software development with comprehensive tooling, security, operational capabilities, and integrated licensing management.*
