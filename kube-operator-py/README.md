# EdgeLake Kubernetes Operator

A Kubernetes Operator for deploying and managing EdgeLake operator nodes using Custom Resource Definitions (CRDs).

## Overview

This operator uses the [kopf](https://kopf.readthedocs.io/) framework to manage EdgeLake operator nodes via the `EdgeLakeOperator` Custom Resource. When you create an `EdgeLakeOperator` resource, the operator automatically provisions:

- **ConfigMap** - All EdgeLake environment variables
- **Secret** - Credentials (if using inline secrets)
- **PersistentVolumeClaims** - Storage for anylog, blockchain, data, and scripts
- **Deployment** - EdgeLake operator pod
- **Service** - Network access (NodePort, ClusterIP, or LoadBalancer)

## Prerequisites

- Kubernetes 1.19+
- kubectl configured with cluster access
- Helm 3.0+ (optional, for easier deployment)

## Installation

### 1. Install the CRD

```bash
kubectl apply -f config/crd/edgelakeoperator-crd.yaml
```

### 2. Deploy the Operator Controller

```bash
# Create namespace
kubectl create namespace edgelake-system

# Apply RBAC
kubectl apply -f config/rbac/

# Deploy operator (replace IMAGE with your registry)
export IMAGE=100.127.19.27:5000/edgelake-kube-operator:latest
export NAMESPACE=edgelake-system
envsubst < config/operator/deployment.yaml | kubectl apply -f -
```

Or use the Makefile:

```bash
make deploy NAMESPACE=edgelake-system IMAGE_REGISTRY=100.127.19.27:5000
```

### 3. Create an EdgeLakeOperator Resource

```bash
kubectl apply -f config/samples/basic-operator.yaml
```

## Usage

### Basic Example

```yaml
apiVersion: edgelake.io/v1alpha1
kind: EdgeLakeOperator
metadata:
  name: my-operator
  namespace: default
spec:
  general:
    nodeName: my-operator
    companyName: "My Company"

  blockchain:
    ledgerConn: "100.127.19.27:32048"

  operator:
    clusterName: my-cluster
    defaultDbms: my_database
```

### Production Example with PostgreSQL

```yaml
apiVersion: edgelake.io/v1alpha1
kind: EdgeLakeOperator
metadata:
  name: prod-operator
  namespace: edgelake
spec:
  image:
    repository: anylogco/edgelake-network
    tag: "1.3.2500"

  resources:
    limits:
      cpu: "4000m"
      memory: "8Gi"
    requests:
      cpu: "1000m"
      memory: "2Gi"

  persistence:
    enabled: true
    storageClassName: "fast-ssd"
    data:
      size: "100Gi"

  general:
    nodeName: prod-operator
    companyName: "Production Company"

  networking:
    serviceType: LoadBalancer
    serverPort: 32148
    restPort: 32149

  database:
    type: psql
    user: edgelake
    passwordSecretRef:
      name: postgres-credentials
      key: password
    host: postgres-service.database.svc.cluster.local
    port: 5432

  blockchain:
    ledgerConn: "master-node.edgelake.svc.cluster.local:32048"

  operator:
    clusterName: production-cluster
    defaultDbms: production_db
    partitioning:
      enabled: true
      interval: "7 days"
      keep: 4
```

## Configuration Reference

### Required Fields

| Field | Description |
|-------|-------------|
| `spec.general.nodeName` | Unique name for this EdgeLake instance |
| `spec.general.companyName` | Organization name |
| `spec.blockchain.ledgerConn` | Master node connection (host:port) |
| `spec.operator.clusterName` | Cluster identifier |
| `spec.operator.defaultDbms` | Default database name |

### Image Configuration

```yaml
spec:
  image:
    repository: anylogco/edgelake-network  # Docker image
    tag: "1.3.2500"                        # Image tag
    pullPolicy: IfNotPresent               # Always, IfNotPresent, Never
    pullSecretName: my-registry-secret     # For private registries
```

### Networking

```yaml
spec:
  networking:
    serviceType: NodePort        # ClusterIP, NodePort, LoadBalancer
    serverPort: 32148            # TCP server port
    restPort: 32149              # REST API port
    brokerPort: 32150            # MQTT broker port (optional)
    overlayIp: "100.102.221.116" # Tailscale/VPN IP (optional)
```

### Database

```yaml
spec:
  database:
    type: sqlite                    # sqlite or psql
    # For PostgreSQL:
    user: edgelake
    password: mypassword            # Inline (not recommended)
    passwordSecretRef:              # Reference to K8s Secret (recommended)
      name: db-credentials
      key: password
    host: postgres-service
    port: 5432
```

### Persistence

```yaml
spec:
  persistence:
    enabled: true
    storageClassName: "standard"
    retainOnDelete: true           # Keep PVCs when CR deleted
    anylog:
      size: "5Gi"
    blockchain:
      size: "1Gi"
    data:
      size: "10Gi"
    scripts:
      size: "1Gi"
```

### MQTT Data Ingestion

```yaml
spec:
  mqtt:
    enabled: true
    broker: "mqtt-broker.iot.svc.cluster.local"
    port: 1883
    user: "edgelake"
    passwordSecretRef:
      name: mqtt-credentials
      key: password
    message:
      topic: "sensors/+/data"
      dbms: "iot_data"
      table: "bring [table]"
```

### OPC-UA Integration

```yaml
spec:
  opcua:
    enabled: true
    url: "opc.tcp://plc-1.factory.local:4840"
    node: "ns=2;s=DataSet"
    frequency: "5 seconds"
```

## Secrets Management

The operator supports two methods for handling sensitive data:

### Option 1: Inline Secrets (Development)

```yaml
spec:
  database:
    password: "mypassword"   # Stored in operator-created Secret
```

### Option 2: Secret References (Production - Recommended)

```yaml
spec:
  database:
    passwordSecretRef:
      name: existing-secret   # Reference to existing K8s Secret
      key: password
```

## Status

The operator updates the CR status with deployment information:

```yaml
status:
  phase: Running              # Pending, Creating, Running, Updating, Failed
  deploymentName: my-operator-deployment
  serviceName: my-operator-service
  configMapName: my-operator-config
  pvcNames:
    - my-operator-anylog-pvc
    - my-operator-blockchain-pvc
    - my-operator-data-pvc
    - my-operator-scripts-pvc
  endpoints:
    tcp: "my-operator-service.default.svc.cluster.local:32148"
    rest: "my-operator-service.default.svc.cluster.local:32149"
```

## Open Horizon Integration

This operator can be deployed via Open Horizon to Kubernetes edge clusters.

### Publishing to Open Horizon Exchange

```bash
cd oh-integration
export HZN_ORG_ID=myorg
export SERVICE_VERSION=0.1.0
make publish
```

### Node Registration

On the edge node with Kubernetes:

```bash
# Set node policy
hzn policy update -f oh-integration/node.policy.json

# The deployment policy will match and deploy the operator
```

## Development

### Local Development

```bash
# Install dependencies
make install

# Run operator locally (uses current kubeconfig)
make run-local

# In another terminal, create a test CR
kubectl apply -f config/samples/basic-operator.yaml
```

### Building

```bash
# Build Docker image
make build

# Push to registry
make push

# Run linting
make lint

# Run tests
make test
```

## Troubleshooting

### View Operator Logs

```bash
kubectl logs -n edgelake-system -l app.kubernetes.io/name=edgelake-operator -f
```

### Check CR Status

```bash
kubectl get edgelakeoperators
kubectl describe edgelakeoperator my-operator
```

### View Created Resources

```bash
kubectl get deploy,svc,cm,pvc -l app.kubernetes.io/instance=my-operator
```

### Common Issues

**Pod not starting:**
```bash
kubectl describe pod -l app.kubernetes.io/instance=my-operator
kubectl logs -l app.kubernetes.io/instance=my-operator
```

**Cannot connect to master node:**
- Verify `spec.blockchain.ledgerConn` is accessible from the cluster
- Check network policies

**PVC not binding:**
- Verify StorageClass exists: `kubectl get storageclass`
- Check PVC status: `kubectl describe pvc`

## License

Mozilla Public License 2.0
