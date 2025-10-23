# Project Template - Claude Code Context

## Project Overview

This is a comprehensive project template incorporating best practices and patterns from Penguin Tech Inc projects. It provides a standardized foundation for multi-language projects with enterprise-grade infrastructure and integrated licensing.

**Template Features:**
- Multi-language support (Go 1.23.x, Python 3.12/3.13, Node.js 18+)
- Enterprise security and licensing integration
- Comprehensive CI/CD pipeline
- Production-ready containerization
- Monitoring and observability
- Version management system
- PenguinTech License Server integration

## Technology Stack

### Languages & Frameworks
- **Go**: 1.23.x (latest patch version)
- **Python**: 3.12 for py4web applications (py4web has issues with 3.13), 3.13 for non-web applications
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
- **Primary**: PostgreSQL with connection pooling, non-root user/password, dedicated database
- **Cache**: Redis/Valkey with optional TLS and authentication
- **ORMs**: PyDAL for Python (supports MySQL, PostgreSQL, etc.), GORM for Go
- **Migrations**: Automated schema management
- **Database Support**: Use PyDAL only for databases with full PyDAL support

### Security & Authentication
- **TLS**: Enforce TLS 1.2 minimum, prefer TLS 1.3
- **HTTP3/QUIC**: Utilize UDP with TLS for high-performance connections where possible
- **Authentication**: JWT and MFA (standard), mTLS where applicable
- **SSO**: SAML/OAuth2 SSO as enterprise-only features
- **Secrets**: Environment variable management
- **Scanning**: Trivy vulnerability scanning, CodeQL analysis

## PenguinTech License Server Integration

All projects should integrate with the centralized PenguinTech License Server at `https://license.penguintech.io` for feature gating and enterprise functionality.

### Universal JSON Response Format

All API responses follow this standardized structure based on the `.JSONDESIGN` specification:

```json
{
    "customer": "string",           // Organization name
    "product": "string",            // Product identifier
    "license_version": "string",    // License schema version (2.0)
    "license_key": "string",        // Full license key
    "expires_at": "ISO8601",        // Expiration timestamp
    "issued_at": "ISO8601",         // Issue timestamp
    "tier": "string",               // community/professional/enterprise
    "features": [
        {
            "name": "string",           // Feature identifier
            "entitled": boolean,        // Feature enabled/disabled
            "units": integer,           // Usage units (0 = unlimited, -1 = not applicable)
            "description": "string",    // Human-readable description
            "metadata": object          // Additional feature-specific data
        }
    ],
    "limits": {
        "max_servers": integer,     // -1 = unlimited
        "max_users": integer,       // -1 = unlimited
        "data_retention_days": integer
    },
    "metadata": {
        "server_id": "string",      // For keepalives
        "support_tier": "string",   // community/email/priority
        "custom_fields": object     // Customer-specific data
    }
}
```

### Authentication

All API calls use Bearer token authentication where the license key serves as the bearer token:

```bash
Authorization: Bearer PENG-XXXX-XXXX-XXXX-XXXX-ABCD
```

### License Key Format

- Format: `PENG-XXXX-XXXX-XXXX-XXXX-ABCD`
- Regex: `^PENG-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$`
- Includes SHA256 checksum in final segment
- Universal prefix for all PenguinTech products

### Core API Endpoints

#### 1. Universal License Validation

**Endpoint:** `POST /api/v2/validate`

```bash
curl -X POST https://license.penguintech.io/api/v2/validate \
  -H "Authorization: Bearer PENG-XXXX-XXXX-XXXX-XXXX-ABCD" \
  -H "Content-Type: application/json" \
  -d '{"product": "your-product-name"}'
```

#### 2. Feature Checking

**Endpoint:** `POST /api/v2/features`

```bash
curl -X POST https://license.penguintech.io/api/v2/features \
  -H "Authorization: Bearer PENG-XXXX-XXXX-XXXX-XXXX-ABCD" \
  -H "Content-Type: application/json" \
  -d '{"product": "your-product-name", "feature": "advanced_feature"}'
```

#### 3. Keepalive/Usage Reporting

**Endpoint:** `POST /api/v2/keepalive`

```bash
curl -X POST https://license.penguintech.io/api/v2/keepalive \
  -H "Authorization: Bearer PENG-XXXX-XXXX-XXXX-XXXX-ABCD" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "your-product-name",
    "server_id": "srv_8f7d6e5c4b3a2918",
    "hostname": "server-01.company.com",
    "version": "1.2.3",
    "uptime_seconds": 86400,
    "usage_stats": {
        "active_users": 45,
        "feature_usage": {
            "feature_name": {"usage_count": 1250000}
        }
    }
  }'
```

