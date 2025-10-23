# Elder gRPC API Documentation

## Overview

Elder provides a high-performance gRPC API for client integrations. The gRPC API is an **enterprise-only feature** that requires a valid PenguinTech Enterprise license.

**Key Features:**
- 45 RPC methods covering all Elder functionality
- HTTP/2-based binary protocol for high performance
- gRPC-Web support for browser clients via Envoy proxy
- Automatic code generation for multiple languages
- Server reflection enabled for debugging with grpcurl/grpcui
- Comprehensive type safety with Protocol Buffers

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ─HTTP/2─┤ Envoy Proxy  │ ─gRPC──│ Elder gRPC  │
│  (gRPC-Web) │         │   :8080      │         │ Server      │
└─────────────┘         └──────────────┘         │   :50051    │
                                                  └─────────────┘
┌─────────────┐                                         │
│   Native    │ ────────── gRPC/HTTP2 ─────────────────┘
│   Client    │
└─────────────┘
```

- **gRPC Server**: Port 50051 (native gRPC clients)
- **Envoy Proxy**: Port 8080 (gRPC-Web for browsers)
- **Envoy Admin**: Port 9901 (Envoy admin interface)

## Service Definition

The Elder gRPC API is defined in `apps/api/grpc/proto/elder.proto`:

```protobuf
service ElderService {
  // Authentication & Identity Management (11 methods)
  rpc Login(...) returns (...);
  rpc RefreshToken(...) returns (...);
  rpc Logout(...) returns (...);
  // ... more auth methods

  // Organization Management (7 methods)
  rpc ListOrganizations(...) returns (...);
  rpc GetOrganization(...) returns (...);
  rpc CreateOrganization(...) returns (...);
  // ... more organization methods

  // Entity Management (7 methods)
  rpc ListEntities(...) returns (...);
  rpc GetEntity(...) returns (...);
  rpc CreateEntity(...) returns (...);
  // ... more entity methods

  // Dependency Management (7 methods)
  rpc ListDependencies(...) returns (...);
  rpc CreateDependency(...) returns (...);
  // ... more dependency methods

  // Graph Operations (4 methods)
  rpc GetDependencyGraph(...) returns (...);
  rpc AnalyzeGraph(...) returns (...);
  rpc FindPath(...) returns (...);
  rpc GetEntityImpact(...) returns (...);

  // Health Check (1 method)
  rpc HealthCheck(...) returns (...);
}
```

## Getting Started

### Prerequisites

- **Enterprise License**: gRPC API requires PenguinTech Enterprise tier
- **License Key**: Set `LICENSE_KEY` environment variable
- **Docker**: For running Elder services

### Starting gRPC Services

```bash
# Start all services including gRPC server and Envoy proxy
docker-compose up -d grpc-server grpc-web-proxy

# Check gRPC server logs
docker-compose logs -f grpc-server

# Check Envoy proxy logs
docker-compose logs -f grpc-web-proxy
```

### Environment Variables

**gRPC Server Configuration:**
```bash
GRPC_HOST=0.0.0.0              # Bind address
GRPC_PORT=50051                # gRPC server port
GRPC_MAX_WORKERS=10            # Thread pool size
GRPC_REQUIRE_LICENSE=true      # Enforce enterprise license
```

**Envoy Proxy Configuration:**
```bash
GRPC_WEB_PORT=8080            # gRPC-Web HTTP port
ENVOY_ADMIN_PORT=9901         # Envoy admin interface
```

## Client Development

### Python Client

```python
import grpc
from apps.api.grpc.generated import elder_pb2_grpc, organization_pb2

# Create channel
channel = grpc.insecure_channel('localhost:50051')
stub = elder_pb2_grpc.ElderServiceStub(channel)

# List organizations
response = stub.ListOrganizations(
    organization_pb2.ListOrganizationsRequest(
        pagination=common_pb2.PaginationRequest(page=1, per_page=10)
    )
)

for org in response.organizations:
    print(f"{org.id}: {org.name}")
```

**Full example:** `docs/grpc/python_client_example.py`

### Go Client

```go
package main

import (
    "context"
    "log"

    "google.golang.org/grpc"
    pb "github.com/penguintechinc/elder/proto"
)

