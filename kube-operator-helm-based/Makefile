# EdgeLake Kubernetes Operator (Helm-based)
# Makefile for building and deploying the operator

# Image configuration
IMG ?= edgelake-operator:latest
REGISTRY ?= docker.io/yourorg

# Kubernetes configuration
NAMESPACE ?= edgelake-operator-system

# Operator SDK version for reference
OPERATOR_SDK_VERSION ?= v1.37.0
HELM_OPERATOR_VERSION ?= v1.37.0

.PHONY: help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: lint
lint: ## Lint Helm chart
	helm lint helm-charts/edgelake-operator

.PHONY: template
template: ## Template Helm chart for debugging
	helm template edgelake-operator helm-charts/edgelake-operator

.PHONY: template-values
template-values: ## Template Helm chart with sample values
	helm template edgelake-operator helm-charts/edgelake-operator -f config/samples/edgelake_v1alpha1_basic.yaml

##@ Build

.PHONY: docker-build
docker-build: ## Build operator docker image
	docker build -t $(IMG) .

.PHONY: docker-push
docker-push: ## Push operator docker image
	docker push $(IMG)

.PHONY: docker-build-push
docker-build-push: docker-build docker-push ## Build and push operator docker image

##@ Deployment

.PHONY: install-crd
install-crd: ## Install CRDs into the cluster
	kubectl apply -f config/crd/

.PHONY: uninstall-crd
uninstall-crd: ## Uninstall CRDs from the cluster
	kubectl delete -f config/crd/

.PHONY: deploy
deploy: ## Deploy operator to the cluster
	@echo "Creating namespace..."
	kubectl apply -f config/manager/manager.yaml
	@echo "Deploying RBAC..."
	kubectl apply -f config/rbac/
	@echo "Operator deployed successfully"

.PHONY: undeploy
undeploy: ## Undeploy operator from the cluster
	kubectl delete -f config/rbac/ --ignore-not-found=true
	kubectl delete -f config/manager/manager.yaml --ignore-not-found=true

.PHONY: install
install: install-crd deploy ## Install CRDs and deploy operator

.PHONY: uninstall
uninstall: undeploy uninstall-crd ## Uninstall CRDs and undeploy operator

##@ Samples

.PHONY: deploy-sample-basic
deploy-sample-basic: ## Deploy basic sample EdgeLakeOperator
	kubectl apply -f config/samples/edgelake_v1alpha1_basic.yaml

.PHONY: deploy-sample-production
deploy-sample-production: ## Deploy production sample EdgeLakeOperator
	kubectl create namespace edgelake --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f config/samples/edgelake_v1alpha1_production.yaml

.PHONY: deploy-sample-mqtt
deploy-sample-mqtt: ## Deploy MQTT ingestion sample EdgeLakeOperator
	kubectl create namespace iot-data --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f config/samples/edgelake_v1alpha1_mqtt_ingestion.yaml

.PHONY: delete-samples
delete-samples: ## Delete all sample EdgeLakeOperators
	kubectl delete -f config/samples/ --ignore-not-found=true

##@ Local Development

.PHONY: run-local
run-local: ## Run operator locally (requires helm-operator binary)
	@echo "Running operator locally..."
	@echo "Make sure you have installed CRDs first: make install-crd"
	helm-operator run --watches-file=./watches.yaml

##@ Utilities

.PHONY: logs
logs: ## Show operator logs
	kubectl logs -n $(NAMESPACE) -l control-plane=controller-manager -f

.PHONY: status
status: ## Show operator status
	@echo "=== Operator Deployment ==="
	kubectl get deployment -n $(NAMESPACE) edgelake-operator-controller-manager
	@echo ""
	@echo "=== Operator Pods ==="
	kubectl get pods -n $(NAMESPACE) -l control-plane=controller-manager
	@echo ""
	@echo "=== EdgeLakeOperator CRs ==="
	kubectl get edgelakeoperators --all-namespaces

.PHONY: describe-cr
describe-cr: ## Describe EdgeLakeOperator CRs (NAME required)
ifndef NAME
	$(error NAME is not set. Usage: make describe-cr NAME=<cr-name> NAMESPACE=<namespace>)
endif
	kubectl describe edgelakeoperator $(NAME) -n $(or $(CR_NAMESPACE),default)

.PHONY: clean
clean: ## Clean up local artifacts
	rm -rf bin/

##@ Bundle (OLM)

.PHONY: bundle
bundle: ## Generate OLM bundle manifests
	@echo "OLM bundle generation requires operator-sdk CLI"
	@echo "Install operator-sdk and run:"
	@echo "  operator-sdk generate kustomize manifests -q"
	@echo "  operator-sdk bundle generate"

##@ Setup

.PHONY: operator-sdk
operator-sdk: ## Install operator-sdk CLI
	@echo "Installing operator-sdk $(OPERATOR_SDK_VERSION)..."
	@curl -LO https://github.com/operator-framework/operator-sdk/releases/download/$(OPERATOR_SDK_VERSION)/operator-sdk_darwin_amd64
	@chmod +x operator-sdk_darwin_amd64
	@sudo mv operator-sdk_darwin_amd64 /usr/local/bin/operator-sdk
	@echo "operator-sdk installed successfully"

.PHONY: helm-operator
helm-operator: ## Install helm-operator binary for local development
	@echo "Installing helm-operator $(HELM_OPERATOR_VERSION)..."
	@curl -LO https://github.com/operator-framework/operator-sdk/releases/download/$(HELM_OPERATOR_VERSION)/helm-operator_darwin_amd64
	@chmod +x helm-operator_darwin_amd64
	@sudo mv helm-operator_darwin_amd64 /usr/local/bin/helm-operator
	@echo "helm-operator installed successfully"
