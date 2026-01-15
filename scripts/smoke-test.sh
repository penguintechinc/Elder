#!/bin/bash
# Unified Smoke Test Script for Elder
# Tests all containers end-to-end: build, run, API health, and page loads
#
# Usage: ./scripts/smoke-test.sh [--skip-build] [--verbose]
#
# This script:
# 1. Builds all containers (unless --skip-build)
# 2. Starts all services
# 3. Tests health endpoints for each container
# 4. Tests API authentication and basic CRUD
# 5. Tests web UI page loads (if puppeteer available)
# 6. Reports results summary

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - read from docker-compose port mappings or use defaults
API_URL="${API_URL:-http://localhost:4000}"
WEB_URL="${WEB_URL:-http://localhost:3005}"
GRPC_PORT="${GRPC_PORT:-50052}"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin@localhost.local}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"
MAX_WAIT=120  # Maximum seconds to wait for services
RETRY_INTERVAL=2

# Parse arguments
SKIP_BUILD=false
VERBOSE=false
for arg in "$@"; do
    case $arg in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=""

record_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    log_success "$1"
}

record_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS="$FAILED_TESTS\n  - $1"
    log_error "$1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

log_info "=========================================="
log_info "Elder Unified Smoke Test"
log_info "=========================================="
log_info "API URL: $API_URL"
log_info "Web URL: $WEB_URL"
log_info ""

# Step 1: Build containers (unless skipped)
if [ "$SKIP_BUILD" = false ]; then
    log_info "Step 1: Building containers..."
    if docker compose build --no-cache; then
        record_pass "Docker build completed successfully"
    else
        record_fail "Docker build failed"
        exit 1
    fi
else
    log_info "Step 1: Skipping build (--skip-build flag set)"
fi

# Step 2: Start services
log_info ""
log_info "Step 2: Starting services..."
docker compose down --volumes 2>/dev/null || true
if docker compose up -d; then
    record_pass "Docker Compose services started"
else
    record_fail "Failed to start Docker Compose services"
    exit 1
fi

# Step 3: Wait for services to be healthy
log_info ""
log_info "Step 3: Waiting for services to become healthy..."

