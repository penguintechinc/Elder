# Elder API Documentation

Overview of Elder's API layer and integration interfaces.

## APIs Available

Elder provides multiple API interfaces for different use cases:

### REST API (v1)
Full-featured RESTful HTTP API for all Elder functionality.

📖 **[Complete REST API Reference](API.md)**

- **Base URL**: `http://localhost:5000/api/v1`
- **Authentication**: Bearer tokens, SAML, OAuth2, LDAP
- **Format**: JSON
- **Documentation**: OpenAPI 3.0

**Key Endpoints:**
- Organizations - `/api/v1/organizations`
- Entities - `/api/v1/entities`
- Dependencies - `/api/v1/dependencies`
- Issues - `/api/v1/issues`
- Graph - `/api/v1/graph`

### gRPC API (Enterprise)
High-performance gRPC API for machine-to-machine communication.

📖 **[gRPC Documentation](../grpc/README.md)**

- **Protocol**: gRPC/Protobuf
- **Features**: Streaming, type-safe
- **License**: Enterprise tier only

## Quick Start

### REST API Example

```bash
# List all entities
curl http://localhost:5000/api/v1/entities

# Create an entity
curl -X POST http://localhost:5000/api/v1/entities \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web-server-01",
    "entity_type": "compute",
    "organization_id": 1,
    "attributes": {"ip": "10.0.1.10"}
  }'

# Get graph visualization data
curl http://localhost:5000/api/v1/graph/organization/1
```

### Authentication

```bash
# Using Bearer token
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:5000/api/v1/entities
```

## API Features

### Core Capabilities
- ✅ Full CRUD operations for all resources
- ✅ Hierarchical organization management
- ✅ Entity relationship tracking
- ✅ GitHub-style issue management
- ✅ Fine-grained resource roles
- ✅ Type-validated metadata
- ✅ Graph visualization data

### Advanced Features
- ✅ Pagination for all list endpoints
- ✅ Filtering and search
- ✅ Bulk operations
- ✅ Async operations
- ✅ WebSocket support (coming soon)
- ✅ Rate limiting
- ✅ API versioning

## Response Format

### Success
```json
{
  "id": 1,
  "name": "Example",
  "created_at": "2025-10-25T10:00:00Z"
}
```

### Error
```json
{
  "error": "Entity not found",
  "code": 404
}
```

### Pagination
```json
{
  "items": [...],
  "total": 500,
  "page": 1,
  "per_page": 50,
  "pages": 10
}
```

## API Clients

### Official Clients
- **Python**: Coming soon
- **Go**: Coming soon
- **JavaScript/TypeScript**: Coming soon

### Community Clients
- Contributions welcome!

## Rate Limits

| Tier | Limit |
|------|-------|
| Community | 100 req/15min |
| Professional | 1000 req/15min |
| Enterprise | Unlimited |

## API Versioning

- **Current**: v1 (`/api/v1`)
- **Stability**: Stable
- **Deprecation**: 6 months notice for breaking changes

## Documentation

- **[Complete REST API Reference](API.md)** - Full endpoint documentation
- **[OpenAPI Spec](http://localhost:5000/api/v1/openapi.json)** - Machine-readable spec
- **[gRPC Documentation](../grpc/README.md)** - gRPC API reference

## Testing

### API Testing Tools

```bash
# Using curl
curl http://localhost:5000/api/v1/healthz

# Using httpie
http GET http://localhost:5000/api/v1/entities

# Using Postman
# Import OpenAPI spec from /api/v1/openapi.json
```

### Test Environment

```bash
# Start test instance
docker-compose up -d api

# Run API tests
pytest tests/api/
```

## Security

- **TLS**: Required in production
- **Authentication**: Multiple methods supported
- **Authorization**: RBAC with resource-level permissions
- **Input Validation**: All endpoints validate input
- **Rate Limiting**: Protection against abuse

## Monitoring

- **Health Check**: `/healthz`
- **Metrics**: `/metrics` (Prometheus format)
- **Logging**: Structured JSON logs

## Support

- **Documentation**: This docs folder
- **Issues**: GitHub Issues
- **Community**: GitHub Discussions

## Further Reading

- [Architecture Documentation](../architecture/README.md)
- [Development Setup](../development/README.md)
- [Deployment Guide](../deployment/README.md)
