# Elder Usage Guide

Quick reference guide for using Elder infrastructure tracking platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Usage](#basic-usage)
- [Docker Compose](#docker-compose)
- [Kubernetes](#kubernetes)
- [Environment Variables](#environment-variables)
- [Common Tasks](#common-tasks)

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/penguintechinc/elder.git
cd elder

# Configure environment
cp .env.example .env
nano .env

# Start services
docker-compose up -d
```

### First Steps

1. **Access Web UI**: http://localhost:3000
2. **Login**: Use admin credentials from `.env`
3. **Create Organization**: Click "Organizations" → "New"
4. **Add Entity**: Click "Entities" → "New"

## Basic Usage

### Via Web UI

**Create an Organization:**
1. Navigate to "Organizations"
2. Click "New Organization"
3. Enter name and description
4. Select parent (optional)
5. Click "Create"

**Add an Entity:**
1. Navigate to "Entities"
2. Click "New Entity"
3. Select entity type (compute, network, etc.)
4. Choose organization
5. Fill in details
6. Click "Create"

**Create Dependency:**
1. Open an entity detail page
2. Click "Add Dependency"
3. Select target entity
4. Choose dependency type
5. Click "Save"

**View Graph:**
1. Navigate to "Graph"
2. Select organization or entity
3. Interact with visualization:
   - Zoom: Scroll wheel
   - Pan: Click and drag
   - Select: Click nodes
   - Details: Double-click nodes

### Via API

**Create Organization:**
```bash
curl -X POST http://localhost:5000/api/v1/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production",
    "description": "Production infrastructure"
  }'
```

**Create Entity:**
```bash
curl -X POST http://localhost:5000/api/v1/entities \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server-01",
    "entity_type": "compute",
    "organization_id": 1,
    "attributes": {
      "ip": "10.0.1.10",
      "os": "Ubuntu 22.04"
    }
  }'
```

**Create Dependency:**
```bash
curl -X POST http://localhost:5000/api/v1/dependencies \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_id": 10,
    "target_entity_id": 20,
    "dependency_type": "network"
  }'
```

**Get Graph Data:**
```bash
curl http://localhost:5000/api/v1/graph/organization/1
```

## Docker Compose

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis api web

# View logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f api
```

### Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop api

# Stop and remove containers
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v
```

### Service Status

```bash
# Check running services
docker-compose ps

# View resource usage
docker stats
```

## Kubernetes

### Helm Installation

```bash
# Add repository
helm repo add elder https://charts.penguintech.io/elder

# Install
helm install elder elder/elder \
  --namespace elder \
  --create-namespace

# Check status
kubectl get pods -n elder
```

### Kubectl Management

```bash
# View pods
kubectl get pods -n elder

# View services
kubectl get svc -n elder

# View logs
kubectl logs -f deployment/elder-api -n elder

# Execute command
kubectl exec -it deployment/elder-api -n elder -- bash
```

### Scaling

```bash
# Scale API
kubectl scale deployment elder-api --replicas=3 -n elder

# Autoscale
kubectl autoscale deployment elder-api \
  --min=2 --max=10 --cpu-percent=70 -n elder
```

## Environment Variables

### Database Configuration

```bash
POSTGRES_DB=elder              # Database name
POSTGRES_USER=elder            # Database user
POSTGRES_PASSWORD=<password>   # Database password
POSTGRES_PORT=5432             # Database port
```

### Redis Configuration

```bash
REDIS_PASSWORD=<password>      # Redis password
REDIS_PORT=6379                # Redis port
REDIS_URL=redis://:password@redis:6379/0
```

### Application Configuration

```bash
FLASK_ENV=production           # Environment (development/production)
SECRET_KEY=<random-key>        # Application secret key
LOG_LEVEL=INFO                 # Logging level
API_PORT=5000                  # API server port
WEB_PORT=3000                  # Web UI port
```

### Admin User

```bash
ADMIN_USERNAME=admin           # Admin username
ADMIN_PASSWORD=<password>      # Admin password
ADMIN_EMAIL=admin@example.com  # Admin email
```

### License Configuration (Optional)

```bash
LICENSE_KEY=PENG-XXXX-...      # PenguinTech license key
PRODUCT_NAME=elder             # Product identifier
LICENSE_SERVER_URL=https://license.penguintech.io
```

### Connector Service (Optional)

```bash
# AWS
AWS_ENABLED=true
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_REGIONS=us-east-1,us-west-2

# GCP
GCP_ENABLED=true
GCP_PROJECT_ID=<project>
GCP_CREDENTIALS_PATH=/app/credentials/gcp.json

# Google Workspace
GOOGLE_WORKSPACE_ENABLED=true
GOOGLE_WORKSPACE_ADMIN_EMAIL=admin@example.com
GOOGLE_WORKSPACE_CREDENTIALS_PATH=/app/credentials/workspace.json

# LDAP
LDAP_ENABLED=true
LDAP_SERVER=ldap.example.com
LDAP_PORT=389
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BASE_DN=dc=example,dc=com
```

## Common Tasks

### Database Backups

**Create Backup:**
```bash
docker-compose exec postgres pg_dump -U elder elder > backup.sql
```

**Restore Backup:**
```bash
docker-compose exec -T postgres psql -U elder elder < backup.sql
```

**Automated Backups:**
```bash
# Add to crontab
0 2 * * * cd /path/to/elder && docker-compose exec postgres pg_dump -U elder elder > backups/elder-$(date +\%Y\%m\%d).sql
```

### Database Migrations

**Run Migrations:**
```bash
docker-compose exec api alembic upgrade head
```

**Check Status:**
```bash
docker-compose exec api alembic current
```

**Rollback:**
```bash
docker-compose exec api alembic downgrade -1
```

### View Logs

**All Services:**
```bash
docker-compose logs -f
```

**Specific Service:**
```bash
docker-compose logs -f api
docker-compose logs -f connector
docker-compose logs -f web
```

**Last N Lines:**
```bash
docker-compose logs --tail=100 api
```

**Since Timestamp:**
```bash
docker-compose logs --since="2025-10-25T10:00:00" api
```

### Restart Services

**All Services:**
```bash
docker-compose restart
```

**Specific Service:**
```bash
docker-compose restart api
```

**Hard Restart (rebuild):**
```bash
docker-compose up -d --build api
```

### Health Checks

**API Health:**
```bash
curl http://localhost:5000/healthz
```

**Database Health:**
```bash
docker-compose exec postgres pg_isready
```

**Redis Health:**
```bash
docker-compose exec redis redis-cli ping
```

**All Services:**
```bash
docker-compose ps
```

### Monitoring

**Prometheus:**
- URL: http://localhost:9090
- Metrics: http://localhost:5000/metrics

**Grafana:**
- URL: http://localhost:3001
- Default: admin/admin (change on first login)

### Connector Service

**Start Sync:**
```bash
# Automatically syncs based on intervals
# Or restart to force immediate sync
docker-compose restart connector
```

**View Sync Status:**
```bash
curl http://localhost:8000/status
```

**Test Connectivity:**
```bash
docker-compose exec connector \
  python3 /app/apps/connector/test_connectivity.py
```

## Storage & Persistence

### Required Volumes

```yaml
volumes:
  postgres_data:    # PostgreSQL data
  redis_data:       # Redis data
  grafana_data:     # Grafana dashboards
  prometheus_data:  # Prometheus metrics
```

### Backup Volumes

```bash
# Backup PostgreSQL volume
docker run --rm \
  -v elder_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz -C /data .

# Restore PostgreSQL volume
docker run --rm \
  -v elder_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /data
```

### Clean Up Volumes

```bash
# Remove all volumes (WARNING: deletes all data!)
docker-compose down -v

# Remove specific volume
docker volume rm elder_postgres_data
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs <service>

# Check if port is in use
lsof -i :<port>

# Restart service
docker-compose restart <service>
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U elder -d elder

# Reset database
docker-compose restart postgres
```

### API Errors

```bash
# View API logs
docker-compose logs api

# Check environment variables
docker-compose exec api env

# Restart API
docker-compose restart api
```

### Web UI Not Loading

```bash
# Check web service
docker-compose ps web

# Check API connectivity
curl http://localhost:5000/healthz

# View web logs
docker-compose logs web
```

## Further Reading

- [Deployment Guide](deployment/README.md) - Production deployment
- [Development Guide](development/README.md) - Development setup
- [API Documentation](api/README.md) - REST API reference
- [Connector Guide](connector/README.md) - Multi-cloud sync
- [Architecture](architecture/README.md) - System architecture