func main() {
    // Connect to server
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    client := pb.NewElderServiceClient(conn)

    // List organizations
    resp, err := client.ListOrganizations(context.Background(),
        &pb.ListOrganizationsRequest{
            Pagination: &pb.PaginationRequest{
                Page:    1,
                PerPage: 10,
            },
        })

    if err != nil {
        log.Fatal(err)
    }

    for _, org := range resp.Organizations {
        log.Printf("%d: %s\n", org.Id, org.Name)
    }
}
```

### JavaScript/TypeScript (gRPC-Web)

```javascript
const {ElderServiceClient} = require('./elder_grpc_web_pb');
const {ListOrganizationsRequest, PaginationRequest} = require('./organization_pb');

// Connect to Envoy proxy
const client = new ElderServiceClient('http://localhost:8080');

// List organizations
const request = new ListOrganizationsRequest();
request.setPagination(new PaginationRequest().setPage(1).setPerPage(10));

client.listOrganizations(request, {}, (err, response) => {
    if (err) {
        console.error(err);
        return;
    }

    response.getOrganizationsList().forEach(org => {
        console.log(`${org.getId()}: ${org.getName()}`);
    });
});
```

## Code Generation

### Generating Python Code

```bash
# Generate Python protobuf and gRPC code
make generate-grpc

