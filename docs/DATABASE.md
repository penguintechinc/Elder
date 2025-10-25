# Elder Database Configuration

Elder uses **PyDAL** (Python Database Abstraction Layer) for database operations, providing support for 18+ different database systems with a unified API.

## Quick Start
Reference: https://py4web.com/_documentation/static/en/chapter-07.html

### PostgreSQL (Default)

Elder is configured for PostgreSQL by default. Set these environment variables:

```bash
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=your_secure_password
DB_POOL_SIZE=10
```

Or use a full connection URI:

```bash
DATABASE_URL=postgres://elder:password@localhost:5432/elder
```

## Configuration Methods

Elder supports two configuration methods:

### 1. Full Database URL (Recommended for Production)

Set a single `DATABASE_URL` environment variable with the complete connection string:

```bash
DATABASE_URL=postgres://user:password@host:port/database
```

This takes precedence over individual component variables.

### 2. Individual Components (Easier for Development)

Configure database connection using separate environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_TYPE` | Database type (see supported types below) | `postgres` |
| `DB_HOST` | Database host/server | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `elder` |
| `DB_USER` | Database username | `elder` |
| `DB_PASSWORD` | Database password | `elder` |
| `DB_POOL_SIZE` | Connection pool size | `10` |

## Supported Database Systems

Elder supports all PyDAL-compatible databases. Below are configuration examples for each:

### Relational Databases

#### PostgreSQL

```bash
# Via components
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=postgres://elder:password@localhost:5432/elder
```

**Note:** PyDAL uses `postgres://` not `postgresql://`

#### MySQL / MariaDB

```bash
# Via components
DB_TYPE=mysql
DB_HOST=localhost
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=mysql://elder:password@localhost/elder?set_encoding=utf8mb4
```

Automatically includes UTF8MB4 encoding for full Unicode support.

#### SQLite

```bash
# Via components
DB_TYPE=sqlite
DB_NAME=elder  # Creates elder.sqlite file

# Via URI
DATABASE_URL=sqlite://elder.sqlite
```

**Note:** SQLite is file-based and doesn't require user/password/host.

#### Microsoft SQL Server

```bash
# Modern SQL Server (2012+) - Recommended
DB_TYPE=mssql4
DB_HOST=localhost
DB_NAME=elder
DB_USER=sa
DB_PASSWORD=password

# SQL Server 2005+
DB_TYPE=mssql3
# ... same configuration

# Legacy SQL Server
DB_TYPE=mssql
# ... same configuration

# Via URI
DATABASE_URL=mssql4://sa:password@localhost/elder
```

#### Oracle

```bash
# Via components
DB_TYPE=oracle
DB_NAME=ORCL
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=oracle://elder/password@ORCL
```

**Note:** Oracle uses a different URI format: `user/password@database`

#### IBM DB2

```bash
# Via components
DB_TYPE=db2
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=db2://elder:password@elder
```

#### FireBird

```bash
# Via components
DB_TYPE=firebird
DB_HOST=localhost
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=firebird://elder:password@localhost/elder
```

#### Ingres

```bash
# Via components
DB_TYPE=ingres
DB_HOST=localhost
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=ingres://elder:password@localhost/elder
```

#### Sybase

```bash
# Via components
DB_TYPE=sybase
DB_HOST=localhost
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=sybase://elder:password@localhost/elder
```

#### Informix

```bash
# Via components
DB_TYPE=informix
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=informix://elder:password@elder
```

#### Teradata

```bash
# Via components (uses DSN format)
DB_TYPE=teradata
DB_HOST=my_dsn
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=teradata://DSN=my_dsn;UID=elder;PWD=password;DATABASE=elder
```

#### CUBRID

```bash
# Via components
DB_TYPE=cubrid
DB_HOST=localhost
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=cubrid://elder:password@localhost/elder
```

#### SAP DB (MaxDB)

```bash
# Via components
DB_TYPE=sapdb
DB_HOST=localhost
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=sapdb://elder:password@localhost/elder
```

### NoSQL Databases

#### MongoDB

```bash
# Via components
DB_TYPE=mongodb
DB_HOST=localhost
DB_NAME=elder
DB_USER=elder
DB_PASSWORD=password

# Via URI
DATABASE_URL=mongodb://elder:password@localhost/elder
```

### Cloud Databases

#### Google Cloud SQL

```bash
# Via components
DB_TYPE=google:sql
DB_HOST=project-id:instance-name
DB_NAME=database

# Via URI
DATABASE_URL=google:sql://project-id:instance-name/database
```

**Note:** `DB_HOST` should be in format `project:instance`

#### Google Cloud Datastore (NoSQL)

```bash
# Standard Datastore
DB_TYPE=google:datastore
DATABASE_URL=google:datastore

# With NDB API
DB_TYPE=google:datastore+ndb
DATABASE_URL=google:datastore+ndb
```

### Special Purpose

#### IMAP (Email Storage)

```bash
# Via components
DB_TYPE=imap
DB_HOST=mail.example.com
DB_PORT=993
DB_USER=user@example.com
DB_PASSWORD=password

# Via URI
DATABASE_URL=imap://user@example.com:password@mail.example.com:993
```

**Note:** Used for storing data in IMAP email folders (advanced use case).

## Connection Pooling

Elder uses connection pooling to efficiently manage database connections:

```bash
DB_POOL_SIZE=10  # Number of connections in pool (default: 10)
```

**Recommendations:**
- **Development:** 5-10 connections
- **Production (small):** 10-20 connections
- **Production (large):** 20-50 connections
- **High traffic:** 50-100 connections

Monitor your application's connection usage and adjust accordingly.

