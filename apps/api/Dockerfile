# Elder Flask API Dockerfile
# Multi-stage build with debian-slim base for optimal size and security
# Python 3.12 for performance optimizations (dataclasses with slots, asyncio TaskGroups)

# Builder stage
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libsasl2-2 \
    libldap2 \
    libxml2 \
    libxmlsec1-openssl \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 elder

# Copy Python dependencies from builder to elder user
COPY --from=builder /root/.local /home/elder/.local
RUN chown -R elder:elder /home/elder/.local

# Create instance directory for PyDAL migrations (before switching to elder user)
RUN mkdir -p /app/instance && chown -R elder:elder /app/instance

# Switch to non-root user
USER elder

# Make sure scripts in .local are usable
ENV PATH=/home/elder/.local/bin:$PATH

# Copy application code
COPY --chown=elder:elder apps /app/apps
COPY --chown=elder:elder shared /app/shared
COPY --chown=elder:elder requirements.txt /app/

# Expose ports
EXPOSE 5000 50051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/healthz || exit 1

# Set environment variables
ENV FLASK_APP=apps.api.main:create_app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run application with uvicorn ASGI server for async Flask support
CMD ["uvicorn", \
     "apps.api.main:create_app", \
     "--factory", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--http", "h11", \
     "--access-log", \
     "--log-level", "info"]