# Generated files will be in:
# apps/api/grpc/generated/*_pb2.py
# apps/api/grpc/generated/*_pb2_grpc.py
```

### Generating Go Code

```bash
# Install protoc-gen-go and protoc-gen-go-grpc
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Generate Go code
protoc -I apps/api/grpc/proto \
    --go_out=. \
    --go_opt=paths=source_relative \
    --go-grpc_out=. \
    --go-grpc_opt=paths=source_relative \
    apps/api/grpc/proto/*.proto
```

### Generating JavaScript (gRPC-Web)

```bash
# Install protoc-gen-grpc-web
npm install -g grpc-web

# Generate JavaScript code
protoc -I apps/api/grpc/proto \
    --js_out=import_style=commonjs:./client \
    --grpc-web_out=import_style=commonjs,mode=grpcwebtext:./client \
    apps/api/grpc/proto/*.proto
```

## Testing with grpcurl

[grpcurl](https://github.com/fullstorydev/grpcurl) is a command-line tool for interacting with gRPC servers.

```bash
# Install grpcurl
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# List services
grpcurl -plaintext localhost:50051 list

# List methods
grpcurl -plaintext localhost:50051 list elder.ElderService

# Health check
grpcurl -plaintext localhost:50051 elder.ElderService/HealthCheck

# List organizations
grpcurl -plaintext \
    -d '{"pagination": {"page": 1, "per_page": 10}}' \
    localhost:50051 elder.ElderService/ListOrganizations

# Create organization
grpcurl -plaintext \
    -d '{"name": "Test Org", "description": "Test organization"}' \
    localhost:50051 elder.ElderService/CreateOrganization
```

## Testing with grpcui

[grpcui](https://github.com/fullstorydev/grpcui) provides a web-based GUI for testing gRPC services.

```bash
# Install grpcui
go install github.com/fullstorydev/grpcui/cmd/grpcui@latest

# Launch grpcui
grpcui -plaintext localhost:50051

# Open browser to http://localhost:8080
```

## Authentication

### Bearer Token Authentication

All gRPC methods (except Login and HealthCheck) require authentication via metadata:

```python
# Python
metadata = [('authorization', f'Bearer {access_token}')]
response = stub.GetOrganization(request, metadata=metadata)
```

```go
// Go
md := metadata.Pairs("authorization", "Bearer "+accessToken)
ctx := metadata.NewOutgoingContext(context.Background(), md)
response, err := client.GetOrganization(ctx, request)
```

```javascript
// JavaScript (gRPC-Web)
const metadata = {'authorization': 'Bearer ' + accessToken};
client.getOrganization(request, metadata, callback);
```

### Login Flow

1. Call `Login` RPC with username and password
2. Receive access_token and refresh_token
3. Use access_token in Authorization metadata for subsequent calls
4. Refresh token when access_token expires using `RefreshToken` RPC

## Error Handling

gRPC uses standard status codes:

| Code | Description | HTTP Equivalent |
|------|-------------|-----------------|
| OK | Success | 200 |
| CANCELLED | Cancelled by caller | 499 |
| INVALID_ARGUMENT | Invalid request | 400 |
| NOT_FOUND | Resource not found | 404 |
| ALREADY_EXISTS | Resource already exists | 409 |
| PERMISSION_DENIED | Permission denied | 403 |
| UNAUTHENTICATED | Authentication required | 401 |
| RESOURCE_EXHAUSTED | Rate limited | 429 |
| UNIMPLEMENTED | Method not implemented | 501 |
| UNAVAILABLE | Service unavailable | 503 |
| INTERNAL | Internal server error | 500 |

**Example error handling:**

```python
try:
    response = stub.GetOrganization(request)
except grpc.RpcError as e:
    print(f"Error: {e.code()} - {e.details()}")
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print("Organization not found")
    elif e.code() == grpc.StatusCode.UNAUTHENTICATED:
        print("Authentication required")
```

## Performance Considerations

### Connection Reuse

Always reuse gRPC channels instead of creating new ones for each request:

```python
# Good: Create channel once, reuse for multiple calls
channel = grpc.insecure_channel('localhost:50051')
stub = elder_pb2_grpc.ElderServiceStub(channel)
# Make many calls with same stub
response1 = stub.ListOrganizations(...)
response2 = stub.ListEntities(...)
channel.close()

# Bad: Creating new channel for each request
for i in range(100):
    channel = grpc.insecure_channel('localhost:50051')  # Don't do this!
    stub = elder_pb2_grpc.ElderServiceStub(channel)
    response = stub.ListOrganizations(...)
    channel.close()
```

### Message Size Limits

Default message size limits:
- Max send message: 100 MB
- Max receive message: 100 MB

### Keepalive Settings

The server uses these keepalive settings:
- Keepalive time: 30 seconds
- Keepalive timeout: 10 seconds

## Production Deployment

### TLS/mTLS

For production, always use TLS:

```python
# Client with TLS
credentials = grpc.ssl_channel_credentials(
    root_certificates=open('ca.pem', 'rb').read(),
    private_key=open('client-key.pem', 'rb').read(),
    certificate_chain=open('client-cert.pem', 'rb').read()
)
channel = grpc.secure_channel('grpc.example.com:443', credentials)
```

```bash
# Server with TLS (update server.py)
server_credentials = grpc.ssl_server_credentials([
    (open('server-key.pem', 'rb').read(),
     open('server-cert.pem', 'rb').read())
])
server.add_secure_port('0.0.0.0:50051', server_credentials)
```

### Load Balancing

Use client-side load balancing for multiple gRPC servers:

```python
# Round-robin across multiple servers
channel = grpc.insecure_channel(
    'grpc-lb.example.com:50051',
    options=[
        ('grpc.lb_policy_name', 'round_robin'),
        ('grpc.enable_retries', 1),
        ('grpc.max_reconnect_backoff_ms', 10000),
    ]
)
```

### Monitoring

Monitor gRPC server metrics via Prometheus:
- Request rate by method
- Error rate by status code
- Request duration histogram
- Active connections

Access Envoy admin interface:
```bash
curl http://localhost:9901/stats/prometheus
```

## Troubleshooting

### Connection Refused

```
grpc._channel._InactiveRpcError: StatusCode.UNAVAILABLE
```

**Solution:** Ensure gRPC server is running on port 50051

```bash
docker-compose ps grpc-server
docker-compose logs grpc-server
```

### License Validation Failed

```
grpc.StatusCode.PERMISSION_DENIED: gRPC API requires enterprise license
```

**Solution:** Set valid enterprise license key

```bash
export LICENSE_KEY=PENG-XXXX-XXXX-XXXX-XXXX-XXXX
docker-compose restart grpc-server
```

### Method Not Implemented

```
grpc.StatusCode.UNIMPLEMENTED: Method not yet implemented
```

**Solution:** The RPC method exists in the protobuf definition but hasn't been implemented yet. Check the server logs for which methods are available.

### CORS Issues (gRPC-Web)

If browser requests fail with CORS errors, check Envoy proxy configuration in `infrastructure/envoy/envoy.yaml` and ensure CORS is properly configured.

## References

- [gRPC Official Documentation](https://grpc.io/docs/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [gRPC-Web](https://github.com/grpc/grpc-web)
- [Envoy Proxy](https://www.envoyproxy.io/)
- [grpcurl](https://github.com/fullstorydev/grpcurl)
- [grpcui](https://github.com/fullstorydev/grpcui)

## Support

For gRPC API support:
- **Technical Issues**: support@penguintech.io
- **License Questions**: sales@penguintech.io
- **Documentation**: https://docs.penguintech.io/elder/grpc
