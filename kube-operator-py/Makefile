.PHONY: help install lint test test-unit test-integ build push deploy undeploy \
        install-crd remove-crd clean run-local oh-publish oh-remove

# Configuration
IMAGE_REGISTRY ?= 100.127.19.27:5000
IMAGE_NAME ?= edgelake-kube-operator
IMAGE_TAG ?= latest
NAMESPACE ?= edgelake-system
FULL_IMAGE ?= $(IMAGE_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

# Detect platform for docker build
ARCH := $(shell uname -m)
ifeq ($(ARCH),arm64)
	PLATFORM := linux/arm64
else
	PLATFORM := linux/amd64
endif

help:
	@echo "EdgeLake Kubernetes Operator Build Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install Python dependencies locally"
	@echo "  make lint         - Run linting checks"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integ   - Run integration tests (requires kind)"
	@echo "  make run-local    - Run operator locally (uses current kubeconfig)"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build        - Build Docker image"
	@echo "  make push         - Push image to registry"
	@echo "  make deploy       - Deploy operator to Kubernetes"
	@echo "  make undeploy     - Remove operator from Kubernetes"
	@echo ""
	@echo "CRD Management:"
	@echo "  make install-crd  - Install CRD to cluster"
	@echo "  make remove-crd   - Remove CRD from cluster"
	@echo ""
	@echo "Open Horizon:"
	@echo "  make oh-publish   - Publish to Open Horizon Exchange"
	@echo "  make oh-remove    - Remove from Open Horizon Exchange"
	@echo ""
	@echo "Configuration:"
	@echo "  IMAGE_REGISTRY=$(IMAGE_REGISTRY)"
	@echo "  IMAGE_NAME=$(IMAGE_NAME)"
	@echo "  IMAGE_TAG=$(IMAGE_TAG)"
	@echo "  NAMESPACE=$(NAMESPACE)"

# ============================================================================
# Development
# ============================================================================

install:
	pip install -r requirements.txt
	pip install -e .

lint:
	ruff check src/
	mypy src/

test: test-unit

test-unit:
	pytest tests/unit -v

test-integ:
	pytest tests/integration -v

run-local:
	kopf run --standalone --namespace=$(NAMESPACE) src/edgelake_operator/operator.py

# ============================================================================
# Build & Deploy
# ============================================================================

build:
	docker build --platform $(PLATFORM) -t $(FULL_IMAGE) .

push: build
	docker push $(FULL_IMAGE)

install-crd:
	kubectl apply -f config/crd/edgelakeoperator-crd.yaml

remove-crd:
	kubectl delete -f config/crd/edgelakeoperator-crd.yaml --ignore-not-found

deploy: install-crd
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f config/rbac/
	IMAGE=$(FULL_IMAGE) NAMESPACE=$(NAMESPACE) envsubst < config/operator/deployment.yaml | kubectl apply -f -

undeploy:
	kubectl delete -f config/operator/deployment.yaml --ignore-not-found
	kubectl delete -f config/rbac/ --ignore-not-found

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# Open Horizon Integration
# ============================================================================

oh-publish:
	@echo "Publishing to Open Horizon Exchange..."
	cd oh-integration && $(MAKE) publish

oh-remove:
	@echo "Removing from Open Horizon Exchange..."
	cd oh-integration && $(MAKE) remove

# ============================================================================
# Samples
# ============================================================================

apply-sample-basic:
	kubectl apply -f config/samples/basic-operator.yaml

apply-sample-psql:
	kubectl apply -f config/samples/production-psql.yaml

apply-sample-mqtt:
	kubectl apply -f config/samples/mqtt-ingestion.yaml

delete-samples:
	kubectl delete -f config/samples/ --ignore-not-found
