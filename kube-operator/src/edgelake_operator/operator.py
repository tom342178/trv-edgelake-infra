"""EdgeLake Operator - kopf handlers for EdgeLakeOperator CRD.

This module contains the main operator logic for managing EdgeLake operator nodes
via Kubernetes Custom Resources.
"""

import logging
from typing import Any

import kopf
import kubernetes

from .constants import API_GROUP, API_VERSION, PLURAL
from .models.spec import EdgeLakeOperatorSpec
from .models.status import ConditionStatus, ConditionType, OperatorPhase
from .resources import configmap, deployment, pvc, secret, service
from .utils.hashing import compute_config_hash
from .utils.kubernetes import apply_resource, check_deployment_ready, delete_resource
from .utils.validation import validate_spec

logger = logging.getLogger(__name__)


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_: Any) -> None:
    """Configure operator settings on startup."""
    settings.posting.level = logging.INFO
    settings.watching.connect_timeout = 60
    settings.watching.server_timeout = 300
    settings.persistence.finalizer = "edgelake.io/cleanup"
    logger.info("EdgeLake Operator started")


@kopf.on.create(API_GROUP, API_VERSION, PLURAL)
async def create_edgelake_operator(
    body: dict[str, Any],
    spec: dict[str, Any],
    name: str,
    namespace: str,
    logger: logging.Logger,
    patch: kopf.Patch,
    **_: Any,
) -> dict[str, Any]:
    """Handle creation of EdgeLakeOperator resource.

    Creates all required Kubernetes resources:
    - Secret (if inline secrets defined)
    - ConfigMap (environment variables)
    - PersistentVolumeClaims (if persistence enabled)
    - Service
    - Deployment
    """
    logger.info(f"Creating EdgeLakeOperator: {namespace}/{name}")

    # Update status to Creating
    patch.status["phase"] = OperatorPhase.CREATING.value

    try:
        # Parse and validate spec
        operator_spec = EdgeLakeOperatorSpec.from_dict(spec)
        validation_errors = validate_spec(operator_spec)
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Validation failed: {error_msg}")
            raise kopf.PermanentError(f"Validation failed: {error_msg}")

        # Generate resource names
        resource_names = _generate_resource_names(name)

        created_resources: dict[str, Any] = {}

        # 1. Create Secret (if using inline secrets)
        if operator_spec.has_inline_secrets():
            secret_resource = secret.build_secret(name, namespace, operator_spec, resource_names)
            if secret_resource:
                kopf.adopt(secret_resource, owner=body)
                await apply_resource(secret_resource, namespace)
                created_resources["secret"] = resource_names["secret"]
                logger.info(f"Created Secret: {resource_names['secret']}")

        # 2. Create ConfigMap
        configmap_resource = configmap.build_configmap(
            name, namespace, operator_spec, resource_names
        )
        kopf.adopt(configmap_resource, owner=body)
        await apply_resource(configmap_resource, namespace)
        created_resources["configmap"] = resource_names["configmap"]
        logger.info(f"Created ConfigMap: {resource_names['configmap']}")

        # 3. Create PVCs (if persistence enabled)
        if operator_spec.persistence.enabled:
            pvc_resources = pvc.build_pvcs(name, namespace, operator_spec, resource_names)
            pvc_names = []
            for pvc_resource in pvc_resources:
                # Don't adopt PVCs if we want to retain them on delete
                if not operator_spec.persistence.retainOnDelete:
                    kopf.adopt(pvc_resource, owner=body)
                await apply_resource(pvc_resource, namespace)
                pvc_names.append(pvc_resource["metadata"]["name"])
            created_resources["pvcs"] = pvc_names
            logger.info(f"Created PVCs: {pvc_names}")

        # 4. Create Service
        service_resource = service.build_service(name, namespace, operator_spec, resource_names)
        kopf.adopt(service_resource, owner=body)
        await apply_resource(service_resource, namespace)
        created_resources["service"] = resource_names["service"]
        logger.info(f"Created Service: {resource_names['service']}")

        # 5. Create Deployment
        config_hash = compute_config_hash(spec)
        deployment_resource = deployment.build_deployment(
            name, namespace, operator_spec, resource_names, config_hash=config_hash
        )
        kopf.adopt(deployment_resource, owner=body)
        await apply_resource(deployment_resource, namespace)
        created_resources["deployment"] = resource_names["deployment"]
        logger.info(f"Created Deployment: {resource_names['deployment']}")

        # Build status response
        return {
            "phase": OperatorPhase.RUNNING.value,
            "deploymentName": resource_names["deployment"],
            "serviceName": resource_names["service"],
            "configMapName": resource_names["configmap"],
            "secretName": created_resources.get("secret"),
            "pvcNames": created_resources.get("pvcs", []),
            "endpoints": _build_endpoints(operator_spec, namespace, resource_names),
            "observedGeneration": body["metadata"].get("generation", 1),
        }

    except kopf.PermanentError:
        raise
    except Exception as e:
        logger.error(f"Failed to create EdgeLakeOperator: {e}")
        patch.status["phase"] = OperatorPhase.FAILED.value
        raise kopf.TemporaryError(str(e), delay=30)


