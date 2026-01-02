"""Service builder for EdgeLake Operator networking."""

from typing import Any

from ..models.spec import EdgeLakeOperatorSpec


def build_service(
    name: str,
    namespace: str,
    spec: EdgeLakeOperatorSpec,
    resource_names: dict[str, str],
) -> dict[str, Any]:
    """Build Service resource from EdgeLakeOperator spec.

    Args:
        name: Name of the EdgeLakeOperator CR
        namespace: Namespace of the CR
        spec: Parsed spec from the CR
        resource_names: Generated resource names

    Returns:
        Service manifest as dictionary
    """
    labels = _build_labels(name)
    selector_labels = _build_selector_labels(name)

    # Build ports
    ports = [
        {
            "name": "tcp-server",
            "port": spec.networking.serverPort,
            "targetPort": spec.networking.serverPort,
            "protocol": "TCP",
        },
        {
            "name": "rest-api",
            "port": spec.networking.restPort,
            "targetPort": spec.networking.restPort,
            "protocol": "TCP",
        },
    ]

    # Add nodePort for NodePort service type
    if spec.networking.serviceType == "NodePort":
        ports[0]["nodePort"] = spec.networking.serverPort
        ports[1]["nodePort"] = spec.networking.restPort

    # Add broker port if configured
    if spec.networking.brokerPort:
        broker_port: dict[str, Any] = {
            "name": "mqtt-broker",
            "port": spec.networking.brokerPort,
            "targetPort": spec.networking.brokerPort,
            "protocol": "TCP",
        }
        if spec.networking.serviceType == "NodePort":
            broker_port["nodePort"] = spec.networking.brokerPort
        ports.append(broker_port)

    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": resource_names["service"],
            "namespace": namespace,
            "labels": labels,
        },
        "spec": {
            "type": spec.networking.serviceType,
            "selector": selector_labels,
            "ports": ports,
        },
    }


def _build_labels(name: str) -> dict[str, str]:
    """Build standard labels for resources."""
    return {
        "app.kubernetes.io/name": "edgelake-operator",
        "app.kubernetes.io/instance": name,
        "app.kubernetes.io/component": "operator",
        "app.kubernetes.io/managed-by": "edgelake-kube-operator",
    }


def _build_selector_labels(name: str) -> dict[str, str]:
    """Build selector labels for pods."""
    return {
        "app.kubernetes.io/name": "edgelake-operator",
        "app.kubernetes.io/instance": name,
        "app": name,
    }
