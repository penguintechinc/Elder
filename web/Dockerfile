# Build stage
FROM node:18-slim AS builder

# Build arguments for Vite
ARG VITE_API_URL=http://localhost:4000
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

# Copy package.json only (not lock file) for multi-arch compatibility
COPY package.json ./

# Install dependencies fresh for current architecture
# This works around npm bug https://github.com/npm/cli/issues/4828 where
# optional platform-specific packages (rollup, esbuild, lightningcss) fail
# when package-lock.json was generated on a different architecture
RUN npm install --ignore-scripts && \
    npm rebuild esbuild

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