### Client Library Integration

#### Python Client Example

```python
import requests
from datetime import datetime, timedelta

class PenguinTechLicenseClient:
    def __init__(self, license_key, product, base_url="https://license.penguintech.io"):
        self.license_key = license_key
        self.product = product
        self.base_url = base_url
        self.server_id = None
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {license_key}",
            "Content-Type": "application/json"
        })

    def validate(self):
        """Validate license and get server ID for keepalives"""
        response = self.session.post(
            f"{self.base_url}/api/v2/validate",
            json={"product": self.product}
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                self.server_id = data["metadata"].get("server_id")
                return data

        return {"valid": False, "message": f"Validation failed: {response.text}"}

    def check_feature(self, feature):
        """Check if specific feature is enabled"""
        response = self.session.post(
            f"{self.base_url}/api/v2/features",
            json={"product": self.product, "feature": feature}
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("features", [{}])[0].get("entitled", False)

        return False

    def keepalive(self, usage_data=None):
        """Send keepalive with optional usage statistics"""
        if not self.server_id:
            validation = self.validate()
            if not validation.get("valid"):
                return validation

        payload = {
            "product": self.product,
            "server_id": self.server_id
        }

        if usage_data:
            payload.update(usage_data)

        response = self.session.post(
            f"{self.base_url}/api/v2/keepalive",
            json=payload
        )

        return response.json()

# Usage example
def requires_feature(feature_name):
    """Decorator to gate functionality behind license features"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not AVAILABLE_FEATURES.get(feature_name, False):
                raise FeatureNotAvailableError(f"Feature '{feature_name}' requires upgrade")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@requires_feature("advanced_feature")
def advanced_functionality():
    """This function only works with professional+ licenses"""
    pass
```

#### Go Client Example

```go
package license

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

type Client struct {
    LicenseKey string
    Product    string
    BaseURL    string
    ServerID   string
    HTTPClient *http.Client
}

type ValidationResponse struct {
    Valid     bool   `json:"valid"`
    Customer  string `json:"customer"`
    Tier      string `json:"tier"`
    Features  []Feature `json:"features"`
    Metadata  struct {
        ServerID string `json:"server_id"`
    } `json:"metadata"`
}

type Feature struct {
    Name     string `json:"name"`
    Entitled bool   `json:"entitled"`
}

func NewClient(licenseKey, product string) *Client {
    return &Client{
        LicenseKey: licenseKey,
        Product:    product,
        BaseURL:    "https://license.penguintech.io",
        HTTPClient: &http.Client{Timeout: 30 * time.Second},
    }
}

func (c *Client) Validate() (*ValidationResponse, error) {
    payload := map[string]string{"product": c.Product}

    resp, err := c.makeRequest("POST", "/api/v2/validate", payload)
    if err != nil {
        return nil, err
    }

    var validation ValidationResponse
    if err := json.Unmarshal(resp, &validation); err != nil {
        return nil, err
    }

    if validation.Valid {
        c.ServerID = validation.Metadata.ServerID
    }

    return &validation, nil
}

func (c *Client) CheckFeature(feature string) (bool, error) {
    payload := map[string]string{
        "product": c.Product,
        "feature": feature,
    }

    resp, err := c.makeRequest("POST", "/api/v2/features", payload)
    if err != nil {
        return false, err
    }

    var response struct {
        Features []Feature `json:"features"`
    }

    if err := json.Unmarshal(resp, &response); err != nil {
        return false, err
    }

    if len(response.Features) > 0 {
        return response.Features[0].Entitled, nil
    }

    return false, nil
}

func (c *Client) makeRequest(method, endpoint string, payload interface{}) ([]byte, error) {
    jsonData, err := json.Marshal(payload)
    if err != nil {
        return nil, err
    }

    req, err := http.NewRequest(method, c.BaseURL+endpoint, bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }

    req.Header.Set("Authorization", "Bearer "+c.LicenseKey)
    req.Header.Set("Content-Type", "application/json")

    resp, err := c.HTTPClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var buf bytes.Buffer
    _, err = buf.ReadFrom(resp.Body)
    if err != nil {
        return nil, err
    }

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("API request failed: %d", resp.StatusCode)
    }

    return buf.Bytes(), nil
}
```

### Environment Variables for License Integration

