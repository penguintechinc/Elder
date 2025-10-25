# Elder REST API Documentation

The Elder REST API provides comprehensive access to all Elder functionality through RESTful HTTP endpoints.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Elder supports multiple authentication methods:

- **Local Authentication**: Username/password (development)
- **API Keys**: Bearer token authentication (recommended for automation)
- **SAML/OAuth2**: Enterprise SSO (Professional/Enterprise tiers)
- **LDAP**: Directory service integration (Enterprise tier)

### Bearer Token Authentication

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:5000/api/v1/entities
```

## API Endpoints

### Organizations

Manage hierarchical organizational structures (Company → Department → Teams).

#### List Organizations
```http
GET /api/v1/organizations
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50, max: 1000)
- `parent_id` (int): Filter by parent organization ID
- `name` (string): Filter by name (partial match)

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Engineering",
      "description": "Engineering department",
      "parent_id": null,
      "ldap_dn": "ou=Engineering,dc=example,dc=com",
      "saml_group": "eng@example.com",
      "owner_identity_id": 10,
      "owner_group_id": 5,
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-10-01T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 50,
  "pages": 2
}
```

#### Create Organization
```http
POST /api/v1/organizations
```

**Request Body:**
```json
{
  "name": "Platform Team",
  "description": "Platform engineering team",
  "parent_id": 1,
  "ldap_dn": "ou=Platform,ou=Engineering,dc=example,dc=com",
  "owner_identity_id": 10
}
```

#### Get Organization
```http
GET /api/v1/organizations/{id}
```

#### Update Organization
```http
PATCH /api/v1/organizations/{id}
PUT /api/v1/organizations/{id}
```

#### Delete Organization
```http
DELETE /api/v1/organizations/{id}
```

**Note:** Cannot delete organizations with children.

#### Get Organization Children
```http
GET /api/v1/organizations/{id}/children?recursive=true
```

#### Get Organization Hierarchy
```http
GET /api/v1/organizations/{id}/hierarchy
```

**Response:**
```json
{
  "path": [/* org hierarchy from root */],
  "depth": 2,
  "hierarchy_string": "Company → Engineering → Platform Team"
}
```

---

### Entities

Track infrastructure and organizational resources.

#### Entity Types

- `datacenter` - Physical or virtual datacenters
- `vpc` - Virtual Private Clouds
- `subnet` - Network subnets
- `compute` - Servers, VMs, containers
- `network` - Load balancers, VPNs, firewalls
- `user` - Users and service accounts
- `security_issue` - Vulnerabilities and CVEs

#### List Entities
```http
GET /api/v1/entities
```

**Query Parameters:**
- `page`, `per_page` - Pagination
- `entity_type` - Filter by type
- `organization_id` - Filter by organization
- `name` - Filter by name (partial match)
- `is_active` - Filter by active status

#### Create Entity
```http
POST /api/v1/entities
```

**Request Body:**
```json
{
  "name": "web-server-01",
  "entity_type": "compute",
  "organization_id": 1,
  "description": "Production web server",
  "attributes": {
    "hostname": "web01.example.com",
    "ip": "10.0.1.10",
    "os": "Ubuntu 22.04",
    "cpu": 4,
    "memory_gb": 16
  },
  "tags": ["production", "web", "us-east-1"],
  "is_active": true
}
```

#### Get Entity
```http
GET /api/v1/entities/{id}
```

#### Update Entity
```http
PATCH /api/v1/entities/{id}
PUT /api/v1/entities/{id}
```

#### Delete Entity
```http
DELETE /api/v1/entities/{id}
```

**Note:** Cannot delete entities with dependencies.

#### Get Entity Dependencies
```http
GET /api/v1/entities/{id}/dependencies?direction=all
```

**Direction options:** `outgoing`, `incoming`, `all`

**Response:**
```json
{
  "entity_id": 10,
  "entity_name": "web-server-01",
  "depends_on": [
    {
      "id": 5,
      "target_entity_id": 20,
      "dependency_type": "network",
      "metadata": {"port": 5432}
    }
  ],
  "depended_by": [
    {
      "id": 6,
      "source_entity_id": 30,
      "dependency_type": "application",
      "metadata": {}
    }
  ]
}
```

#### Update Entity Attributes
```http
PATCH /api/v1/entities/{id}/attributes
```

**Request Body:**
```json
{
  "cpu": 8,
  "memory_gb": 32,
  "updated_date": "2025-10-25"
}
```

---

### Dependencies

Manage relationships between entities.

#### List Dependencies
```http
GET /api/v1/dependencies
```

#### Create Dependency
```http
POST /api/v1/dependencies
```

**Request Body:**
```json
{
  "source_entity_id": 10,
  "target_entity_id": 20,
  "dependency_type": "network",
  "metadata": {"port": 443, "protocol": "https"}
}
```

#### Get Dependency
```http
GET /api/v1/dependencies/{id}
```

#### Update Dependency
```http
PATCH /api/v1/dependencies/{id}
```

#### Delete Dependency
```http
DELETE /api/v1/dependencies/{id}
```

---

### Identities

Manage users and authentication.

#### List Identities
```http
GET /api/v1/identities
```

#### Create Identity
```http
POST /api/v1/identities
```

#### Get Identity
```http
GET /api/v1/identities/{id}
```

#### Update Identity
```http
PATCH /api/v1/identities/{id}
```

---

### Issues (GitHub-Style Issue Tracking)

Track issues, bugs, and tasks associated with organizations and entities.

#### List Issues
```http
GET /api/v1/issues
```

**Query Parameters:**
- `organization_id` - Filter by organization (includes children)
- `status` - Filter by status (open, closed)
- `priority` - Filter by priority (low, medium, high, critical)
- `assignee_id` - Filter by assigned identity
- `label_id` - Filter by label

#### Create Issue
```http
POST /api/v1/issues
```

**Request Body:**
```json
{
  "title": "Database connection timeout",
  "description": "Production database experiencing timeouts",
  "organization_id": 1,
  "status": "open",
  "priority": "high",
  "is_incident": false,
  "assignee_id": 10
}
```

#### Get Issue
```http
GET /api/v1/issues/{id}
```

#### Update Issue
```http
PATCH /api/v1/issues/{id}
```

#### Add Comment
```http
POST /api/v1/issues/{id}/comments
```

#### Add/Remove Labels
```http
POST /api/v1/issues/{id}/labels
DELETE /api/v1/issues/{id}/labels/{label_id}
```

#### Link Entity
```http
POST /api/v1/issues/{id}/entities
```

---

### Projects

Manage project milestones and roadmaps.

#### List Projects
```http
GET /api/v1/projects
```

#### Create Project
```http
POST /api/v1/projects
```

#### Manage Milestones
```http
GET /api/v1/milestones
POST /api/v1/milestones
PATCH /api/v1/milestones/{id}
```

---

### Resource Roles

Fine-grained permissions per organization or entity.

#### Role Types

- `maintainer` - Full control (CRUD all)
- `operator` - Operational access (create, close issues, manage)
- `viewer` - Read-only access

#### List Resource Roles
```http
GET /api/v1/resource-roles
```

#### Assign Role
```http
POST /api/v1/resource-roles
```

**Request Body:**
```json
{
  "identity_id": 10,
  "role": "operator",
  "organization_id": 1
}
```

---

### Metadata

Type-validated metadata fields for entities and organizations.

#### Field Types

- `string`
- `number`
- `date`
- `boolean`
- `json`

#### List Metadata Fields
```http
GET /api/v1/metadata/entity/{entity_id}
GET /api/v1/metadata/organization/{org_id}
```

#### Set Metadata Field
```http
POST /api/v1/metadata/entity/{entity_id}/fields
```

**Request Body:**
```json
{
  "field_name": "compliance_level",
  "field_type": "string",
  "value": "SOC2",
  "is_system": false
}
```

---

### Graph Visualization

Get entity relationship graphs for visualization.

#### Get Graph Data
```http
GET /api/v1/graph
GET /api/v1/graph/organization/{org_id}
GET /api/v1/graph/entity/{entity_id}
```

**Query Parameters:**
- `depth` (int): Maximum traversal depth
- `include_types` (list): Filter entity types

**Response:**
```json
{
  "nodes": [
    {
      "id": 10,
      "label": "web-server-01",
      "type": "compute",
      "group": "compute"
    }
  ],
  "edges": [
    {
      "from": 10,
      "to": 20,
      "label": "depends on",
      "type": "network"
    }
  ]
}
```

---

### Lookup

Fast entity lookups by unique ID or external identifiers.

#### Lookup Entity
```http
GET /api/v1/lookup/entity/{unique_id}
GET /api/v1/lookup/external/{provider}/{external_id}
```

---

## Response Format

### Success Response

```json
{
  "data": { /* response data */ },
  "message": "Success"
}
```

### Error Response

```json
{
  "error": "Entity not found",
  "code": 404,
  "details": {}
}
```

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` - Page number (1-indexed)
- `per_page` - Items per page (max: 1000)

