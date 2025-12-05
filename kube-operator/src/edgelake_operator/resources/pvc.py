"""PersistentVolumeClaim builder for EdgeLake Operator storage."""

from typing import Any

from ..models.spec import EdgeLakeOperatorSpec


def build_pvcs(
    name: str,
    namespace: str,
    spec: EdgeLakeOperatorSpec,
    resource_names: dict[str, str],
) -> list[dict[str, Any]]:
    """Build PVC resources from EdgeLakeOperator spec.

    Args:
        name: Name of the EdgeLakeOperator CR
        namespace: Namespace of the CR
        spec: Parsed spec from the CR
        resource_names: Generated resource names

    Returns:
        List of PVC manifests as dictionaries
    """
    if not spec.persistence.enabled:
        return []

    labels = _build_labels(name)

    pvcs = [
        _build_pvc(
            resource_names["pvc_anylog"],
            namespace,
            labels,
            spec.persistence.anylog.size,
            spec.persistence.storageClassName,
            spec.persistence.accessMode,
        ),
        _build_pvc(
            resource_names["pvc_blockchain"],
            namespace,
            labels,
            spec.persistence.blockchain.size,
            spec.persistence.storageClassName,
            spec.persistence.accessMode,
        ),
        _build_pvc(
            resource_names["pvc_data"],
            namespace,
            labels,
            spec.persistence.data.size,
            spec.persistence.storageClassName,
            spec.persistence.accessMode,
        ),
        _build_pvc(
            resource_names["pvc_scripts"],
            namespace,
            labels,
            spec.persistence.scripts.size,
            spec.persistence.storageClassName,
            spec.persistence.accessMode,
        ),
    ]

    return pvcs


def _build_pvc(
    pvc_name: str,
    namespace: str,
    labels: dict[str, str],
    size: str,
    storage_class: str | None,
    access_mode: str,
) -> dict[str, Any]:
    """Build a single PVC manifest."""
    pvc: dict[str, Any] = {
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {
            "name": pvc_name,
            "namespace": namespace,
            "labels": labels,
        },
        "spec": {
            "accessModes": [access_mode],
            "resources": {
                "requests": {
                    "storage": size,
                }
            },
        },
    }

    if storage_class:
        pvc["spec"]["storageClassName"] = storage_class

    return pvc


def _build_labels(name: str) -> dict[str, str]:
    """Build standard labels for resources."""
    return {
        "app.kubernetes.io/name": "edgelake-operator",
        "app.kubernetes.io/instance": name,
        "app.kubernetes.io/component": "operator",
        "app.kubernetes.io/managed-by": "edgelake-kube-operator",
    }