@kopf.on.update(API_GROUP, API_VERSION, PLURAL)
async def update_edgelake_operator(
    body: dict[str, Any],
    spec: dict[str, Any],
    old: dict[str, Any],
    new: dict[str, Any],
    diff: kopf.Diff,
    name: str,
    namespace: str,
    status: dict[str, Any],
    logger: logging.Logger,
    patch: kopf.Patch,
    **_: Any,
) -> dict[str, Any]:
    """Handle updates to EdgeLakeOperator resource.

    Updates ConfigMap and triggers rolling restart if configuration changed.
    """
    logger.info(f"Updating EdgeLakeOperator: {namespace}/{name}")

    patch.status["phase"] = OperatorPhase.UPDATING.value

    try:
        operator_spec = EdgeLakeOperatorSpec.from_dict(spec)
        validation_errors = validate_spec(operator_spec)
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            raise kopf.PermanentError(f"Validation failed: {error_msg}")

        resource_names = _generate_resource_names(name)

        # Determine what changed
        config_changed = _config_fields_changed(diff)
        secrets_changed = _secrets_changed(diff)

        # Update Secret if secrets changed
        if secrets_changed and operator_spec.has_inline_secrets():
            secret_resource = secret.build_secret(name, namespace, operator_spec, resource_names)
            if secret_resource:
                kopf.adopt(secret_resource, owner=body)
                await apply_resource(secret_resource, namespace)
                logger.info(f"Updated Secret: {resource_names['secret']}")

        # Update ConfigMap if configuration changed
        if config_changed:
            configmap_resource = configmap.build_configmap(
                name, namespace, operator_spec, resource_names
            )
            kopf.adopt(configmap_resource, owner=body)
            await apply_resource(configmap_resource, namespace)
            logger.info(f"Updated ConfigMap: {resource_names['configmap']}")

            # Trigger rolling restart by updating deployment with new config hash
            config_hash = compute_config_hash(spec)
            deployment_resource = deployment.build_deployment(
                name, namespace, operator_spec, resource_names, config_hash=config_hash
            )
            kopf.adopt(deployment_resource, owner=body)
            await apply_resource(deployment_resource, namespace)
            logger.info(f"Updated Deployment (config hash: {config_hash})")

        # Update Service if networking changed
        if _networking_changed(diff):
            service_resource = service.build_service(
                name, namespace, operator_spec, resource_names
            )
            kopf.adopt(service_resource, owner=body)
            await apply_resource(service_resource, namespace)
            logger.info(f"Updated Service: {resource_names['service']}")

        return {
            "phase": OperatorPhase.RUNNING.value,
            "observedGeneration": body["metadata"].get("generation", 1),
            "endpoints": _build_endpoints(operator_spec, namespace, resource_names),
        }

    except kopf.PermanentError:
        raise
    except Exception as e:
        logger.error(f"Failed to update EdgeLakeOperator: {e}")
        patch.status["phase"] = OperatorPhase.FAILED.value
        raise kopf.TemporaryError(str(e), delay=30)


