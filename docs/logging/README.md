# Elder Logging Configuration

Elder implements comprehensive structured logging with support for multiple destinations and configurable verbosity levels.

## Logging Architecture

```
┌──────────────────────────┐
│   Application Logs       │
│  (structlog format)      │
└────────────┬─────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌──────────┐
│ Console  │  │  Remote  │
│  Output  │  │  Sinks   │
└──────────┘  └────┬─────┘
                   │
        ┌──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ Syslog │ │ Kafka  │ │  AWS   │ │  GCP   │
   │  UDP   │ │ HTTP3  │ │CloudWch│ │  Logs  │
   └────────┘ └────────┘ └────────┘ └────────┘
```

## Verbosity Levels

Elder supports three verbosity levels controlled by the `-v` flag:

| Flag | Level | Log Level | Description |
|------|-------|-----------|-------------|
| `-v` | 1 | WARNING | Warnings and critical errors only |
| `-vv` | 2 | INFO | Standard operational information (default) |
| `-vvv` | 3 | DEBUG | Detailed debugging information |

## Environment Variables

### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` | No |
| `VERBOSITY` | Verbosity level (1, 2, 3) - overrides LOG_LEVEL | `2` | No |

### Console Logging

Console logging is always enabled and outputs to stdout.

### UDP Syslog Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SYSLOG_ENABLED` | Enable syslog logging | `false` | No |
| `SYSLOG_HOST` | Syslog server hostname | - | If enabled |
| `SYSLOG_PORT` | Syslog server port | `514` | No |

**Example:**
```bash
SYSLOG_ENABLED=true
SYSLOG_HOST=syslog.example.com
SYSLOG_PORT=514
```

### Kafka HTTP3 Configuration

High-performance log streaming to Kafka clusters via HTTP3/QUIC.

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `KAFKA_ENABLED` | Enable Kafka logging | `false` | No |
| `KAFKA_URL` | Kafka REST API URL | - | If enabled |
| `KAFKA_TOPIC` | Kafka topic name | `elder-logs` | No |
| `KAFKA_API_KEY` | Kafka API key for authentication | - | No |

**Example:**
```bash
KAFKA_ENABLED=true
KAFKA_URL=https://kafka.example.com:443
KAFKA_TOPIC=elder-production-logs
KAFKA_API_KEY=your-api-key-here
```

### AWS CloudWatch Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CLOUDWATCH_ENABLED` | Enable CloudWatch logging | `false` | No |
| `CLOUDWATCH_LOG_GROUP` | CloudWatch log group name | - | If enabled |
| `CLOUDWATCH_LOG_STREAM` | CloudWatch log stream name | - | If enabled |
| `CLOUDWATCH_REGION` | AWS region | `us-east-1` | No |
| `AWS_ACCESS_KEY_ID` | AWS access key (or use IAM role) | - | No |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (or use IAM role) | - | No |

**Example:**
```bash
CLOUDWATCH_ENABLED=true
CLOUDWATCH_LOG_GROUP=/elder/production
CLOUDWATCH_LOG_STREAM=api-server-01
CLOUDWATCH_REGION=us-west-2
# AWS credentials via IAM role (recommended) or:
# AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
# AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Install boto3 for CloudWatch:**
```bash
pip install boto3==1.35.90
```

### GCP Cloud Logging Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GCP_LOGGING_ENABLED` | Enable GCP Cloud Logging | `false` | No |
| `GCP_PROJECT_ID` | GCP project ID | - | If enabled |
| `GCP_LOG_NAME` | GCP log name | `elder` | No |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | - | If enabled |

**Example:**
```bash
GCP_LOGGING_ENABLED=true
GCP_PROJECT_ID=my-gcp-project
GCP_LOG_NAME=elder-production
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Install google-cloud-logging:**
```bash
pip install google-cloud-logging==3.11.4
```

## Log Format

All logs are structured in JSON format:

```json
{
  "event": "user_login",
  "timestamp": "2025-10-23T14:30:45.123456Z",
  "level": "info",
  "logger": "elder",
  "user_id": 123,
  "organization_id": 456,
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "message": "User logged in successfully"
}
```

## Usage Examples

### Basic Python Usage

```python
from shared.logging import configure_logging_from_env
import structlog

# Configure logging from environment variables
logger = configure_logging_from_env(app_name="elder")

# Log messages
logger.info("application_started", version="0.1.0", port=5000)
logger.warning("high_memory_usage", usage_mb=1024, threshold_mb=800)
logger.error("database_connection_failed", error="Connection timeout", host="db.example.com")

