#!/bin/bash
# Script to configure insecure registry on all nodes

REGISTRY_IP="192.168.7.21:30500"

# For containerd (Kubernetes default)
cat > /tmp/registry-config.toml <<EOF
[plugins."io.containerd.grpc.v1.cri".registry.mirrors]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."${REGISTRY_IP}"]
    endpoint = ["http://${REGISTRY_IP}"]

[plugins."io.containerd.grpc.v1.cri".registry.configs."${REGISTRY_IP}".tls]
  insecure_skip_verify = true
EOF

# Append to containerd config if not already present
if ! grep -q "${REGISTRY_IP}" /etc/containerd/config.toml 2>/dev/null; then
    cat /tmp/registry-config.toml >> /etc/containerd/config.toml
    systemctl restart containerd
fi

# For Docker daemon (if present)
if [ -f /etc/docker/daemon.json ]; then
    if ! grep -q "insecure-registries" /etc/docker/daemon.json; then
        jq '. + {"insecure-registries": ["'${REGISTRY_IP}'"]}' /etc/docker/daemon.json > /tmp/daemon.json
        mv /tmp/daemon.json /etc/docker/daemon.json
        systemctl restart docker
    fi
else
    echo '{"insecure-registries": ["'${REGISTRY_IP}'"]}' > /etc/docker/daemon.json
    systemctl restart docker 2>/dev/null || true
fi

echo "Registry ${REGISTRY_IP} configured as insecure on $(hostname)"
