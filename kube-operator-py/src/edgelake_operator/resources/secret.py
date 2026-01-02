"""Secret builder for EdgeLake Operator credentials."""

import base64
from typing import Any

from ..models.spec import EdgeLakeOperatorSpec


def build_secret(
    name: str,
    namespace: str,
    spec: EdgeLakeOperatorSpec,
    resource_names: dict[str, str],
) -> dict[str, Any] | None:
    """Build Secret resource from EdgeLakeOperator spec.

    This creates a secret only for inline secrets that need to be stored.
    If all credentials use secretKeyRef, no secret is created.

    Args:
        name: Name of the EdgeLakeOperator CR
        namespace: Namespace of the CR
        spec: Parsed spec from the CR
        resource_names: Generated resource names

    Returns:
        Secret manifest as dictionary, or None if no secrets needed
    """
    data = {}

    # Database password (only if inline and no secretRef)
    if spec.database.password and not spec.database.passwordSecretRef:
        data["db-password"] = _encode(spec.database.password)

    # NoSQL password
    if spec.database.nosql.password and not spec.database.nosql.passwordSecretRef:
        data["nosql-password"] = _encode(spec.database.nosql.password)

    # MQTT password
    if spec.mqtt.password and not spec.mqtt.passwordSecretRef:
        data["mqtt-password"] = _encode(spec.mqtt.password)

    # License key
    if spec.general.licenseKey and not spec.general.licenseKeySecretRef:
        data["license-key"] = _encode(spec.general.licenseKey)

    if not data:
        return None

    return {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": resource_names["secret"],
            "namespace": namespace,
            "labels": _build_labels(name),
        },
        "type": "Opaque",
        "data": data,
    }


def _encode(value: str) -> str:
    """Base64 encode a string for Kubernetes secret."""
    return base64.b64encode(value.encode()).decode()


def _build_labels(name: str) -> dict[str, str]:
    """Build standard labels for resources."""
    return {
        "app.kubernetes.io/name": "edgelake-operator",
        "app.kubernetes.io/instance": name,
        "app.kubernetes.io/component": "operator",
        "app.kubernetes.io/managed-by": "edgelake-kube-operator",
    }
