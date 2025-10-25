# Elder Connector Service

The Elder Connector Service synchronizes data from external sources (AWS, GCP, Google Workspace, LDAP/LDAPS) into the Elder infrastructure management platform.

## Features

- **AWS Integration**: Sync EC2 instances, VPCs, S3 buckets, and more
- **GCP Integration**: Sync Compute Engine instances, VPC networks, Cloud Storage buckets
- **Google Workspace Integration**: Sync users, groups, and organizational units
- **LDAP/LDAPS Integration**: Sync directory services including users, groups, and organizational units
- **Scheduled Synchronization**: Configurable sync intervals for each connector
- **Health Monitoring**: Built-in health checks and Prometheus metrics
- **Auto-Organization Creation**: Automatically creates organizational hierarchies in Elder

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Elder Connector Service                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ AWS Connector│  │ GCP Connector│  │  Workspace   │      │
│  │              │  │              │  │  Connector   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────────────────────────┐    │
│  │LDAP Connector│  │   Elder API Client               │    │
│  │              │  │   (Organizations & Entities)     │    │
│  └──────────────┘  └──────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Scheduler (aiocron) + Health Server (Flask)        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                                         │
         │ Pull Data                               │ Push Data
         ▼                                         ▼
┌─────────────────────┐                 ┌─────────────────────┐
│  External Sources   │                 │    Elder API        │
│  - AWS              │                 │  - Organizations    │
│  - GCP              │                 │  - Entities         │
│  - Google Workspace │                 │  - Dependencies     │
│  - LDAP/LDAPS       │                 └─────────────────────┘
└─────────────────────┘
```

## Configuration

All configuration is done via environment variables in Docker.

### Elder API Configuration

```bash
ELDER_API_URL=http://api:5000              # Elder API base URL
ELDER_API_KEY=                             # Optional API key for authentication
```

### AWS Connector

```bash
AWS_ENABLED=false                          # Enable AWS connector
AWS_ACCESS_KEY_ID=                         # AWS access key ID
AWS_SECRET_ACCESS_KEY=                     # AWS secret access key
AWS_DEFAULT_REGION=us-east-1               # Default AWS region
AWS_REGIONS=us-east-1,us-west-2           # Comma-separated list of regions to scan
AWS_SYNC_INTERVAL=3600                     # Sync interval in seconds (default: 1 hour)
```

**Resources Synced:**
- EC2 Instances → Elder entities (type: `compute`)
- VPCs → Elder entities (type: `vpc`)
- S3 Buckets → Elder entities (type: `network`)

### GCP Connector

```bash
GCP_ENABLED=false                          # Enable GCP connector
GCP_PROJECT_ID=                            # GCP project ID
GCP_CREDENTIALS_PATH=/app/credentials/gcp-credentials.json  # Path to service account JSON
GCP_SYNC_INTERVAL=3600                     # Sync interval in seconds
```

**Resources Synced:**
- Compute Engine Instances → Elder entities (type: `compute`)
- VPC Networks → Elder entities (type: `vpc`)
- Cloud Storage Buckets → Elder entities (type: `network`)

**Credentials Setup:**
1. Create a service account in GCP with appropriate permissions
2. Download the JSON key file
3. Mount it to `/app/credentials/gcp-credentials.json` in the container

### Google Workspace Connector

```bash
GOOGLE_WORKSPACE_ENABLED=false             # Enable Google Workspace connector
GOOGLE_WORKSPACE_CREDENTIALS_PATH=/app/credentials/workspace-credentials.json
GOOGLE_WORKSPACE_ADMIN_EMAIL=              # Admin email for domain-wide delegation
GOOGLE_WORKSPACE_CUSTOMER_ID=my_customer   # Customer ID (usually "my_customer")
GOOGLE_WORKSPACE_SYNC_INTERVAL=3600        # Sync interval in seconds
```

**Resources Synced:**
- Users → Elder entities (type: `user`)
- Groups → Elder entities (type: `user` with `type: group` in attributes)
- Organizational Units → Elder organizations (hierarchical)

**Credentials Setup:**
1. Create a service account with domain-wide delegation
2. Grant necessary Admin SDK scopes
3. Download the JSON key file
4. Mount it to `/app/credentials/workspace-credentials.json`

### LDAP/LDAPS Connector

```bash
LDAP_ENABLED=false                         # Enable LDAP connector
LDAP_SERVER=                               # LDAP server hostname or IP
LDAP_PORT=389                              # LDAP port (389 for LDAP, 636 for LDAPS)
LDAP_USE_SSL=false                         # Use LDAPS (SSL/TLS)
LDAP_VERIFY_CERT=true                      # Verify SSL certificate
LDAP_BIND_DN=                              # Bind DN for authentication
LDAP_BIND_PASSWORD=                        # Bind password
LDAP_BASE_DN=                              # Base DN for searches (e.g., dc=example,dc=com)
LDAP_USER_FILTER=(objectClass=person)      # LDAP filter for users
LDAP_GROUP_FILTER=(objectClass=group)      # LDAP filter for groups
LDAP_SYNC_INTERVAL=3600                    # Sync interval in seconds
```

**Resources Synced:**
- LDAP Users → Elder entities (type: `user`)
- LDAP Groups → Elder entities (type: `user` with `type: group` in attributes)
- Organizational Units → Elder organizations (hierarchical)

**Common LDAP Configurations:**

**Active Directory:**
```bash
LDAP_SERVER=ad.example.com
LDAP_PORT=389
LDAP_USE_SSL=false
LDAP_BIND_DN=cn=admin,cn=Users,dc=example,dc=com
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_FILTER=(&(objectClass=user)(objectCategory=person))
LDAP_GROUP_FILTER=(objectClass=group)
```

**OpenLDAP:**
```bash
LDAP_SERVER=ldap.example.com
LDAP_PORT=389
LDAP_USE_SSL=false
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_FILTER=(objectClass=inetOrgPerson)
LDAP_GROUP_FILTER=(objectClass=groupOfNames)
```

**LDAPS (Secure):**
```bash
LDAP_SERVER=ldaps.example.com
LDAP_PORT=636
LDAP_USE_SSL=true
LDAP_VERIFY_CERT=true
```

### Organization Mapping

```bash
DEFAULT_ORGANIZATION_ID=                   # Default Elder org ID for entities without mapping
CREATE_MISSING_ORGANIZATIONS=true          # Auto-create organizations in Elder
```

### Sync Configuration

```bash
SYNC_ON_STARTUP=true                       # Run initial sync when connector starts
SYNC_BATCH_SIZE=100                        # Number of entities per batch
SYNC_MAX_RETRIES=3                         # Max retries for failed operations
```

### Health & Monitoring

```bash
HEALTH_CHECK_PORT=8000                     # Health check HTTP server port
METRICS_ENABLED=true                       # Enable Prometheus metrics
```

**Health Endpoints:**
- `GET /healthz` - Health check (returns 200 if healthy)
- `GET /metrics` - Prometheus metrics
- `GET /status` - Detailed service status

### Logging

```bash
LOG_LEVEL=INFO                             # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT=json                            # Log format (json or text)
```

## Usage

### Running with Docker Compose

1. **Configure environment variables** in `.env` file:

```bash
# Enable connectors
AWS_ENABLED=true
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGIONS=us-east-1,us-west-2