# Log with context
logger.bind(user_id=123, organization_id=456).info("entity_created", entity_type="server", entity_name="web-01")
```

### Flask Integration

```python
from flask import Flask
from shared.logging import configure_logging_from_env

app = Flask(__name__)
logger = configure_logging_from_env(app_name="elder-api")

@app.before_request
def log_request():
    logger.info("http_request",
                method=request.method,
                path=request.path,
                ip=request.remote_addr)

@app.after_request
def log_response(response):
    logger.info("http_response",
                method=request.method,
                path=request.path,
                status=response.status_code,
                size=response.content_length)
    return response
```

### gRPC Server Integration

```python
from shared.logging import configure_logging_from_env
import grpc

logger = configure_logging_from_env(app_name="elder-grpc")

class ElderServicer(elder_pb2_grpc.ElderServiceServicer):
    def ListOrganizations(self, request, context):
        logger.info("grpc_request",
                    method="ListOrganizations",
                    page=request.pagination.page,
                    per_page=request.pagination.per_page)
        # Implementation...
        logger.info("grpc_response",
                    method="ListOrganizations",
                    result_count=len(organizations))
        return response
```

### Command-Line Arguments

```python
import argparse
from shared.logging import StructuredLogger

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='Increase verbosity (-v, -vv, -vvv)')
args = parser.parse_args()

# Map argparse count to verbosity level (0->2, 1->1, 2->2, 3->3)
verbosity = max(1, min(3, 2 - args.verbose + 1)) if args.verbose else 2

logger_config = StructuredLogger(app_name="elder-cli", verbosity=verbosity)
logger = logger_config.configure(enable_console=True)
```

## Configuration Templates

### Development Environment

```bash
# .env.development
LOG_LEVEL=DEBUG
VERBOSITY=3
SYSLOG_ENABLED=false
KAFKA_ENABLED=false
CLOUDWATCH_ENABLED=false
GCP_LOGGING_ENABLED=false
```

### Production with Syslog

```bash
# .env.production
LOG_LEVEL=INFO
VERBOSITY=2
SYSLOG_ENABLED=true
SYSLOG_HOST=syslog.company.com
SYSLOG_PORT=514
KAFKA_ENABLED=false
CLOUDWATCH_ENABLED=false
GCP_LOGGING_ENABLED=false
```

### Production with Kafka

```bash
# .env.production
LOG_LEVEL=INFO
VERBOSITY=2
SYSLOG_ENABLED=false
KAFKA_ENABLED=true
KAFKA_URL=https://kafka-rest.company.com:443
KAFKA_TOPIC=elder-production-logs
KAFKA_API_KEY=${KAFKA_API_KEY}  # From secrets
CLOUDWATCH_ENABLED=false
GCP_LOGGING_ENABLED=false
```

### Production with AWS CloudWatch

```bash
# .env.production
LOG_LEVEL=INFO
VERBOSITY=2
SYSLOG_ENABLED=false
KAFKA_ENABLED=false
CLOUDWATCH_ENABLED=true
CLOUDWATCH_LOG_GROUP=/elder/production
CLOUDWATCH_LOG_STREAM=api-${HOSTNAME}
CLOUDWATCH_REGION=us-east-1
GCP_LOGGING_ENABLED=false
# Use IAM role for credentials (recommended)
```

### Production with GCP Cloud Logging

```bash
# .env.production
LOG_LEVEL=INFO
VERBOSITY=2
SYSLOG_ENABLED=false
KAFKA_ENABLED=false
CLOUDWATCH_ENABLED=false
GCP_LOGGING_ENABLED=true
GCP_PROJECT_ID=elder-production
GCP_LOG_NAME=elder-api
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-service-account.json
```

### Multi-Destination Production

```bash
# .env.production
LOG_LEVEL=INFO
VERBOSITY=2

# Local syslog for debugging
SYSLOG_ENABLED=true
SYSLOG_HOST=localhost
SYSLOG_PORT=514

# Primary log aggregation via Kafka
KAFKA_ENABLED=true
KAFKA_URL=https://kafka-rest.company.com:443
KAFKA_TOPIC=elder-production-logs
KAFKA_API_KEY=${KAFKA_API_KEY}

