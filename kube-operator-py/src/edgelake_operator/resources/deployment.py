"""Deployment builder for EdgeLake Operator pods."""

from typing import Any, Optional

from ..constants import (
    VOLUME_MOUNT_ANYLOG,
    VOLUME_MOUNT_BLOCKCHAIN,
    VOLUME_MOUNT_DATA,
    VOLUME_MOUNT_SCRIPTS,
)
from ..models.spec import EdgeLakeOperatorSpec


def build_deployment(
    name: str,
    namespace: str,
    spec: EdgeLakeOperatorSpec,
    resource_names: dict[str, str],
    config_hash: Optional[str] = None,
) -> dict[str, Any]:
    """Build Deployment resource from EdgeLakeOperator spec.

    Args:
        name: Name of the EdgeLakeOperator CR
        namespace: Namespace of the CR
        spec: Parsed spec from the CR
        resource_names: Generated resource names
        config_hash: Optional config hash for triggering rolling updates

    Returns:
        Deployment manifest as dictionary
    """
    labels = _build_labels(name)
    selector_labels = _build_selector_labels(name)

    annotations = {}
    if config_hash:
        annotations["edgelake.io/config-hash"] = config_hash

    # Container ports
    ports = [
        {
            "name": "tcp-server",
            "containerPort": spec.networking.serverPort,
            "protocol": "TCP",
        },
        {
            "name": "rest-api",
            "containerPort": spec.networking.restPort,
            "protocol": "TCP",
        },
    ]
    if spec.networking.brokerPort:
        ports.append(
            {
                "name": "mqtt-broker",
                "containerPort": spec.networking.brokerPort,
                "protocol": "TCP",
            }
        )

    # Volume mounts
    volume_mounts = [
        {"name": "anylog-volume", "mountPath": VOLUME_MOUNT_ANYLOG},
        {"name": "blockchain-volume", "mountPath": VOLUME_MOUNT_BLOCKCHAIN},
        {"name": "data-volume", "mountPath": VOLUME_MOUNT_DATA},
        {"name": "scripts-volume", "mountPath": VOLUME_MOUNT_SCRIPTS},
    ]

    # Volumes (PVC or emptyDir)
    volumes = _build_volumes(spec, resource_names)

    # Environment from ConfigMap
    env_from = [{"configMapRef": {"name": resource_names["configmap"]}}]

    # Individual env vars for secrets
    env = _build_secret_env_vars(spec, resource_names)

    # Image pull secrets
    image_pull_secrets = []
    if spec.image.pullSecretName:
        image_pull_secrets.append({"name": spec.image.pullSecretName})

    container = {
        "name": f"{name}-container",
        "image": f"{spec.image.repository}:{spec.image.tag}",
        "imagePullPolicy": spec.image.pullPolicy,
        "ports": ports,
        "envFrom": env_from,
        "tty": True,
        "stdin": True,
        "volumeMounts": volume_mounts,
        "resources": {
            "limits": {
                "cpu": spec.resources.limits.cpu,
                "memory": spec.resources.limits.memory,
            },
            "requests": {
                "cpu": spec.resources.requests.cpu,
                "memory": spec.resources.requests.memory,
            },
        },
    }

    if env:
        container["env"] = env

    pod_spec: dict[str, Any] = {
        "containers": [container],
        "volumes": volumes,
    }

    if image_pull_secrets:
        pod_spec["imagePullSecrets"] = image_pull_secrets

    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": resource_names["deployment"],
            "namespace": namespace,
            "labels": labels,
        },
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": selector_labels},
            "template": {
                "metadata": {
                    "labels": selector_labels,
                    "annotations": annotations if annotations else None,
                },
                "spec": pod_spec,
            },
        },
    }


def _build_volumes(
    spec: EdgeLakeOperatorSpec, resource_names: dict[str, str]
) -> list[dict[str, Any]]:
    """Build volume definitions."""
    if spec.persistence.enabled:
        return [
            {
                "name": "anylog-volume",
                "persistentVolumeClaim": {"claimName": resource_names["pvc_anylog"]},
            },
            {
                "name": "blockchain-volume",
                "persistentVolumeClaim": {"claimName": resource_names["pvc_blockchain"]},
            },
            {
                "name": "data-volume",
                "persistentVolumeClaim": {"claimName": resource_names["pvc_data"]},
            },
            {
                "name": "scripts-volume",
                "persistentVolumeClaim": {"claimName": resource_names["pvc_scripts"]},
            },
        ]
    else:
        return [
            {"name": "anylog-volume", "emptyDir": {}},
            {"name": "blockchain-volume", "emptyDir": {}},
            {"name": "data-volume", "emptyDir": {}},
            {"name": "scripts-volume", "emptyDir": {}},
        ]


def _build_secret_env_vars(
    spec: EdgeLakeOperatorSpec, resource_names: dict[str, str]
) -> list[dict[str, Any]]:
    """Build env vars that reference secrets."""
    env = []

    # Database password
    if spec.database.passwordSecretRef:
        env.append(
            {
                "name": "DB_PASSWD",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": spec.database.passwordSecretRef.name,
                        "key": spec.database.passwordSecretRef.key,
                    }
                },
            }
        )
    elif spec.database.password:
        env.append(
            {
                "name": "DB_PASSWD",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": resource_names["secret"],
                        "key": "db-password",
                    }
                },
            }
        )

    # NoSQL password
    if spec.database.nosql.passwordSecretRef:
        env.append(
            {
                "name": "NOSQL_PASSWD",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": spec.database.nosql.passwordSecretRef.name,
                        "key": spec.database.nosql.passwordSecretRef.key,
                    }
                },
            }
        )
    elif spec.database.nosql.password:
        env.append(
            {
                "name": "NOSQL_PASSWD",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": resource_names["secret"],
                        "key": "nosql-password",
                    }
                },
            }
        )

    # MQTT password
    if spec.mqtt.passwordSecretRef:
        env.append(
            {
                "name": "MQTT_PASSWD",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": spec.mqtt.passwordSecretRef.name,
                        "key": spec.mqtt.passwordSecretRef.key,
                    }
                },
            }
        )
    elif spec.mqtt.password:
        env.append(
            {
                "name": "MQTT_PASSWD",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": resource_names["secret"],
                        "key": "mqtt-password",
                    }
                },
            }
        )

    # License key
    if spec.general.licenseKeySecretRef:
        env.append(
            {
                "name": "LICENSE_KEY",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": spec.general.licenseKeySecretRef.name,
                        "key": spec.general.licenseKeySecretRef.key,
                    }
                },
            }
        )
    elif spec.general.licenseKey:
        env.append(
            {
                "name": "LICENSE_KEY",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": resource_names["secret"],
                        "key": "license-key",
                    }
                },
            }
        )

    return env


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