GCP_ENABLED=true
GCP_PROJECT_ID=my-gcp-project
```

2. **Place credential files** (if using GCP or Google Workspace):

```bash
# Create credentials directory
docker volume create connector_credentials

# Copy credential files
docker run --rm -v connector_credentials:/credentials \
  -v $(pwd)/gcp-credentials.json:/src/gcp-credentials.json \
  alpine cp /src/gcp-credentials.json /credentials/
```

3. **Start the connector service**:

```bash
docker-compose up -d connector
```

4. **Check logs**:

```bash
docker-compose logs -f connector
```

5. **Verify health**:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/status
```

### Manual Sync Trigger

The connector automatically syncs on startup (if `SYNC_ON_STARTUP=true`) and on the configured intervals. To manually trigger a sync, restart the connector:

```bash
docker-compose restart connector
```

## Data Mapping

### AWS Resources

| AWS Resource | Elder Entity Type | Key Attributes |
|--------------|-------------------|----------------|
| EC2 Instance | `compute` | `instance_id`, `instance_type`, `state`, `private_ip`, `public_ip` |
| VPC | `vpc` | `vpc_id`, `cidr_block`, `state` |
| S3 Bucket | `network` | `bucket_name`, `region` |

### GCP Resources

| GCP Resource | Elder Entity Type | Key Attributes |
|--------------|-------------------|----------------|
| Compute Instance | `compute` | `instance_id`, `machine_type`, `status`, `zone` |
| VPC Network | `vpc` | `network_id`, `network_name`, `routing_mode` |
| Storage Bucket | `network` | `bucket_name`, `location`, `storage_class` |

