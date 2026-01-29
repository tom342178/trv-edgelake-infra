# Build the helm-operator image
FROM quay.io/operator-framework/helm-operator:v1.37.0

# Required to run on OpenShift
ENV HOME=/opt/helm
WORKDIR ${HOME}

# Copy watches.yaml
COPY watches.yaml ${HOME}/watches.yaml

# Copy Helm chart
COPY helm-charts/ ${HOME}/helm-charts/