## Docker Compose Configuration

Example `docker-compose.yml` database configuration:

```yaml
services:
  api:
    environment:
      # Method 1: Full URI
      - DATABASE_URL=postgres://elder:${DB_PASSWORD}@postgres:5432/elder

      # Method 2: Individual components
      - DB_TYPE=postgres
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=elder
      - DB_USER=elder
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_POOL_SIZE=20

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=elder
      - POSTGRES_USER=elder
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## Database Migrations

Elder uses PyDAL's automatic migration system:

### Automatic Migrations (Default)

PyDAL automatically creates and updates database tables based on model definitions:

```python
# In shared/database/connection.py
db = DAL(
    database_url,
    migrate=True,           # Enable automatic migrations
    fake_migrate_all=False  # Disable fake migrations
)
```

### Migration Files

Migration files are stored in the `databases/` folder (or `app.instance_path`):
- `*.table` files - Table definitions
- `sql.log` - SQL migration history

**Important:** Keep these files in version control for production deployments.

### Disabling Migrations (Production)

For production environments where you want to control migrations:

```python
db = DAL(
    database_url,
    migrate=False,          # Disable migrations
    fake_migrate_all=False
)
```

Then manually apply schema changes as needed.

## Database Schema

Elder defines 18 database tables in `apps/api/models/pydal_models.py`:

### Core Tables
1. **organizations** - Organization Units (OUs) hierarchy
2. **entities** - Business entities (applications, services, etc.)
3. **dependencies** - Entity dependency relationships

### Identity & Access Management
4. **identities** - Users and service accounts
5. **identity_groups** - User groups
6. **identity_group_memberships** - Group membership
7. **roles** - System roles
8. **permissions** - Fine-grained permissions
9. **role_permissions** - Role-to-permission mappings
10. **user_roles** - User role assignments

### Enterprise Features
11. **resource_roles** - Resource-level RBAC
12. **issues** - GitHub-style issue tracking
13. **issue_labels** - Issue categorization
14. **issue_label_assignments** - Issue-to-label mappings
15. **issue_comments** - Issue discussion
16. **issue_entity_links** - Entity-to-issue relationships
17. **metadata_fields** - Typed metadata system

### Audit & Logging
18. **audit_logs** - Comprehensive audit trail

## Performance Optimization

### Indexing

PyDAL automatically creates indexes for:
- Primary keys
- Foreign keys
- Fields marked with `unique=True`

For additional indexes, define them in your table definitions:

```python
Field('name', 'string', length=255, notnull=True),
Field('organization_id', 'reference organizations', notnull=True),
# Add custom index in PyDAL migration
```

### Query Optimization

Use PyDAL's query builder efficiently:

```python
# Good: Specific field selection
rows = db(db.organizations.id > 0).select(
    db.organizations.id,
    db.organizations.name,
    orderby=db.organizations.name,
    limitby=(0, 100)
)

# Bad: Select all fields for large result sets
rows = db(db.organizations).select()
```

### Connection Pooling

Adjust `DB_POOL_SIZE` based on your workload:

```bash
# Low traffic
DB_POOL_SIZE=5

# Medium traffic
DB_POOL_SIZE=20

# High traffic
DB_POOL_SIZE=50
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to database

**Solutions:**
1. Verify database is running: `docker-compose ps`
2. Check connection string format matches your database type
3. Verify credentials are correct
4. Check network connectivity: `docker-compose exec api ping postgres`

### Migration Issues

**Problem:** Migration fails or tables not created

**Solutions:**
1. Check database permissions (user needs CREATE TABLE rights)
2. Delete `databases/*.table` files and restart (development only!)
3. Check `databases/sql.log` for error messages
4. Verify database URL is correct

### Performance Issues

**Problem:** Slow database queries

**Solutions:**
1. Increase `DB_POOL_SIZE`
2. Add indexes to frequently queried columns
3. Use `select()` with specific fields instead of `select(*)`
4. Enable query logging to identify slow queries
5. Consider read replicas for high-traffic applications

## Security Best Practices

### 1. Use Strong Passwords

```bash
# Good
DB_PASSWORD=$(openssl rand -base64 32)

# Bad
DB_PASSWORD=password123
```

### 2. Limit Database Permissions

Create a dedicated database user with minimal permissions:

```sql
-- PostgreSQL example
CREATE USER elder WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE elder TO elder;
GRANT USAGE ON SCHEMA public TO elder;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO elder;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO elder;
```

### 3. Use SSL/TLS Connections

For production, enable SSL connections:

```bash
# PostgreSQL with SSL
DATABASE_URL=postgres://user:pass@host/db?sslmode=require

# MySQL with SSL
DATABASE_URL=mysql://user:pass@host/db?ssl=true
```

### 4. Rotate Credentials Regularly

Use secret management tools:
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets
- Docker Secrets

### 5. Network Isolation

Use Docker networks to isolate database access:

```yaml
services:
  api:
    networks:
      - elder-network

  postgres:
    networks:
      - elder-network
    # No external port exposure in production!
```

## References

- **PyDAL Documentation:** https://py4web.com/_documentation/static/en/chapter-07.html
- **Elder Database Models:** `apps/api/models/pydal_models.py`
- **Connection Code:** `shared/database/connection.py`
- **Docker Compose:** `docker-compose.yml`

## Support

For database-related issues:
1. Check this documentation
2. Review PyDAL documentation
3. Check Elder logs: `docker-compose logs api`
4. Open an issue on GitHub

---

**Last Updated:** 2025-10-25
**PyDAL Version:** 20251018.1
**Supported Databases:** 18+