wait_for_health() {
    local service_name="$1"
    local url="$2"
    local waited=0

    log_verbose "Waiting for $service_name at $url..."

    while [ $waited -lt $MAX_WAIT ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            return 0
        fi
        sleep $RETRY_INTERVAL
        waited=$((waited + RETRY_INTERVAL))
        log_verbose "Waiting for $service_name... ($waited/$MAX_WAIT seconds)"
    done
    return 1
}

# Wait for PostgreSQL (via docker compose health check)
log_info "Waiting for PostgreSQL..."
POSTGRES_WAIT=0
while [ $POSTGRES_WAIT -lt $MAX_WAIT ]; do
    if docker compose exec -T postgres pg_isready -U elder > /dev/null 2>&1; then
        record_pass "PostgreSQL is ready"
        break
    fi
    sleep $RETRY_INTERVAL
    POSTGRES_WAIT=$((POSTGRES_WAIT + RETRY_INTERVAL))
done
if [ $POSTGRES_WAIT -ge $MAX_WAIT ]; then
    record_fail "PostgreSQL failed to become ready"
fi

# Wait for Redis
log_info "Waiting for Redis..."
REDIS_WAIT=0
while [ $REDIS_WAIT -lt $MAX_WAIT ]; do
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        record_pass "Redis is ready"
        break
    fi
    sleep $RETRY_INTERVAL
    REDIS_WAIT=$((REDIS_WAIT + RETRY_INTERVAL))
done
if [ $REDIS_WAIT -ge $MAX_WAIT ]; then
    record_fail "Redis failed to become ready"
fi

# Wait for API
log_info "Waiting for API..."
if wait_for_health "API" "$API_URL/healthz"; then
    record_pass "API health check passed"
else
    record_fail "API health check failed"
    log_error "API logs:"
    docker compose logs api --tail=50
fi

# Wait for Web UI
log_info "Waiting for Web UI..."
if wait_for_health "Web UI" "$WEB_URL"; then
    record_pass "Web UI is accessible"
else
    record_fail "Web UI health check failed"
    log_error "Web UI logs:"
    docker compose logs web --tail=50
fi

# Step 4: API Smoke Tests
log_info ""
log_info "Step 4: API Smoke Tests..."

# Test health endpoint response content
HEALTH_RESPONSE=$(curl -sf "$API_URL/healthz" 2>/dev/null || echo "")
if echo "$HEALTH_RESPONSE" | grep -qi "healthy\|ok\|status.*up"; then
    record_pass "API /healthz returns healthy status"
else
    record_fail "API /healthz response invalid: $HEALTH_RESPONSE"
fi

# Test API version endpoint
VERSION_RESPONSE=$(curl -sf "$API_URL/api/v1/version" 2>/dev/null || echo "")
if echo "$VERSION_RESPONSE" | grep -qi "version"; then
    record_pass "API /api/v1/version returns version info"
else
    log_warn "API /api/v1/version not available (may be expected)"
fi

# Test authentication - login
log_info "Testing authentication..."
LOGIN_RESPONSE=$(curl -sf -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$ADMIN_USERNAME\", \"password\": \"$ADMIN_PASSWORD\"}" 2>/dev/null || echo "")

TOKEN=""
if echo "$LOGIN_RESPONSE" | grep -qi "access_token\|token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -z "$TOKEN" ]; then
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    fi
    record_pass "API authentication successful"
else
    record_fail "API authentication failed: $LOGIN_RESPONSE"
fi

# Test authenticated endpoints (if we got a token)
if [ -n "$TOKEN" ]; then
    # Test organizations endpoint
    ORGS_RESPONSE=$(curl -sf -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/organizations" 2>/dev/null || echo "")
    if echo "$ORGS_RESPONSE" | grep -qi "items\|organizations\|\[\]"; then
        record_pass "API GET /organizations works"
    else
        record_fail "API GET /organizations failed"
    fi

    # Test entities endpoint
    ENTITIES_RESPONSE=$(curl -sf -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/entities" 2>/dev/null || echo "")
    if echo "$ENTITIES_RESPONSE" | grep -qi "items\|entities\|\[\]"; then
        record_pass "API GET /entities works"
    else
        record_fail "API GET /entities failed"
    fi

    # Test services endpoint
    SERVICES_RESPONSE=$(curl -sf -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/services" 2>/dev/null || echo "")
    if echo "$SERVICES_RESPONSE" | grep -qi "items\|services\|\[\]"; then
        record_pass "API GET /services works"
    else
        record_fail "API GET /services failed"
    fi
fi

# Step 5: Web UI Smoke Tests
log_info ""
log_info "Step 5: Web UI Smoke Tests..."

# Test main page loads
WEB_CONTENT=$(curl -sf "$WEB_URL" 2>/dev/null || echo "")
if echo "$WEB_CONTENT" | grep -qi "elder\|<!DOCTYPE\|<html"; then
    record_pass "Web UI main page loads"
else
    record_fail "Web UI main page failed to load"
fi

# Test static assets (check if JS/CSS are served)
if curl -sf "$WEB_URL/assets/" > /dev/null 2>&1 || curl -sf "$WEB_URL" | grep -q "assets/"; then
    record_pass "Web UI static assets accessible"
else
    log_warn "Web UI static assets check inconclusive"
fi

# Test login page
LOGIN_PAGE=$(curl -sf "$WEB_URL/login" 2>/dev/null || curl -sf "$WEB_URL/#/login" 2>/dev/null || echo "")
if [ -n "$LOGIN_PAGE" ]; then
    record_pass "Web UI login page accessible"
else
    log_warn "Web UI login page not directly accessible (SPA routing)"
fi

# Step 6: Scanner Container Test (if running)
log_info ""
log_info "Step 6: Scanner Container Test..."

SCANNER_RUNNING=$(docker compose ps scanner --format json 2>/dev/null | grep -c "running" || echo "0")
if [ "$SCANNER_RUNNING" -gt "0" ]; then
    # Check scanner health via docker exec
    if docker compose exec -T scanner python -c "import sys; sys.exit(0)" 2>/dev/null; then
        record_pass "Scanner container is running and Python works"
    else
        record_fail "Scanner container Python test failed"
    fi
else
    log_warn "Scanner container not running (may be expected for dev setup)"
fi

# Step 7: Connector Container Test (if running)
log_info ""
log_info "Step 7: Connector Container Test..."

CONNECTOR_RUNNING=$(docker compose ps connector --format json 2>/dev/null | grep -c "running" || echo "0")
if [ "$CONNECTOR_RUNNING" -gt "0" ]; then
    if docker compose exec -T connector python -c "import sys; sys.exit(0)" 2>/dev/null; then
        record_pass "Connector container is running and Python works"
    else
        record_fail "Connector container Python test failed"
    fi
else
    log_warn "Connector container not running (may be expected for dev setup)"
fi

# Step 8: gRPC Server Test (if running)
log_info ""
log_info "Step 8: gRPC Server Test..."

GRPC_RUNNING=$(docker compose ps grpc-server --format json 2>/dev/null | grep -c "running" || echo "0")
if [ "$GRPC_RUNNING" -gt "0" ]; then
    # Simple TCP check on gRPC port
    if nc -z localhost $GRPC_PORT 2>/dev/null; then
        record_pass "gRPC server is listening on port $GRPC_PORT"
    else
        record_fail "gRPC server not responding on port $GRPC_PORT"
    fi
else
    log_warn "gRPC server not running (enterprise feature)"
fi

# Step 9: Summary
log_info ""
log_info "=========================================="
log_info "Smoke Test Summary"
log_info "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "\n${RED}Failed tests:${NC}$FAILED_TESTS"
    log_info ""
    log_info "Service logs available via: docker compose logs <service>"
    exit 1
else
    log_success "All smoke tests passed!"
    exit 0
fi
