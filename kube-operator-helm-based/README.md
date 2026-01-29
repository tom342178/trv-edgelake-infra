# EdgeLake Kubernetes Operator (Helm-based)

A Kubernetes Operator for deploying and managing EdgeLake operator nodes, built using the Operator SDK Helm plugin. This operator wraps the `edgelake-operator` Helm chart and provides a Kubernetes-native way to manage EdgeLake deployments through Custom Resources.

## Overview

This operator uses the [Helm Operator](https://sdk.operatorframework.io/docs/building-operators/helm/) from the Operator SDK to automatically reconcile EdgeLake deployments based on Custom Resource definitions. When you create, update, or delete an `EdgeLakeOperator` CR, the operator manages the corresponding Helm release.

## Prerequisites

- Kubernetes cluster (v1.19+)
- kubectl configured to access your cluster
- Docker (for building the operator image)
- Helm 3 (optional, for local testing)

## Quick Start

### 1. Install CRDs

```bash
make install-crd
```

### 2. Build and Push Operator Image

```bash
# Set your registry
export IMG=your-registry/edgelake-operator:v1.0.0

# Build and push
make docker-build-push IMG=$IMG
```

### 3. Update Manager Image

Edit `config/manager/manager.yaml` and set the image to your pushed image:

```yaml
containers:
  - name: manager
    image: your-registry/edgelake-operator:v1.0.0
```

### 4. Deploy Operator

```bash
make deploy
```

### 5. Create an EdgeLakeOperator Instance

```bash
# Basic deployment
make deploy-sample-basic

# Or apply a custom CR
kubectl apply -f config/samples/edgelake_v1alpha1_basic.yaml
```

## Directory Structure

```
kube-operator-helm-based/
├── Dockerfile                    # Operator container image
├── Makefile                      # Build and deployment commands
├── watches.yaml                  # CRD to Helm chart mapping
├── config/
│   ├── crd/                      # Custom Resource Definition
│   │   └── edgelake.trv.io_edgelakeoperators.yaml
│   ├── manager/                  # Operator deployment
│   │   └── manager.yaml
│   ├── rbac/                     # RBAC configuration
│   │   ├── role.yaml
│   │   ├── role_binding.yaml
│   │   ├── service_account.yaml
│   │   ├── leader_election_role.yaml
│   │   └── leader_election_role_binding.yaml
│   └── samples/                  # Example EdgeLakeOperator CRs
│       ├── edgelake_v1alpha1_basic.yaml
│       ├── edgelake_v1alpha1_production.yaml
│       └── edgelake_v1alpha1_mqtt_ingestion.yaml
└── helm-charts/
    └── edgelake-operator/        # The Helm chart being managed
```

## Custom Resource Definition

The `EdgeLakeOperator` CRD allows you to configure all aspects of an EdgeLake operator node deployment:

```yaml
apiVersion: edgelake.trv.io/v1alpha1
kind: EdgeLakeOperator
metadata:
  name: my-edgelake-operator
  namespace: default
spec:
  # Kubernetes metadata
  metadata:
    hostname: edgelake-operator
    app_name: edgelake-operator
    service_type: NodePort

  # Container image
  image:
    repository: anylogco/edgelake-network
    tag: "1.3.2500"

  # Persistent storage
  persistence:
    enabled: true
    data:
      size: 10Gi

  # Resource limits
  resources:
    limits:
      cpu: "2000m"
      memory: "4Gi"

  # EdgeLake node configuration
  node_configs:
    general:
      NODE_TYPE: operator
      COMPANY_NAME: "My Company"
    networking:
      ANYLOG_SERVER_PORT: 32148
      ANYLOG_REST_PORT: 32149
    blockchain:
      LEDGER_CONN: "master-ip:32048"
    operator:
      CLUSTER_NAME: my-cluster
      DEFAULT_DBMS: my_data
```

## Configuration Reference

### metadata

| Field | Description | Default |
|-------|-------------|---------|
| `namespace` | Kubernetes namespace | `default` |
| `hostname` | Deployment hostname | `edgelake-operator` |
| `app_name` | Application name | `edgelake-operator` |
| `service_type` | Service type (ClusterIP, NodePort, LoadBalancer) | `NodePort` |

### image

| Field | Description | Default |
|-------|-------------|---------|
| `repository` | Docker image repository | `anylogco/edgelake-network` |
| `tag` | Image tag | `1.3.2500` |
| `pull_policy` | Image pull policy | `IfNotPresent` |

### persistence

| Field | Description | Default |
|-------|-------------|---------|
| `enabled` | Enable persistent volumes | `true` |
| `storageClassName` | Storage class name | `""` (default) |
| `anylog.size` | AnyLog volume size | `5Gi` |
| `blockchain.size` | Blockchain volume size | `1Gi` |
| `data.size` | Data volume size | `10Gi` |
| `scripts.size` | Scripts volume size | `1Gi` |

### node_configs

See the [Helm chart values.yaml](helm-charts/edgelake-operator/values.yaml) for complete configuration options including:

- **general**: Node type, name, company
- **networking**: Ports, overlay IP, thread configuration
- **database**: SQLite or PostgreSQL configuration
- **blockchain**: Master node connection, sync settings
- **operator**: Cluster name, partitioning, HA settings
- **mqtt**: MQTT client configuration for data ingestion
- **opcua**: OPC-UA client settings
- **monitoring**: Node monitoring options
- **advanced**: Performance tuning options

## Sample Deployments

### Basic Development

```bash
kubectl apply -f config/samples/edgelake_v1alpha1_basic.yaml
```

### Production with PostgreSQL

```bash
kubectl create namespace edgelake
kubectl apply -f config/samples/edgelake_v1alpha1_production.yaml
```

### MQTT Data Ingestion

```bash
kubectl create namespace iot-data
kubectl apply -f config/samples/edgelake_v1alpha1_mqtt_ingestion.yaml
```

## Operations

### View Operator Status

```bash
make status
```

### View Operator Logs

```bash
make logs
```

### List All EdgeLakeOperator Instances

```bash
kubectl get edgelakeoperators --all-namespaces
# Or using short name
kubectl get elo --all-namespaces
```

### Describe an Instance

```bash
kubectl describe edgelakeoperator my-edgelake-operator -n default
```

### Delete an Instance

```bash
kubectl delete edgelakeoperator my-edgelake-operator -n default
```

## Local Development

### Run Operator Locally

For development, you can run the operator outside the cluster:

1. Install the CRDs:
   ```bash
   make install-crd
   ```

2. Install helm-operator binary:
   ```bash
   make helm-operator
   ```

3. Run the operator:
   ```bash
   make run-local
   ```

### Test Helm Chart

```bash
# Lint the chart
make lint

# Render templates
make template

# Render with sample values
make template-values
```

## Uninstall

```bash
# Remove all EdgeLakeOperator instances first
make delete-samples

# Uninstall operator and CRDs
make uninstall
```

## Troubleshooting

### Operator Pod Not Starting

Check the operator logs:
```bash
kubectl logs -n edgelake-operator-system -l control-plane=controller-manager
```

### EdgeLake Pod Issues

Check the EdgeLake container logs:
```bash
kubectl logs -n <namespace> <pod-name>
```

### CR Status Shows Errors

```bash
kubectl describe edgelakeoperator <name> -n <namespace>
```

Look at the `status.conditions` field for error messages.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                  │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐   │
│  │          EdgeLake Operator (Helm)            │   │
│  │  ┌─────────────┐   ┌──────────────────────┐ │   │
│  │  │ watches.yaml│──▶│  helm-operator       │ │   │
│  │  └─────────────┘   │  runtime             │ │   │
│  │                    └──────────┬───────────┘ │   │
│  └───────────────────────────────┼─────────────┘   │
│                                  │                  │
│                    ┌─────────────▼─────────────┐   │
│                    │     EdgeLakeOperator CR    │   │
│                    │  apiVersion: edgelake.trv.io/v1alpha1 │
│                    │  kind: EdgeLakeOperator    │   │
│                    └─────────────┬─────────────┘   │
│                                  │                  │
│         ┌────────────────────────┼────────────────┐│
│         │        Helm Release                     ││
│         │  ┌───────────┐  ┌───────────┐          ││
│         │  │ ConfigMap │  │  Service  │          ││
│         │  └───────────┘  └───────────┘          ││
│         │  ┌───────────┐  ┌───────────┐          ││
│         │  │Deployment │  │   PVCs    │          ││
│         │  └─────┬─────┘  └───────────┘          ││
│         │        │                                ││
│         │  ┌─────▼─────┐                         ││
│         │  │ EdgeLake  │                         ││
│         │  │   Pod     │                         ││
│         │  └───────────┘                         ││
│         └─────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

## Related Documentation

- [EdgeLake Documentation](https://github.com/EdgeLake/EdgeLake)
- [Operator SDK Helm Guide](https://sdk.operatorframework.io/docs/building-operators/helm/)
- [Helm Chart values.yaml](helm-charts/edgelake-operator/values.yaml)