@kopf.on.delete(API_GROUP, API_VERSION, PLURAL)
async def delete_edgelake_operator(
    body: dict[str, Any],
    name: str,
    namespace: str,
    status: dict[str, Any],
    logger: logging.Logger,
    **_: Any,
) -> None:
    """Handle deletion of EdgeLakeOperator resource.

    Resources with owner references are automatically garbage collected.
    PVCs may be retained based on retainOnDelete setting.
    """
    logger.info(f"Deleting EdgeLakeOperator: {namespace}/{name}")

    resource_names = _generate_resource_names(name)

    # Most resources are deleted automatically via owner references
    # But we may want to explicitly delete PVCs if they weren't adopted

    # Check if PVCs should be deleted
    spec = body.get("spec", {})
    persistence = spec.get("persistence", {})
    retain_on_delete = persistence.get("retainOnDelete", True)

    if not retain_on_delete:
        # Delete PVCs explicitly
        pvc_names = status.get("pvcNames", [])
        for pvc_name in pvc_names:
            try:
                await delete_resource("PersistentVolumeClaim", pvc_name, namespace)
                logger.info(f"Deleted PVC: {pvc_name}")
            except Exception as e:
                logger.warning(f"Failed to delete PVC {pvc_name}: {e}")
    else:
        logger.info("Retaining PVCs (retainOnDelete=true)")

    logger.info(f"EdgeLakeOperator {namespace}/{name} deleted successfully")


@kopf.timer(API_GROUP, API_VERSION, PLURAL, interval=60, initial_delay=30)
async def monitor_edgelake_operator(
    body: dict[str, Any],
    spec: dict[str, Any],
    name: str,
    namespace: str,
    status: dict[str, Any],
    logger: logging.Logger,
    patch: kopf.Patch,
    **_: Any,
) -> None:
    """Periodic health check of EdgeLake deployment."""
    current_phase = status.get("phase")

    if current_phase != OperatorPhase.RUNNING.value:
        return

    try:
        deployment_name = status.get("deploymentName")
        if deployment_name:
            is_ready = check_deployment_ready(deployment_name, namespace)
            if not is_ready:
                logger.warning(f"Deployment {deployment_name} not fully ready")
    except Exception as e:
        logger.error(f"Health check failed: {e}")


def _generate_resource_names(name: str) -> dict[str, str]:
    """Generate consistent resource names based on CR name."""
    return {
        "deployment": f"{name}-deployment",
        "service": f"{name}-service",
        "configmap": f"{name}-config",
        "secret": f"{name}-secrets",
        "pvc_anylog": f"{name}-anylog-pvc",
        "pvc_blockchain": f"{name}-blockchain-pvc",
        "pvc_data": f"{name}-data-pvc",
        "pvc_scripts": f"{name}-scripts-pvc",
    }


def _build_endpoints(
    spec: EdgeLakeOperatorSpec,
    namespace: str,
    resource_names: dict[str, str],
) -> dict[str, str | None]:
    """Build service endpoint URLs for status."""
    service_name = resource_names["service"]
    return {
        "tcp": f"{service_name}.{namespace}.svc.cluster.local:{spec.networking.serverPort}",
        "rest": f"{service_name}.{namespace}.svc.cluster.local:{spec.networking.restPort}",
        "broker": (
            f"{service_name}.{namespace}.svc.cluster.local:{spec.networking.brokerPort}"
            if spec.networking.brokerPort
            else None
        ),
    }


def _config_fields_changed(diff: kopf.Diff) -> bool:
    """Check if configuration fields changed that require ConfigMap update."""
    config_paths = [
        "general",
        "networking",
        "database",
        "blockchain",
        "operator",
        "mqtt",
        "opcua",
        "etherip",
        "monitoring",
        "advanced",
        "geolocation",
        "mcp",
        "nebula",
        "aggregations",
    ]
    for op, path, old, new in diff:
        path_str = ".".join(str(p) for p in path)
        if any(p in path_str for p in config_paths):
            return True
    return False


def _secrets_changed(diff: kopf.Diff) -> bool:
    """Check if secret-related fields changed."""
    secret_paths = ["password", "licenseKey"]
    for op, path, old, new in diff:
        path_str = ".".join(str(p) for p in path)
        if any(p in path_str for p in secret_paths):
            return True
    return False


def _networking_changed(diff: kopf.Diff) -> bool:
    """Check if networking configuration changed."""
    for op, path, old, new in diff:
        path_str = ".".join(str(p) for p in path)
        if "networking" in path_str:
            return True
    return False
