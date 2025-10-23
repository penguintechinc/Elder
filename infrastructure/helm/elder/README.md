# Elder Helm Chart

This Helm chart deploys Elder - an Entity, Element, and Relationship Tracking System - on Kubernetes.

## Prerequisites

- Kubernetes 1.24+
- Helm 3.8+
- PV provisioner support in the underlying infrastructure (for PostgreSQL and Redis persistence)

## Installing the Chart

### Add Dependencies

First, add the Bitnami repository and update dependencies:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm dependency update
```

### Install with Default Configuration

```bash
helm install elder . \
  --set config.secretKey="your-secret-key-here" \
  --set postgresql.auth.password="your-db-password" \
  --set redis.auth.password="your-redis-password"
```

### Install with Enterprise License

```bash
helm install elder . \
  --set config.secretKey="your-secret-key-here" \
  --set config.license.key="PENG-XXXX-XXXX-XXXX-XXXX-ABCD" \
  --set postgresql.auth.password="your-db-password" \
  --set redis.auth.password="your-redis-password"
```

### Install with External Database

```bash
helm install elder . \
  --set config.secretKey="your-secret-key-here" \
  --set config.databaseUrl="postgresql://user:pass@host:5432/elder" \
  --set config.redisUrl="redis://:pass@host:6379/0" \
  --set postgresql.enabled=false \
  --set redis.enabled=false
```

### Install with Ingress

```bash
helm install elder . \
  --set config.secretKey="your-secret-key-here" \
  --set api.ingress.enabled=true \
  --set api.ingress.hosts[0].host=elder.example.com \
  --set api.ingress.hosts[0].paths[0].path=/ \
  --set api.ingress.hosts[0].paths[0].pathType=Prefix \
  --set api.ingress.tls[0].secretName=elder-tls \
  --set api.ingress.tls[0].hosts[0]=elder.example.com \
  --set postgresql.auth.password="your-db-password" \
  --set redis.auth.password="your-redis-password"
```

## Configuration

The following table lists the configurable parameters and their default values.

### Global Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.imageRegistry` | Global Docker image registry | `ghcr.io` |
| `global.imagePullSecrets` | Global Docker registry secret names | `[]` |

### API Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `api.enabled` | Enable API deployment | `true` |
| `api.replicaCount` | Number of API replicas | `3` |
| `api.image.repository` | API image repository | `penguintechinc/elder-api` |
| `api.image.tag` | API image tag | Chart appVersion |
| `api.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `api.service.type` | Kubernetes service type | `ClusterIP` |
| `api.service.port` | Service port | `80` |
| `api.service.targetPort` | Container port | `5000` |
| `api.resources.requests.memory` | Memory request | `256Mi` |
| `api.resources.requests.cpu` | CPU request | `250m` |
| `api.resources.limits.memory` | Memory limit | `512Mi` |
| `api.resources.limits.cpu` | CPU limit | `500m` |

### gRPC Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `grpc.enabled` | Enable gRPC server | `true` |
| `grpc.replicaCount` | Number of gRPC replicas | `2` |
| `grpc.image.repository` | gRPC image repository | `penguintechinc/elder-grpc` |
| `grpc.image.tag` | gRPC image tag | Chart appVersion |
| `grpc.service.port` | gRPC service port | `50051` |
| `grpc.config.maxWorkers` | gRPC max workers | `10` |
| `grpc.config.requireLicense` | Require enterprise license | `true` |

### Envoy Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `envoy.enabled` | Enable Envoy proxy for gRPC-Web | `true` |
| `envoy.replicaCount` | Number of Envoy replicas | `2` |
| `envoy.image.repository` | Envoy image repository | `penguintechinc/elder-envoy` |
| `envoy.service.port` | Envoy HTTP port | `8080` |
| `envoy.service.adminPort` | Envoy admin port | `9901` |

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.flaskEnv` | Flask environment | `production` |
| `config.secretKey` | Flask secret key (required) | `""` |
| `config.license.key` | PenguinTech license key | `""` |
| `config.license.serverUrl` | License server URL | `https://license.penguintech.io` |
| `config.license.productName` | Product name | `elder` |
| `config.databaseUrl` | External database URL | `""` |
| `config.redisUrl` | External Redis URL | `""` |
| `config.logging.level` | Log level | `INFO` |
| `config.metricsEnabled` | Enable Prometheus metrics | `true` |

### PostgreSQL Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable bundled PostgreSQL | `true` |
| `postgresql.auth.username` | Database username | `elder` |
| `postgresql.auth.password` | Database password | `""` |
| `postgresql.auth.database` | Database name | `elder` |
| `postgresql.primary.persistence.size` | Persistent volume size | `10Gi` |

### Redis Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable bundled Redis | `true` |
| `redis.auth.enabled` | Enable Redis authentication | `true` |
| `redis.auth.password` | Redis password | `""` |
| `redis.master.persistence.size` | Persistent volume size | `1Gi` |

### Autoscaling Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `api.autoscaling.enabled` | Enable HPA for API | `false` |
| `api.autoscaling.minReplicas` | Minimum replicas | `2` |
| `api.autoscaling.maxReplicas` | Maximum replicas | `10` |
| `api.autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `80` |

### Monitoring Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `monitoring.enabled` | Enable monitoring | `true` |
| `monitoring.serviceMonitor.enabled` | Enable ServiceMonitor | `false` |
| `monitoring.serviceMonitor.interval` | Scrape interval | `30s` |

## Upgrading

### To a New Version

```bash
helm upgrade elder . \
  --reuse-values \
  --set api.image.tag=v0.2.0
```

### With New Configuration

```bash
helm upgrade elder . \
  --reuse-values \
  --set api.replicaCount=5 \
  --set api.autoscaling.enabled=true
```

## Uninstalling

```bash
helm uninstall elder
```

This removes all Kubernetes resources associated with the chart, except PersistentVolumeClaims (to prevent data loss).

To remove PVCs as well:

```bash
kubectl delete pvc -l app.kubernetes.io/instance=elder
```

## Architecture

```
┌─────────────────┐
│     Ingress     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ API  │  │ Envoy │
│ Pods │  │ Proxy │
└───┬──┘  └──┬────┘
    │        │
    │    ┌───▼─────┐
    │    │  gRPC   │
    │    │  Pods   │
    │    └───┬─────┘
    │        │
┌───┴────────┴───┐
│   PostgreSQL   │
│     Redis      │
└────────────────┘
```

## Features

- **Multi-Architecture Support**: Supports both amd64 and arm64 architectures
- **High Availability**: Multiple replicas with pod anti-affinity
- **Horizontal Pod Autoscaling**: Automatic scaling based on CPU/memory
- **Health Checks**: Liveness and readiness probes configured
- **Security**: Pod security contexts, network policies, secrets management
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Persistence**: Persistent volumes for database and cache
- **Enterprise Features**: License validation and enterprise-tier features
- **gRPC Support**: Full gRPC API with gRPC-Web browser compatibility

## License Tiers

Elder supports three license tiers:

- **Community**: Free tier with basic features
- **Professional**: Advanced features and priority support
- **Enterprise**: Full feature set, gRPC API, and dedicated support

Enterprise license required for:
- gRPC API access
- SAML/OAuth2 SSO
- Advanced LDAP integration
- Resource-level roles

## Support

- **Documentation**: https://github.com/penguintechinc/elder
- **Issues**: https://github.com/penguintechinc/elder/issues
- **License Support**: support@penguintech.io
- **Sales**: sales@penguintech.io
