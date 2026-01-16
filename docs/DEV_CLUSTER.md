# Elder Development Cluster

Local development environment with full stack running in Docker.

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

## Service URLs

All services are accessible from your local machine:

### Core Services

| Service | URL | Purpose | Credentials |
|---------|-----|---------|-------------|
| **API Server** | http://localhost:5000 | REST API endpoints | admin / admin123 |
| **Web UI** | http://localhost:3000 | Frontend application | admin / admin123 |
| **Grafana** | http://localhost:3001 | Monitoring dashboards | admin / admin |
| **Prometheus** | http://localhost:9091 | Metrics collection | N/A |

### Databases

| Service | Connection | Credentials |
|---------|------------|-------------|
| **PostgreSQL** | localhost:5433 | elder / elder_dev_password |
| **Redis** | localhost:6382 | elder_redis_password |

### API Endpoints

**Health Check:**
```bash
curl http://localhost:5000/healthz
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Get Current User:**
```bash
# First, get a token
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Then use the token
curl http://localhost:5000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Docker Network Communication

Services communicate internally using the `elder-network` Docker network:

- API: `http://api:5000`
- PostgreSQL: `postgres:5432`
- Redis: `redis:6379`
- Prometheus: `prometheus:9090`

## Testing

### Quick API Test (Local)
```bash
./scripts/test-api.sh
```

### Full API Test (Docker Network)
```bash
./scripts/test-api-docker.sh
```

## Database Access

### Using psql
```bash
docker-compose exec postgres psql -U elder -d elder
```

### Common Queries
```sql
-- List all users
SELECT id, username, email, is_superuser, is_active FROM identities;

-- List organizations
SELECT id, name, description, parent_id FROM organizations;

-- List entities
SELECT id, name, entity_type, organization_id FROM entities;

-- Count dependencies
SELECT COUNT(*) FROM dependencies;
```

## Logs

```bash
# API logs
docker-compose logs -f api

# Database logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

## Stopping Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes (DESTRUCTIVE)
docker-compose down -v
```

## Default Admin User

Created automatically on first startup:

- **Username:** admin
- **Password:** admin123
- **Email:** admin@localhost.local
- **Role:** Superuser

## Environment Variables

All configuration is in `.env` file:

```bash
# Core
FLASK_ENV=development
API_PORT=5000

# Database
POSTGRES_DB=elder
POSTGRES_USER=elder
POSTGRES_PASSWORD=elder_dev_password
POSTGRES_PORT=5433

# Redis
REDIS_PASSWORD=elder_redis_password
REDIS_PORT=6382

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@localhost.local

# Monitoring
PROMETHEUS_PORT=9091
GRAFANA_PORT=3001
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

## API Examples

### Create Organization
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

curl -X POST http://localhost:5000/api/v1/organizations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Organization",
    "description": "Test organization",
    "attributes": {"region": "us-east-1"}
  }'
```

### Create Entity
```bash
curl -X POST http://localhost:5000/api/v1/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Web Server 01",
    "description": "Production web server",
    "entity_type": "compute",
    "organization_id": 1,
    "attributes": {
      "hostname": "web-01.example.com",
      "ip": "10.0.1.5",
      "os": "Ubuntu 22.04"
    }
  }'
```

### Create Dependency
```bash
curl -X POST http://localhost:5000/api/v1/dependencies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_entity_id": 1,
    "target_entity_id": 2,
    "dependency_type": "runtime",
    "description": "Web server depends on database"
  }'
```

### Graph Analysis
```bash
curl "http://localhost:5000/api/v1/graph/analyze?organization_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

## Metrics

Prometheus metrics are exposed at:
```bash
curl http://localhost:5000/metrics
```

View in Grafana at http://localhost:3001

## Troubleshooting

### Port Already in Use
If ports are already allocated, update `.env`:
```bash
API_PORT=5001
POSTGRES_PORT=5434
REDIS_PORT=6383
PROMETHEUS_PORT=9092
GRAFANA_PORT=3002
```

### Can't Connect to API
```bash
# Check if API is healthy
docker-compose exec api curl http://localhost:5000/healthz

# Check logs
docker-compose logs api

# Restart API
docker-compose restart api
```

### Database Issues
```bash
# Check database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Reset database (DESTRUCTIVE)
docker-compose down -v
docker-compose up -d
```

## Architecture

```
┌─────────────┐     ┌──────────────┐
│   Web UI    │────▶│  API Server  │
│ (Port 3000) │     │ (Port 5000)  │
└─────────────┘     └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼────┐    ┌─────▼─────┐  ┌─────▼──────┐
      │PostgreSQL│    │   Redis   │  │ Prometheus │
      │(Pt 5433)│    │ (Pt 6382) │  │ (Pt 9091)  │
      └─────────┘    └───────────┘  └──────┬─────┘
                                            │
                                     ┌──────▼──────┐
                                     │   Grafana   │
                                     │ (Pt 3001)   │
                                     └─────────────┘
```

## PyDAL Migration Status

✅ **Migration Complete!**

- All 9 API files migrated to PyDAL with async/await
- 4,269 lines of async/PyDAL code
- 79+ REST API endpoints functional
- 18 PyDAL tables in PostgreSQL
- Python 3.12 asyncio.TaskGroup for concurrent operations

## Next Steps

1. **Test API Endpoints**: Use the examples above or run `./scripts/test-api-docker.sh`
2. **Explore Web UI**: Visit http://localhost:3000
3. **View Metrics**: Check Grafana at http://localhost:3001
4. **Create Organizations and Entities**: Use the API examples above
5. **Build Dependency Graphs**: Use the graph endpoints to visualize relationships

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Check health: `curl http://localhost:5000/healthz`
- Review API docs: See `docs/api/` folder
- Database schema: See `docs/DATABASE.md`
