# CI/CD Patterns and Build Standards

## Docker Build Standards

### CRITICAL: Always Use `--no-cache` for Production Rebuilds

All builds MUST use the `--no-cache` flag to prevent stale build artifacts:

```bash
# CORRECT: Always rebuild with --no-cache (using Docker Compose V2)
docker compose build --no-cache api
docker compose build --no-cache web
docker compose build --no-cache grpc-server

# WRONG: Never use cached builds for production changes
docker compose build api  # BAD - May use stale cached layers
docker compose build web  # BAD - May serve old frontend code

# Complete rebuild and restart workflow
docker compose build --no-cache api && docker compose restart api
docker compose build --no-cache web && docker compose restart web
```

### Why `--no-cache` is Mandatory

- Prevents serving stale frontend builds with old navigation/components
- Ensures Python dependency changes are properly applied
- Avoids cached intermediate layers with outdated code
- Guarantees reproducible builds across environments
- Eliminates "works on my machine" issues from layer caching

### Standard Build Commands

```bash
# Go builds within containers (using debian-slim)
docker run --rm -v $(pwd):/app -w /app golang:1.23-slim go build -o bin/app
docker build --no-cache -t app:latest .

# Python builds within containers (using debian-slim)
# Use Python 3.13+ for Flask applications
docker run --rm -v $(pwd):/app -w /app python:3.13-slim pip install -r requirements.txt
docker build --no-cache -t web:latest .

# Use multi-stage builds with debian-slim for optimized production images
FROM golang:1.23-slim AS builder
FROM debian:stable-slim AS runtime

FROM python:3.13-slim AS builder
FROM debian:stable-slim AS runtime
```

## GitHub Actions Multi-Arch Build Strategy

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

## Build Pipeline Features

- **Multi-architecture Docker builds** (amd64/arm64) using separate parallel workflows
- **Debian-slim base images** for all container builds to minimize size and attack surface
- **Parallel workflow execution** to minimize total build time without removing functionality
- **Optimized build times**: Prioritize speed while maintaining full functionality
- Dependency caching for faster builds
- Artifact management and versioning
- Container registry integration
- Build optimization and layer caching

## Deployment Pipeline

- Environment-specific deployment configs
- Blue-green deployment support
- Rollback capabilities
- Health check validation
- Automated database migrations

## Quality Gates

- Required code review process
- Automated testing requirements
- Security scan pass requirements
- Performance benchmark validation
- Documentation update verification
