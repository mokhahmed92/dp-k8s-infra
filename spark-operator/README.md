# Spark on Kubernetes with K3d

A production-ready data platform on Kubernetes using K3d, Spark Operator, and multi-tenant architecture.

## 🚀 Current Cluster Status

### Cluster Information
- **Platform**: K3d on WSL2
- **Kubernetes Version**: v1.31.4+k3s1
- **Nodes**: 
  - 1 control-plane node (k3d-data-platform-cluster-server-0)
  - 2 worker nodes (k3d-data-platform-cluster-agent-0, k3d-data-platform-cluster-agent-1)
- **Status**: ✅ All nodes Ready

### Deployed Components

#### 1. Spark Operator
- **Namespace**: `spark-operator`
- **Version**: 2.3.0
- **Status**: ✅ Running
- **Components**:
  - Controller: 1/1 replica running
  - Webhook: 1/1 replica running with admission webhook enabled
- **Configuration**:
  - Watches namespaces: `team-alpha`, `team-beta`
  - Metrics enabled on port 8080
  - Leader election enabled for HA

#### 2. Multi-Tenant Setup
- **Team Namespaces**: 
  - `team-alpha`: Active with completed PySpark job
  - `team-beta`: Active with completed Scala Spark job
- **Service Accounts**:
  - `team-alpha-sa` in team-alpha namespace
  - `team-beta-sa` in team-beta namespace
- **RBAC**: Full permissions for Spark operations and pod management
- **Resource Quotas** (per team):
  - CPU: 4 cores (requests), 8 cores (limits)
  - Memory: 8Gi (requests), 16Gi (limits)
  - Max Pods: 10

### Completed Spark Applications

| Namespace | Application | Type | Status | Result |
|-----------|------------|------|--------|--------|
| team-alpha | pyspark-pi-test | PySpark | ✅ COMPLETED | Pi ≈ 3.138040 |
| team-beta | spark-pi-test | Scala | ✅ COMPLETED | Pi ≈ 3.141651 |

## 📁 Project Structure

```
spark-operators-on-k8s/
├── k3d/
│   └── k3d-config.yaml              # K3d cluster configuration
├── spark-operator/
│   ├── namespaces.yaml              # Namespace definitions
│   ├── rbac.yaml                    # RBAC roles and bindings
│   ├── resource-quotas.yaml         # Resource quota limits
│   ├── values.yaml                  # Spark Operator Helm values
│   └── values-updated.yaml          # Alternative values configuration
├── spark-jobs/
│   ├── team-alpha-pyspark-test.yaml # PySpark test job
│   └── team-beta-spark-test.yaml    # Scala Spark test job
├── CLAUDE.md                        # Claude AI assistant instructions
└── README.md                        # This file
```

## 🛠️ Quick Start

### Prerequisites
- Docker Desktop or Docker Engine
- kubectl command-line tool
- k3d
- Helm 3

### Installing k3d

#### Windows (PowerShell)
```powershell
choco install k3d
# or
winget install k3d
```

#### Linux/MacOS
```bash
wget -q -O - https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

### Installing Helm

#### Linux/WSL
```bash
curl -fsSL https://get.helm.sh/helm-v3.18.6-linux-amd64.tar.gz | tar -xz
mv linux-amd64/helm ~/.local/bin/
export PATH=$PATH:~/.local/bin
```

### 1. Create K3d Cluster
```bash
cd k3d
k3d cluster create -c k3d-config.yaml

# Verify cluster
kubectl get nodes
kubectl cluster-info
```

### 2. Apply Kubernetes Resources
```bash
# Create namespaces
kubectl apply -f spark-operator/namespaces.yaml

# Apply RBAC
kubectl apply -f spark-operator/rbac.yaml

# Apply resource quotas
kubectl apply -f spark-operator/resource-quotas.yaml
```

### 3. Install Spark Operator
```bash
# Add Helm repository
helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update

# Install with custom values
helm install spark-operator spark-operator/spark-operator \
  --namespace spark-operator \
  --create-namespace \
  -f spark-operator/values.yaml