### Google Workspace

| Workspace Resource | Elder Type | Key Attributes |
|-------------------|------------|----------------|
| User | Entity (`user`) | `email`, `user_id`, `first_name`, `last_name`, `suspended` |
| Group | Entity (`user`) | `email`, `group_id`, `group_name`, `type: group` |
| Org Unit | Organization | `org_unit_path`, hierarchical structure |

### LDAP/LDAPS

| LDAP Resource | Elder Type | Key Attributes |
|--------------|------------|----------------|
| User | Entity (`user`) | `ldap_dn`, `cn`, `uid`, `email`, `display_name` |
| Group | Entity (`user`) | `ldap_dn`, `cn`, `group_name`, `type: group` |
| Org Unit | Organization | `ldap_dn`, hierarchical structure |

## Monitoring

### Prometheus Metrics

The connector exposes the following Prometheus metrics at `/metrics`:

```
# Sync operations
connector_sync_total{connector="aws",status="success"} 10
connector_sync_total{connector="aws",status="failed"} 0
connector_sync_duration_seconds{connector="aws"} 15.2

# Errors
connector_sync_errors_total{connector="aws"} 0

# Entities and organizations
connector_entities_synced{connector="aws",operation="created"} 150
connector_entities_synced{connector="aws",operation="updated"} 25
connector_organizations_synced{connector="aws",operation="created"} 5

# Last sync timestamp
connector_last_sync_timestamp{connector="aws"} 1672531200
```

### Grafana Dashboard

A Grafana dashboard can be created to visualize:
- Sync success/failure rates
- Sync duration trends
- Number of entities synced per connector
- Error rates and patterns

## Troubleshooting

### Connector Not Starting

1. Check logs: `docker-compose logs connector`
2. Verify Elder API is healthy: `curl http://localhost:5000/healthz`
3. Check configuration in `.env` file

### Sync Errors

1. View detailed error messages: `docker-compose logs connector | grep ERROR`
2. Check credentials and permissions for each connector
3. Verify network connectivity to external services
4. Check Elder API is accepting requests

### Missing Entities

1. Verify the connector is enabled: Check `*_ENABLED` environment variable
2. Check sync interval hasn't expired
3. Review entity filters in connector configuration
4. Check Elder organization mapping settings

### LDAP Connection Issues

1. Test LDAP connectivity: `ldapsearch -H ldap://server -D "bind_dn" -W`
2. For LDAPS, verify certificate is valid
3. Check bind DN and password are correct
4. Verify base DN exists

### GCP/Google Workspace Authentication

1. Verify service account has correct permissions
2. For Google Workspace, ensure domain-wide delegation is configured
3. Check credential file path is correct and accessible
4. Verify admin email has necessary permissions

## Security Considerations

- **Credentials**: Store all credentials securely using Docker secrets or encrypted environment variables
- **LDAPS**: Always use LDAPS (SSL/TLS) for production LDAP connections
- **Least Privilege**: Grant minimum necessary permissions to service accounts
- **Network**: Use private networks when possible, avoid exposing connector to public internet
- **Logging**: Ensure sensitive data is not logged (credentials, passwords, etc.)

## Development

### Project Structure

```
apps/connector/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── connectors/
│   ├── __init__.py
│   ├── base.py             # Base connector interface
│   ├── aws_connector.py    # AWS connector implementation
│   ├── gcp_connector.py    # GCP connector implementation
│   ├── google_workspace_connector.py
│   └── ldap_connector.py   # LDAP/LDAPS connector implementation
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Structured logging
│   └── elder_client.py     # Elder API client
├── main.py                 # Main service orchestrator
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
└── README.md              # This file
```

### Adding a New Connector

1. Create a new connector class inheriting from `BaseConnector`
2. Implement required methods: `connect()`, `disconnect()`, `sync()`, `health_check()`
3. Add configuration settings to `config/settings.py`
4. Register the connector in `main.py`
5. Update docker-compose.yml with environment variables
6. Update this README with configuration and usage

## License

Elder Connector Service is part of the Elder infrastructure management platform.

Copyright © 2025 Penguin Tech Inc. All rights reserved.