**Response includes:**
```json
{
  "items": [/* data */],
  "total": 500,
  "page": 1,
  "per_page": 50,
  "pages": 10
}
```

## Rate Limiting

- **Community**: 100 requests/15 minutes
- **Professional**: 1000 requests/15 minutes
- **Enterprise**: Unlimited

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Examples

### Complete Workflow Example

```bash
# 1. Create an organization
ORG=$(curl -X POST http://localhost:5000/api/v1/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Infrastructure",
    "description": "Production environment"
  }' | jq -r '.id')

# 2. Create entities
WEB_SERVER=$(curl -X POST http://localhost:5000/api/v1/entities \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"web-server-01\",
    \"entity_type\": \"compute\",
    \"organization_id\": $ORG,
    \"attributes\": {
      \"ip\": \"10.0.1.10\",
      \"os\": \"Ubuntu 22.04\"
    }
  }" | jq -r '.id')

DB_SERVER=$(curl -X POST http://localhost:5000/api/v1/entities \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"db-server-01\",
    \"entity_type\": \"compute\",
    \"organization_id\": $ORG,
    \"attributes\": {
      \"ip\": \"10.0.1.20\",
      \"os\": \"Ubuntu 22.04\"
    }
  }" | jq -r '.id')

# 3. Create dependency
curl -X POST http://localhost:5000/api/v1/dependencies \
  -H "Content-Type: application/json" \
  -d "{
    \"source_entity_id\": $WEB_SERVER,
    \"target_entity_id\": $DB_SERVER,
    \"dependency_type\": \"database\",
    \"metadata\": {\"port\": 5432}
  }"

# 4. Get graph visualization
curl "http://localhost:5000/api/v1/graph/organization/$ORG" | jq
```

## SDK & Client Libraries

- **Python**: Official Python client (coming soon)
- **Go**: Official Go client (coming soon)
- **JavaScript/TypeScript**: Official JS client (coming soon)

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
```
http://localhost:5000/api/v1/openapi.json
```

## Further Reading

- [Quick Start Guide](../connector/QUICKSTART.md)
- [Architecture Documentation](../architecture/README.md)
- [Development Setup](../development/README.md)