# Verify installation
kubectl get pods -n spark-operator
```

### 4. Submit Spark Jobs

#### Team Alpha (PySpark)
```bash
kubectl apply -f spark-jobs/team-alpha-pyspark-test.yaml
kubectl get sparkapplication -n team-alpha -w
```

#### Team Beta (Scala)
```bash
kubectl apply -f spark-jobs/team-beta-spark-test.yaml
kubectl get sparkapplication -n team-beta -w
```

## 📊 Monitoring

### Check Spark Operator
```bash
# Operator status
kubectl get pods -n spark-operator

# Operator logs
kubectl logs -n spark-operator deployment/spark-operator-controller

# Verify watched namespaces (should show team-alpha,team-beta)
kubectl logs -n spark-operator deployment/spark-operator-controller | head -5 | grep namespace
```

### Check Applications
```bash
# All Spark applications
kubectl get sparkapplications -A

# Specific application details
kubectl describe sparkapplication pyspark-pi-test -n team-alpha

# Application logs
kubectl logs <driver-pod-name> -n <namespace>
```

### Resource Usage
```bash
# Check quota usage
kubectl describe quota -n team-alpha
kubectl describe quota -n team-beta

# Pod resources (requires metrics-server)
kubectl top pods -n team-alpha
kubectl top pods -n team-beta
```

## 🔧 Configuration Details

### Spark Operator Values (`spark-operator/values.yaml`)
Key configurations:
- `spark.jobNamespaces`: Restricts operator to watch only team-alpha and team-beta
- `webhook.enable`: Enables admission webhook for validation
- `metrics.enable`: Enables Prometheus metrics endpoint
- `controller.resources`: Sets resource limits for operator pods

### RBAC Configuration (`spark-operator/rbac.yaml`)
Each team service account has permissions to:
- Create, manage, and delete Spark applications
- Create and manage pods, services, configmaps
- View pod logs and exec into pods
- Manage persistent volume claims

### Resource Quotas (`spark-operator/resource-quotas.yaml`)
Per-team limits ensure fair resource distribution:
- Prevents resource hogging
- Ensures predictable performance
- Enables cost control

### Spark Application Configuration

#### Required Fields for Resource Quotas
When resource quotas are enabled, all pods must specify:
- `driver.coreLimit`: CPU limit for driver
- `executor.coreLimit`: CPU limit for executors
- Memory specifications for both driver and executor

## 🚨 Troubleshooting

### Image Pull Issues
If pods show `ImagePullBackOff`:
- Verify image name and tag
- Check network connectivity
- Working images: `apache/spark:3.5.0`

### Permission Errors
If Spark jobs fail with permission errors:
```bash
# Check service account exists
kubectl get sa -n <namespace>

# Verify RBAC bindings
kubectl get rolebindings -n <namespace>

# Ensure service account is specified in YAML
```

### Resource Quota Violations
Error: "must specify limits.cpu"
- Add `coreLimit` to driver and executor specs
- Ensure memory limits don't exceed quotas
- Check current usage: `kubectl describe quota -n <namespace>`

### Spark Operator Not Watching Namespaces
If applications stay in pending state:
```bash
# Check operator is watching correct namespaces
kubectl logs -n spark-operator deployment/spark-operator-controller | grep namespace

# Should show: --namespaces=team-alpha,team-beta
```

## 🧹 Cleanup

### Delete Spark Applications
```bash
kubectl delete sparkapplication --all -n team-alpha
kubectl delete sparkapplication --all -n team-beta
```

### Uninstall Spark Operator
```bash
helm uninstall spark-operator -n spark-operator
```

### Delete Cluster
```bash
k3d cluster delete data-platform-cluster
```

## 🔮 Future Enhancements

- [ ] Add Volcano scheduler for advanced scheduling
- [ ] Integrate MinIO for S3-compatible storage
- [ ] Set up Prometheus + Grafana for metrics visualization
- [ ] Add Spark History Server for job history
- [ ] Implement CI/CD pipeline for Spark jobs
- [ ] Add data pipeline examples with real datasets
- [ ] Configure autoscaling for Spark executors
- [ ] Add network policies for enhanced security

## 📚 References

- [K3d Documentation](https://k3d.io/)
- [Spark Operator Documentation](https://github.com/kubeflow/spark-operator)
- [Apache Spark on Kubernetes](https://spark.apache.org/docs/latest/running-on-kubernetes.html)
- [Kubernetes Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)

## 📝 License

This project is for demonstration and educational purposes.

---
**Last Updated**: September 3, 2025  
**Cluster Status**: ✅ Operational  
**Author**: Data Platform Team