```bash
# License Server Configuration
LICENSE_KEY=PENG-XXXX-XXXX-XXXX-XXXX-ABCD
LICENSE_SERVER_URL=https://license.penguintech.io
PRODUCT_NAME=your-product-identifier

# Optional: Custom License Server (for testing/development)
LICENSE_SERVER_URL=https://license-dev.penguintech.io
```

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
- Security scanning integration
- Performance regression testing

### Build Pipeline
- **Multi-architecture Docker builds** (amd64/arm64) using separate parallel workflows
- **Debian-slim base images** for all container builds to minimize size and attack surface
- **Parallel workflow execution** to minimize total build time without removing functionality
- **Optimized build times**: Prioritize speed while maintaining full functionality
- Dependency caching for faster builds
- Artifact management and versioning
- Container registry integration
- Build optimization and layer caching

### Deployment Pipeline
- Environment-specific deployment configs
- Blue-green deployment support
- Rollback capabilities
- Health check validation
- Automated database migrations

### Quality Gates
- Required code review process
- Automated testing requirements
- Security scan pass requirements
- Performance benchmark validation
- Documentation update verification

## Critical Development Rules

### Git Workflow
- **NEVER commit automatically** unless explicitly requested by the user
- **NEVER push to remote repositories** under any circumstances
- **ONLY commit when explicitly asked** - never assume commit permission
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

### Docker Build Standards
```bash
# Go builds within containers (using debian-slim)
docker run --rm -v $(pwd):/app -w /app golang:1.23-slim go build -o bin/app
docker build -t app:latest .

# Python builds within containers (using debian-slim)
# Use Python 3.12 for py4web applications due to py4web compatibility issues with 3.13
docker run --rm -v $(pwd):/app -w /app python:3.12-slim pip install -r requirements.txt
docker build -t web:latest .

# Use multi-stage builds with debian-slim for optimized production images
FROM golang:1.23-slim AS builder
FROM debian:stable-slim AS runtime

FROM python:3.12-slim AS builder
FROM debian:stable-slim AS runtime
```

### GitHub Actions Multi-Arch Build Strategy
```yaml
# Single workflow with multi-arch builds for each container
name: Build Containers
jobs:
  build-app:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v4
        with:
          platforms: linux/amd64,linux/arm64
          context: ./apps/app
          file: ./apps/app/Dockerfile

  build-manager:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v4
        with:
          platforms: linux/amd64,linux/arm64
          context: ./apps/manager
          file: ./apps/manager/Dockerfile

# Separate parallel workflows for each container type (app, manager, etc.)
# Each workflow builds multi-arch for that specific container
# Minimize build time through parallel container builds and caching
```

### Code Quality
- Follow language-specific style guides
- Comprehensive test coverage (80%+ target)
- No hardcoded secrets or credentials
- Proper error handling and logging
- Security-first development approach

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

### Documentation
- **README.md**: Keep as overview and pointer to comprehensive docs/ folder
- **docs/ folder**: Create comprehensive documentation for all aspects
- **RELEASE_NOTES.md**: Maintain in docs/ folder, prepend new version releases to top
- Update CLAUDE.md when adding significant context
- API documentation must be comprehensive
- Architecture decisions should be documented
- Security procedures must be documented

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
- **py4web primary**: Use py4web for ALL application web structures (sales/docs websites exempt)
- **Health endpoints**: ALL applications must implement `/healthz` endpoint
- **Metrics endpoints**: ALL applications must implement Prometheus metrics endpoint using py4web

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
- **PostgreSQL default**: Default to PostgreSQL with non-root user/password and dedicated database
- **PyDAL usage**: Only use PyDAL for databases with full PyDAL support
- **Redis/Valkey**: Utilize Redis/Valkey with optional TLS and authentication where appropriate

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
- **Each project MUST have two dedicated websites**:
  - Marketing/Sales website (Node.js based)
  - Documentation website (Markdown based)
- **Website Design Preferences**:
  - **Multi-page design preferred** - avoid single-page applications for marketing sites
  - **Modern aesthetic** with clean, professional appearance
  - **Not overly bright** - use subtle, sophisticated color schemes
  - **Gradient usage encouraged** - subtle gradients for visual depth and modern appeal
  - **Responsive design** - must work seamlessly across all device sizes
  - **Performance focused** - fast loading times and optimized assets
- **Website Repository Integration**:
  - Add `github.com/penguintechinc/website` as a sparse checkout submodule
  - Only include the project's specific website folders in the sparse checkout
  - Folder naming convention:
    - `{app_name}/` - Marketing and sales website
    - `{app_name}-docs/` - Documentation website
