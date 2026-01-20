#!/bin/bash
# Deploy Elder API to registry-dal2.penguintech.io
# Builds amd64-only image and pushes to private registry

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Configuration
REGISTRY="registry-dal2.penguintech.io"
IMAGE_NAME="elder-api"
VERSION_FILE=".version"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Read version from .version file
if [ ! -f "$VERSION_FILE" ]; then
    log_error "Version file not found: $VERSION_FILE"
    exit 1
fi

VERSION=$(cat "$VERSION_FILE" | tr -d '\n')
log_info "Version: $VERSION"

# Build image for amd64 (native architecture build)
log_info "Building Docker image..."
docker build \
    --file apps/api/Dockerfile \
    --tag "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
    --tag "${REGISTRY}/${IMAGE_NAME}:latest" \
    .

log_success "Image built successfully"

# Push to registry
log_info "Pushing image to ${REGISTRY}..."
docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker push "${REGISTRY}/${IMAGE_NAME}:latest"

log_success "Image pushed successfully"
log_info ""
log_info "Deployment images:"
log_info "  - ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
log_info "  - ${REGISTRY}/${IMAGE_NAME}:latest"
log_info ""
log_info "Next steps:"
log_info "  kubectl set image deployment/elder-api api=${REGISTRY}/${IMAGE_NAME}:${VERSION} -n waddleperf"
log_info "  kubectl rollout status deployment/elder-api -n waddleperf"
