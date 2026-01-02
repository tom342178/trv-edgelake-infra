"""Kubernetes client utilities for the EdgeLake Operator."""

import logging
from typing import Any

import kubernetes
from kubernetes import client
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


def get_k8s_client() -> client.ApiClient:
    """Get Kubernetes API client.

    Attempts to load in-cluster config first, falls back to kubeconfig.
    """
    try:
        kubernetes.config.load_incluster_config()
        logger.debug("Loaded in-cluster Kubernetes config")
    except kubernetes.config.ConfigException:
        kubernetes.config.load_kube_config()
        logger.debug("Loaded kubeconfig")

    return client.ApiClient()


async def apply_resource(resource: dict[str, Any], namespace: str) -> dict[str, Any]:
    """Apply a Kubernetes resource (create or update).

    Args:
        resource: Resource manifest as dictionary
        namespace: Namespace for the resource

    Returns:
        The created/updated resource
    """
    kind = resource["kind"]
    name = resource["metadata"]["name"]
    api_version = resource["apiVersion"]

    logger.info(f"Applying {kind}/{name} in namespace {namespace}")

    try:
        if kind == "ConfigMap":
            return await _apply_configmap(resource, namespace)
        elif kind == "Secret":
            return await _apply_secret(resource, namespace)
        elif kind == "Service":
            return await _apply_service(resource, namespace)
        elif kind == "Deployment":
            return await _apply_deployment(resource, namespace)
        elif kind == "PersistentVolumeClaim":
            return await _apply_pvc(resource, namespace)
        else:
            raise ValueError(f"Unsupported resource kind: {kind}")
    except ApiException as e:
        logger.error(f"Failed to apply {kind}/{name}: {e}")
        raise


async def delete_resource(kind: str, name: str, namespace: str) -> bool:
    """Delete a Kubernetes resource.

    Args:
        kind: Resource kind
        name: Resource name
        namespace: Namespace

    Returns:
        True if deleted, False if not found
    """
    logger.info(f"Deleting {kind}/{name} from namespace {namespace}")

    try:
        if kind == "ConfigMap":
            api = client.CoreV1Api()
            api.delete_namespaced_config_map(name, namespace)
        elif kind == "Secret":
            api = client.CoreV1Api()
            api.delete_namespaced_secret(name, namespace)
        elif kind == "Service":
            api = client.CoreV1Api()
            api.delete_namespaced_service(name, namespace)
        elif kind == "Deployment":
            api = client.AppsV1Api()
            api.delete_namespaced_deployment(name, namespace)
        elif kind == "PersistentVolumeClaim":
            api = client.CoreV1Api()
            api.delete_namespaced_persistent_volume_claim(name, namespace)
        else:
            logger.warning(f"Unknown resource kind: {kind}")
            return False

        logger.info(f"Deleted {kind}/{name}")
        return True

    except ApiException as e:
        if e.status == 404:
            logger.debug(f"{kind}/{name} not found, nothing to delete")
            return False
        raise


async def _apply_configmap(resource: dict[str, Any], namespace: str) -> dict[str, Any]:
    """Apply a ConfigMap resource."""
    api = client.CoreV1Api()
    name = resource["metadata"]["name"]

    try:
        existing = api.read_namespaced_config_map(name, namespace)
        resource["metadata"]["resourceVersion"] = existing.metadata.resource_version
        result = api.replace_namespaced_config_map(name, namespace, resource)
        logger.debug(f"Updated ConfigMap/{name}")
    except ApiException as e:
        if e.status == 404:
            result = api.create_namespaced_config_map(namespace, resource)
            logger.debug(f"Created ConfigMap/{name}")
        else:
            raise

    return result.to_dict()


async def _apply_secret(resource: dict[str, Any], namespace: str) -> dict[str, Any]:
    """Apply a Secret resource."""
    api = client.CoreV1Api()
    name = resource["metadata"]["name"]

    try:
        existing = api.read_namespaced_secret(name, namespace)
        resource["metadata"]["resourceVersion"] = existing.metadata.resource_version
        result = api.replace_namespaced_secret(name, namespace, resource)
        logger.debug(f"Updated Secret/{name}")
    except ApiException as e:
        if e.status == 404:
            result = api.create_namespaced_secret(namespace, resource)
            logger.debug(f"Created Secret/{name}")
        else:
            raise

    return result.to_dict()


async def _apply_service(resource: dict[str, Any], namespace: str) -> dict[str, Any]:
    """Apply a Service resource."""
    api = client.CoreV1Api()
    name = resource["metadata"]["name"]

    try:
        existing = api.read_namespaced_service(name, namespace)
        # Preserve clusterIP for updates
        resource["spec"]["clusterIP"] = existing.spec.cluster_ip
        resource["metadata"]["resourceVersion"] = existing.metadata.resource_version
        result = api.replace_namespaced_service(name, namespace, resource)
        logger.debug(f"Updated Service/{name}")
    except ApiException as e:
        if e.status == 404:
            result = api.create_namespaced_service(namespace, resource)
            logger.debug(f"Created Service/{name}")
        else:
            raise

    return result.to_dict()


async def _apply_deployment(resource: dict[str, Any], namespace: str) -> dict[str, Any]:
    """Apply a Deployment resource."""
    api = client.AppsV1Api()
    name = resource["metadata"]["name"]

    try:
        existing = api.read_namespaced_deployment(name, namespace)
        resource["metadata"]["resourceVersion"] = existing.metadata.resource_version
        result = api.replace_namespaced_deployment(name, namespace, resource)
        logger.debug(f"Updated Deployment/{name}")
    except ApiException as e:
        if e.status == 404:
            result = api.create_namespaced_deployment(namespace, resource)
            logger.debug(f"Created Deployment/{name}")
        else:
            raise

    return result.to_dict()


async def _apply_pvc(resource: dict[str, Any], namespace: str) -> dict[str, Any]:
    """Apply a PersistentVolumeClaim resource.

    Note: PVCs are immutable after creation, so we only create, never update.
    """
    api = client.CoreV1Api()
    name = resource["metadata"]["name"]

    try:
        existing = api.read_namespaced_persistent_volume_claim(name, namespace)
        logger.debug(f"PVC/{name} already exists, skipping")
        return existing.to_dict()
    except ApiException as e:
        if e.status == 404:
            result = api.create_namespaced_persistent_volume_claim(namespace, resource)
            logger.debug(f"Created PVC/{name}")
            return result.to_dict()
        raise


def check_deployment_ready(name: str, namespace: str) -> bool:
    """Check if a Deployment is ready.

    Args:
        name: Deployment name
        namespace: Namespace

    Returns:
        True if deployment is ready
    """
    api = client.AppsV1Api()

    try:
        dep = api.read_namespaced_deployment(name, namespace)
        ready_replicas = dep.status.ready_replicas or 0
        desired_replicas = dep.spec.replicas or 1
        return ready_replicas >= desired_replicas
    except ApiException:
        return False
