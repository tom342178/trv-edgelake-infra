.PHONY: help publish remove verify

# Configuration
HZN_ORG_ID ?= myorg
SERVICE_VERSION ?= 0.1.0
ARCH ?= amd64
DOCKER_IMAGE_BASE ?= 100.127.19.27:5000/edgelake-kube-operator

# Exchange settings
HZN_EXCHANGE_URL ?= http://100.127.19.27:3090/v1

help:
	@echo "Open Horizon Integration Commands"
	@echo ""
	@echo "  make publish   - Publish service to OH Exchange"
	@echo "  make remove    - Remove service from OH Exchange"
	@echo "  make verify    - Verify service in Exchange"
	@echo ""
	@echo "Configuration:"
	@echo "  HZN_ORG_ID=$(HZN_ORG_ID)"
	@echo "  SERVICE_VERSION=$(SERVICE_VERSION)"
	@echo "  ARCH=$(ARCH)"
	@echo "  DOCKER_IMAGE_BASE=$(DOCKER_IMAGE_BASE)"

publish:
	@echo "Publishing EdgeLake K8s Operator to Open Horizon Exchange..."
	@echo "Organization: $(HZN_ORG_ID)"
	@echo "Version: $(SERVICE_VERSION)"
	@echo ""
	# Export variables for envsubst
	export HZN_ORG_ID=$(HZN_ORG_ID) && \
	export SERVICE_VERSION=$(SERVICE_VERSION) && \
	export ARCH=$(ARCH) && \
	export DOCKER_IMAGE_BASE=$(DOCKER_IMAGE_BASE) && \
	envsubst < service.definition.json > /tmp/service.definition.json && \
	hzn exchange service publish -f /tmp/service.definition.json -O
	@echo ""
	@echo "Publishing service policy..."
	hzn exchange service addpolicy -f service.policy.json \
		$(HZN_ORG_ID)/service-edgelake-kube-operator_$(SERVICE_VERSION)_$(ARCH)
	@echo ""
	@echo "Publishing deployment policy..."
	export HZN_ORG_ID=$(HZN_ORG_ID) && \
	export SERVICE_VERSION=$(SERVICE_VERSION) && \
	envsubst < deployment.policy.json > /tmp/deployment.policy.json && \
	hzn exchange deployment addpolicy -f /tmp/deployment.policy.json \
		edgelake-kube-operator-policy

remove:
	@echo "Removing EdgeLake K8s Operator from Open Horizon Exchange..."
	-hzn exchange deployment removepolicy edgelake-kube-operator-policy
	-hzn exchange service remove \
		$(HZN_ORG_ID)/service-edgelake-kube-operator_$(SERVICE_VERSION)_$(ARCH)

verify:
	@echo "Verifying service in Exchange..."
	hzn exchange service list $(HZN_ORG_ID)/service-edgelake-kube-operator_$(SERVICE_VERSION)_$(ARCH)
	@echo ""
	@echo "Verifying deployment policy..."
	hzn exchange deployment listpolicy edgelake-kube-operator-policy
