# Elder API Testing Guide

Quick guide for testing the Elder API locally.

## Prerequisites

```bash
# Ensure cluster is running
docker-compose ps

# All services should show "Up" or "Up (healthy)"
```

## Quick Test

```bash
# Health check
curl http://localhost:5000/healthz

# Expected output:
# {"service":"elder","status":"healthy"}
```

## API Authentication

### Login
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "Bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@localhost",
    "is_superuser": true
  }
}
```

### Using the Token

Save the access token and use it in subsequent requests:

```bash
# Save token to variable
export TOKEN="<your-access-token-here>"

# Or get it dynamically (in a script)
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')
```

## Testing Organizations

### List Organizations
```bash
curl http://localhost:5000/api/v1/organizations \
  -H "Authorization: Bearer $TOKEN"
```

### Create Organization
```bash
curl -X POST http://localhost:5000/api/v1/organizations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering",
    "description": "Engineering department",
    "parent_id": null,
    "attributes": {
      "cost_center": "ENG-001",
      "region": "us-east-1"
    }
  }'
```

### Get Organization
```bash
curl http://localhost:5000/api/v1/organizations/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Update Organization
```bash
curl -X PATCH http://localhost:5000/api/v1/organizations/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "attributes": {"region": "us-west-2"}
  }'
```

### Delete Organization
```bash
curl -X DELETE http://localhost:5000/api/v1/organizations/1 \
  -H "Authorization: Bearer $TOKEN"
```

## Testing Entities

### List Entities
```bash
curl http://localhost:5000/api/v1/entities \
  -H "Authorization: Bearer $TOKEN"
```

### Create Entity
```bash
curl -X POST http://localhost:5000/api/v1/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server-01",
    "description": "Primary web server",
    "entity_type": "compute",
    "organization_id": 1,
    "attributes": {
      "hostname": "web-01.example.com",
      "ip_address": "10.0.1.5",
      "os": "Ubuntu 22.04 LTS",
      "cpu_cores": 4,
      "memory_gb": 16,
      "disk_gb": 100
    }
  }'
```

### Get Entity
```bash
curl http://localhost:5000/api/v1/entities/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Update Entity
```bash
curl -X PATCH http://localhost:5000/api/v1/entities/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "attributes": {"status": "active"}
  }'
```

## Testing Dependencies

### Create Dependency
```bash
# Entity 1 depends on Entity 2
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

### List Dependencies
```bash
curl http://localhost:5000/api/v1/dependencies \
  -H "Authorization: Bearer $TOKEN"
```

### Get Entity Dependencies
```bash
# Get all dependencies for entity 1
curl "http://localhost:5000/api/v1/dependencies?source_entity_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

## Testing Graph Analysis

### Analyze Organization Graph
```bash
curl "http://localhost:5000/api/v1/graph/analyze?organization_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

**Response includes:**
- Total entities and dependencies
- Entities by type breakdown
- Graph metrics (density, is_acyclic)
- Critical nodes

### Get Full Graph
```bash
curl "http://localhost:5000/api/v1/graph?organization_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

### Find Path Between Entities
```bash
curl "http://localhost:5000/api/v1/graph/path?source_id=1&target_id=5" \
  -H "Authorization: Bearer $TOKEN"
```

## Testing Public Lookup

The lookup endpoint doesn't require authentication:

```bash
# Lookup entity by ID
curl http://localhost:5000/lookup/1

# Batch lookup
curl -X POST http://localhost:5000/lookup/batch \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3, 4, 5]}'
```

## Testing User Management

### List Users
```bash
curl http://localhost:5000/api/v1/identities \
  -H "Authorization: Bearer $TOKEN"
```

### Create User
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePassword123",
    "full_name": "John Doe"
  }'
```

### Get Current User
```bash
curl http://localhost:5000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Change Password
```bash
curl -X POST http://localhost:5000/api/v1/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "admin123",
    "new_password": "NewPassword123"
  }'
```

## Troubleshooting

### "Internal Server Error" when creating resources

If you get 500 errors, the database connection may be in a bad state. Restart the API:

```bash
docker-compose restart api
sleep 3
curl http://localhost:5000/healthz
```

### "Authentication required"

Make sure your token is still valid (tokens expire after 1 hour):

```bash
# Get a fresh token
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')
```

### Check API logs

```bash
docker-compose logs -f api
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Connect to database directly
docker-compose exec postgres psql -U elder -d elder
```

## Complete Test Script

Save this as `test-complete.sh`:

```bash
#!/bin/bash
set -e

echo "=== Elder API Complete Test ==="
echo ""

# Login
echo "1. Logging in..."
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')
echo "✓ Logged in successfully"
echo ""

# Create Organization
echo "2. Creating organization..."
ORG=$(curl -s -X POST http://localhost:5000/api/v1/organizations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Org","description":"Test"}')
ORG_ID=$(echo "$ORG" | jq -r '.id')
echo "✓ Created organization ID: $ORG_ID"
echo ""

# Create Entities
echo "3. Creating entities..."
WEB=$(curl -s -X POST http://localhost:5000/api/v1/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"web-server\",\"entity_type\":\"compute\",\"organization_id\":$ORG_ID}")
WEB_ID=$(echo "$WEB" | jq -r '.id')
echo "✓ Created web server ID: $WEB_ID"

DB=$(curl -s -X POST http://localhost:5000/api/v1/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"database\",\"entity_type\":\"database\",\"organization_id\":$ORG_ID}")
DB_ID=$(echo "$DB" | jq -r '.id')
echo "✓ Created database ID: $DB_ID"
echo ""

# Create Dependency
echo "4. Creating dependency..."
curl -s -X POST http://localhost:5000/api/v1/dependencies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source_entity_id\":$WEB_ID,\"target_entity_id\":$DB_ID,\"dependency_type\":\"runtime\"}" > /dev/null
echo "✓ Created dependency: web-server -> database"
echo ""

# Analyze Graph
echo "5. Analyzing graph..."
ANALYSIS=$(curl -s "http://localhost:5000/api/v1/graph/analyze?organization_id=$ORG_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "$ANALYSIS" | jq '{entities: .basic_stats.total_entities, dependencies: .basic_stats.total_dependencies}'
echo ""

echo "=== All tests passed! ==="
```

Run it:
```bash
chmod +x test-complete.sh
./test-complete.sh
```

## Metrics and Monitoring

### Prometheus Metrics
```bash
curl http://localhost:5000/metrics
```

### Grafana Dashboards
Open http://localhost:3001 in your browser
- Username: admin
- Password: admin

## API Documentation

For full API documentation, see:
- Swagger/OpenAPI: Check if `/docs` or `/api/docs` is configured
- API Reference: See `docs/api/` folder
- Database Schema: See `docs/DATABASE.md`

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| API/Web UI | admin | admin123 |
| Grafana | admin | admin |
| PostgreSQL | elder | elder_dev_password |
