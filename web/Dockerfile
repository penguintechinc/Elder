# Build stage
FROM node:18-slim AS builder

# Build arguments for Vite
# VITE_API_URL defaults to empty string - nginx proxies /api/* to API server
# Only set VITE_API_URL for development or when API is on a different domain
ARG VITE_API_URL=
ARG VITE_BUILD_TIME
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_BUILD_TIME=$VITE_BUILD_TIME

WORKDIR /app

# Copy package files (only package.json, not lock file)
# For cross-platform builds, package-lock.json contains platform-specific optional deps
# that break ARM64 builds under QEMU emulation
COPY package.json ./

# Install dependencies fresh without lock file
# This ensures architecture-specific optional dependencies (like @rollup/rollup-linux-arm64-gnu)
# are properly resolved for the target platform
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Health check - verify nginx is serving content
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