# AWS CloudWatch for compliance
CLOUDWATCH_ENABLED=true
CLOUDWATCH_LOG_GROUP=/elder/production
CLOUDWATCH_LOG_STREAM=api-${HOSTNAME}
CLOUDWATCH_REGION=us-east-1
```

## Docker Compose Configuration

```yaml
services:
  api:
    environment:
      - VERBOSITY=2
      - SYSLOG_ENABLED=true
      - SYSLOG_HOST=syslog
      - KAFKA_ENABLED=true
      - KAFKA_URL=http://kafka-rest:8082
      - KAFKA_TOPIC=elder-logs
    depends_on:
      - syslog
      - kafka

  syslog:
    image: balabit/syslog-ng:latest
    volumes:
      - ./config/syslog-ng.conf:/etc/syslog-ng/syslog-ng.conf
    ports:
      - "514:514/udp"

  kafka:
    image: confluentinc/cp-kafka:latest
    # Kafka configuration...

  kafka-rest:
    image: confluentinc/cp-kafka-rest:latest
    # Kafka REST proxy configuration...
```

## Kubernetes Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: elder-logging-config
data:
  LOG_LEVEL: "INFO"
  VERBOSITY: "2"
  KAFKA_ENABLED: "true"
  KAFKA_URL: "https://kafka-rest.kafka.svc.cluster.local:8082"
  KAFKA_TOPIC: "elder-production-logs"
---
apiVersion: v1
kind: Secret
metadata:
  name: elder-logging-secrets
type: Opaque
stringData:
  KAFKA_API_KEY: "your-kafka-api-key"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elder-api
spec:
  template:
    spec:
      containers:
      - name: api
        envFrom:
        - configMapRef:
            name: elder-logging-config
        - secretRef:
            name: elder-logging-secrets
```

## Performance Considerations

### Log Volume

- **DEBUG level**: High volume, use only in development or troubleshooting
- **INFO level**: Moderate volume, suitable for production
- **WARNING level**: Low volume, minimal performance impact

### Destination Performance

| Destination | Latency | Throughput | Reliability | Notes |
|-------------|---------|------------|-------------|-------|
| Console | <1ms | High | 100% | Always available |
| UDP Syslog | 1-5ms | High | Best-effort | May lose messages |
| Kafka HTTP3 | 5-20ms | Very High | High | Batching recommended |
| CloudWatch | 10-50ms | Medium | High | API rate limits |
| GCP Logs | 10-50ms | Medium | High | API rate limits |

### Recommendations

1. **Always enable console logging** for debugging and local development
2. **Use Kafka for high-volume production** environments (1000+ logs/sec)
3. **Use CloudWatch/GCP for compliance** and long-term retention
4. **Use UDP syslog for legacy compatibility** or local aggregation
5. **Avoid synchronous cloud logging** in critical request paths

## Troubleshooting

### Logs Not Appearing

1. Check verbosity level matches expected log level
2. Verify environment variables are set correctly
3. Check network connectivity to remote sinks
4. Review handler initialization messages in console output

### High Memory Usage

1. Reduce log volume by increasing verbosity threshold
2. Enable asynchronous handlers for cloud destinations
3. Implement log sampling for high-frequency events

### CloudWatch Rate Limiting

```python
# Batch logs before sending
logger.info("batch_operation_started", operation_id=123)
# ... perform batch operation ...
logger.info("batch_operation_completed",
            operation_id=123,
            items_processed=1000,
            duration_ms=5000)
```

## Security Considerations

- **Never log sensitive data**: passwords, API keys, tokens, PII
- **Sanitize user input**: prevent log injection attacks
- **Encrypt log transport**: use TLS for remote destinations
- **Rotate API keys**: regularly rotate Kafka/cloud API keys
- **Access control**: restrict access to log data

```python
# Good: Sanitized logging
logger.info("user_login_attempt",
            username=username,  # OK
            ip=request.remote_addr)  # OK

# Bad: Logging sensitive data
logger.debug("auth_request",
             password=password)  # NEVER DO THIS
```

## Log Retention

- **Development**: 7 days
- **Production**: 30-90 days (depends on compliance requirements)
- **Compliance**: 1-7 years (AWS CloudWatch/GCP with lifecycle policies)

## Additional Resources

- [structlog Documentation](https://www.structlog.org/)
- [AWS CloudWatch Logs](https://docs.aws.amazon.com/cloudwatch/)
- [GCP Cloud Logging](https://cloud.google.com/logging/docs)
- [Kafka REST Proxy](https://docs.confluent.io/platform/current/kafka-rest/index.html)
