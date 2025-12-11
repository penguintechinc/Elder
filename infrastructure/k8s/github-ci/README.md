# GitHub CI/CD Kubernetes Infrastructure

This directory contains Kubernetes manifests for GitHub Actions CI/CD integration.

## Overview

These manifests define the necessary Kubernetes resources for GitHub Actions to deploy Elder to a Kubernetes cluster:

- **namespace.yaml**: Creates the `elder` namespace with appropriate labels
- **serviceaccount.yaml**: Creates the `github-ci` ServiceAccount for authentication
- **rbac.yaml**: Defines namespace-scoped Role and RoleBinding with deployment permissions

## Quick Start

### Recommended: Use Setup Script

The easiest way to configure your Kubernetes cluster for GitHub Actions is to use the automated setup script:

```bash
../../scripts/k8s/setup-github-serviceaccount.sh
```

This script will:
1. Detect your Kubernetes distribution (MicroK8s, kind, k3s, standard)
2. Apply all manifests in this directory
3. Generate a kubeconfig for the ServiceAccount
4. Output GitHub secrets in copy-paste format

### Manual Application

If you prefer to apply manifests manually:

```bash
# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f serviceaccount.yaml
kubectl apply -f rbac.yaml

# Verify resources
kubectl get namespace elder
kubectl get serviceaccount -n elder
kubectl get role,rolebinding -n elder
```

## Components

### Namespace (`namespace.yaml`)

Creates the `elder` namespace where Elder services will be deployed:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: elder
  labels:
    app.kubernetes.io/name: elder
    environment: production
```

### ServiceAccount (`serviceaccount.yaml`)

Creates the `github-ci` ServiceAccount that GitHub Actions will use to authenticate:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: github-ci
  namespace: elder
```

**Security note**: `automountServiceAccountToken: false` prevents automatic token mounting, following security best practices.

### RBAC (`rbac.yaml`)

Defines a namespace-scoped Role with permissions needed for deployment operations:

**Permissions granted:**
- **Deployments, ReplicaSets, StatefulSets**: Full access for application deployments
- **Services, ConfigMaps, Secrets, Pods, PVCs**: Full access for service configuration
- **Pod logs**: Read-only access for debugging
- **Ingress**: Create and update for routing configuration
- **HorizontalPodAutoscaler**: Create and update for autoscaling
- **Jobs, CronJobs**: Full access for batch operations

**Security design:**
- Namespace-scoped (not cluster-wide) following principle of least privilege
- No access to nodes, cluster-level resources, or other namespaces
- Only grants permissions necessary for CI/CD deployment operations

## GitHub Actions Integration

After applying these manifests, the setup script will provide:

1. **KUBE_CONFIG**: Base64-encoded kubeconfig for GitHub secret
2. **K8S_NAMESPACE**: Target namespace (`elder`)

Add these to your GitHub repository secrets:
1. Go to repository Settings → Secrets and variables → Actions
2. Add `KUBE_CONFIG` secret with the provided value
3. Add `K8S_NAMESPACE` secret with value `elder`

The GitHub Actions workflow (`.github/workflows/docker-build.yml`) will automatically detect these secrets and deploy to your cluster on main branch pushes.

## Customization

### Different Namespace

To use a different namespace, update all files:

```bash
# Edit namespace.yaml
name: elder-production  # Change this

# Edit serviceaccount.yaml and rbac.yaml
namespace: elder-production  # Change this
```

Or use the setup script with custom namespace:

```bash
../../scripts/k8s/setup-github-serviceaccount.sh --namespace elder-production
```

### Custom ServiceAccount Name

```bash
../../scripts/k8s/setup-github-serviceaccount.sh \
  --namespace elder \
  --serviceaccount deploy-bot \
  --role-name deploy-bot-role
```

## Security Considerations

1. **Namespace Isolation**: Role is scoped to `elder` namespace only
2. **No ClusterRole**: Prevents cluster-wide access
3. **Token Security**: Kubeconfig should be stored securely in GitHub secrets
4. **Audit Logging**: All actions taken by this ServiceAccount are logged by Kubernetes

## Troubleshooting

### ServiceAccount Creation Failed

```bash
# Check if namespace exists
kubectl get namespace elder

# Check RBAC permissions
kubectl auth can-i create serviceaccounts -n elder --as=system:serviceaccount:elder:github-ci
```

### Permission Denied Errors

```bash
# Verify Role exists
kubectl get role github-ci-deployer -n elder

# Verify RoleBinding exists
kubectl get rolebinding github-ci-deployer -n elder

# Check what ServiceAccount can do
kubectl auth can-i --list --as=system:serviceaccount:elder:github-ci -n elder
```

### Token Generation Issues

For Kubernetes 1.24+, tokens are not automatically created as secrets. Use the setup script which handles both legacy and new token APIs, or manually create a token:

```bash
kubectl create token github-ci -n elder --duration=87600h
```

## References

- Setup script: `../../scripts/k8s/setup-github-serviceaccount.sh`
- GitHub Actions workflow: `../../.github/workflows/docker-build.yml`
- Helm chart: `../../helm/elder/`
- Documentation: `../../docs/deployment/github-actions-k8s.md`

## Support

For issues or questions:
- Check documentation: `docs/deployment/`
- Review GitHub Actions logs: `gh workflow view docker-build`
- Verify cluster connectivity: `kubectl cluster-info`