- **Sparse Submodule Setup**:
  ```bash
  # First, check if folders exist in the website repo and create if needed
  git clone https://github.com/penguintechinc/website.git temp-website
  cd temp-website

  # Create project folders if they don't exist
  mkdir -p {app_name}/
  mkdir -p {app_name}-docs/

  # Create initial template files if folders are empty
  if [ ! -f {app_name}/package.json ]; then
    # Initialize Node.js marketing website
    echo "Creating initial marketing website structure..."
    # Add basic package.json, index.js, etc.
  fi

  if [ ! -f {app_name}-docs/README.md ]; then
    # Initialize documentation website
    echo "Creating initial docs website structure..."
    # Add basic markdown structure
  fi

  # Commit and push if changes were made
  git add .
  git commit -m "Initialize website folders for {app_name}"
  git push origin main
  cd .. && rm -rf temp-website

  # Now add sparse submodule for website integration
  git submodule add --name websites https://github.com/penguintechinc/website.git websites
  git config -f .gitmodules submodule.websites.sparse-checkout true

  # Configure sparse checkout to only include project folders
  echo "{app_name}/" > .git/modules/websites/info/sparse-checkout
  echo "{app_name}-docs/" >> .git/modules/websites/info/sparse-checkout

  # Initialize sparse checkout
  git submodule update --init websites
  ```
- **Website Maintenance**: Both websites must be kept current with project releases and feature updates
- **First-Time Setup**: If project folders don't exist in the website repo, they must be created and initialized with basic templates before setting up the sparse submodule

## Common Integration Patterns

### License-Gated Features
```python
# Python feature gating
from shared.licensing import license_client, requires_feature

@requires_feature("advanced_analytics")
def generate_advanced_report():
    """This feature requires professional+ license"""
    return advanced_analytics.generate_report()

# Startup validation
def initialize_application():
    client = license_client.get_client()
    validation = client.validate()
    if not validation.get("valid"):
        logger.error(f"License validation failed: {validation.get('message')}")
        sys.exit(1)

    logger.info(f"License valid for {validation['customer']} ({validation['tier']})")
    return validation
```

```go
// Go feature gating
package main

import (
    "log"
    "os"
    "your-project/internal/license"
)

func main() {
    client := license.NewClient(os.Getenv("LICENSE_KEY"), "your-product")

    validation, err := client.Validate()
    if err != nil || !validation.Valid {
        log.Fatal("License validation failed")
    }

    log.Printf("License valid for %s (%s)", validation.Customer, validation.Tier)

    // Check features
    if hasAdvanced, _ := client.CheckFeature("advanced_feature"); hasAdvanced {
        log.Println("Advanced features enabled")
    }
}
```

### Database Integration
```python
# Python with PyDAL
from pydal import DAL, Field

db = DAL('postgresql://user:pass@host/db')
db.define_table('users',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
    Field('email', 'string', requires=IS_EMAIL()),
    migrate=True, fake_migrate=False)
```

```go
// Go with GORM
import "gorm.io/gorm"

type User struct {
    ID    uint   `gorm:"primaryKey"`
    Name  string `gorm:"not null"`
    Email string `gorm:"uniqueIndex;not null"`
}
```

### API Development
```python
# Python with py4web
from py4web import action, request, response
from py4web.utils.cors import CORS

@action('api/users', method=['GET', 'POST'])
@CORS()
def api_users():
    if request.method == 'GET':
        return {'users': db(db.users).select().as_list()}
    # Handle POST...
```

```go
// Go with Gin
func setupRoutes() *gin.Engine {
    r := gin.Default()
    r.Use(cors.Default())

    v1 := r.Group("/api/v1")
    {
        v1.GET("/users", getUsers)
        v1.POST("/users", createUser)
    }
    return r
}
```

### Monitoring Integration
```python
# Python metrics
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@action('metrics')
def metrics():
    return generate_latest(), {'Content-Type': 'text/plain'}
```

```go
// Go metrics
import "github.com/prometheus/client_golang/prometheus"

var (
    requestCount = prometheus.NewCounterVec(
        prometheus.CounterOpts{Name: "http_requests_total"},
        []string{"method", "endpoint"})
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{Name: "http_request_duration_seconds"},
        []string{"method", "endpoint"})
)
```

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

**Template Version**: 1.0.0
**Last Updated**: 2025-09-23
**Maintained by**: Penguin Tech Inc
**License Server**: https://license.penguintech.io

*This template provides a production-ready foundation for enterprise software development with comprehensive tooling, security, operational capabilities, and integrated licensing management.*