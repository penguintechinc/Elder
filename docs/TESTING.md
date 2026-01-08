# Testing Guide for Elder

This document outlines the testing strategy and local pre-commit checklist for the Elder project.

## Testing Strategy

### GitHub Actions CI (Automated)

The GitHub Actions CI pipeline runs on every push and pull request:

- **Code Quality**: Black, isort, flake8, mypy
- **Unit Tests**: Pytest with mocked dependencies (no external services)
- **Security Scans**: Trivy (filesystem), Semgrep, Dependabot
- **Build Tests**: Docker image builds (amd64 & arm64)
- **Web Builds**: TypeScript compilation, bundling

### Local Testing (Pre-Commit Checklist)

Run these checks **locally BEFORE committing** to catch issues early:

## Pre-Commit Checklist

### 1. Code Quality (2 min)

```bash
# Format code with Black (matches CI version 25.12.0)
docker compose exec -T api black apps/ shared/ --exclude=apps/api/grpc/generated

# Sort imports with isort (matches CI version 7.0.0)
docker compose exec -T api isort apps/ shared/ --skip apps/api/grpc/generated

# Lint with flake8
docker compose exec -T api flake8 apps/ shared/ --exclude=apps/api/grpc/generated
```

### 2. Unit Tests (5 min)

```bash
# Run unit tests (exclude integration and e2e)
docker compose exec -T api pytest tests/unit/ -v --tb=short -m "not integration and not e2e"
```

### 3. E2E Tests (10 min - Local Only)

**ONLY run locally if you have docker compose services running:**

```bash
make dev
pytest tests/e2e/ -v --tb=short
docker compose down
```

### 4. Security Checks (2 min)

```bash
safety check  # Check Python dependencies
```

### 5. Build Verification

```bash
docker compose build --no-cache api
docker compose build --no-cache web
```

## What Gets Tested Where

| Test Type | GitHub Actions | Status |
|-----------|-----------------|--------|
| Code Quality | Yes | ✅ Blocking |
| Unit Tests | Yes | ✅ Blocking |
| E2E Tests | No | ❌ Disabled |
| Integration Tests | No | ❌ Disabled |
| Container Security | No | ❌ Disabled |

## Why Tests Are Disabled in CI

- **E2E Tests**: Require full docker compose; resource-intensive
- **Integration Tests**: Using outdated SQLAlchemy (needs PyDAL rewrite)
- **Container Security**: Registry propagation issues; Trivy runs on filesystem

## Logo Issue (ARM Deployment)

**Issue**: "cannot find /elder-logo.png" on ARM/other systems

**Root Cause**: Static assets path configuration differs between architectures/environments

**Solution**: Check the following:

1. Verify logo exists in web build:
```bash
docker compose exec web ls -la /app/public/elder-logo.png
```

2. Check web Dockerfile uses correct base image for your architecture:
```bash
# For ARM:
FROM node:18-alpine

# For amd64:
FROM node:18-alpine
```

3. Check environment-specific asset paths in web app config

4. Ensure web service is built with `--no-cache`:
```bash
docker compose build --no-cache web
```
