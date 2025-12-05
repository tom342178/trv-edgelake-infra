"""Validation utilities for EdgeLakeOperator spec."""

import re
from typing import Optional

from ..models.spec import EdgeLakeOperatorSpec


def validate_spec(spec: EdgeLakeOperatorSpec) -> list[str]:
    """Validate EdgeLakeOperator spec for semantic correctness.

    Args:
        spec: Parsed spec to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Required fields
    if not spec.general.nodeName:
        errors.append("spec.general.nodeName is required")
    if not spec.general.companyName:
        errors.append("spec.general.companyName is required")
    if not spec.blockchain.ledgerConn:
        errors.append("spec.blockchain.ledgerConn is required")
    if not spec.operator.clusterName:
        errors.append("spec.operator.clusterName is required")
    if not spec.operator.defaultDbms:
        errors.append("spec.operator.defaultDbms is required")

    # Port validation
    if not (1 <= spec.networking.serverPort <= 65535):
        errors.append(f"spec.networking.serverPort must be 1-65535, got {spec.networking.serverPort}")
    if not (1 <= spec.networking.restPort <= 65535):
        errors.append(f"spec.networking.restPort must be 1-65535, got {spec.networking.restPort}")
    if spec.networking.brokerPort and not (1 <= spec.networking.brokerPort <= 65535):
        errors.append(f"spec.networking.brokerPort must be 1-65535, got {spec.networking.brokerPort}")

    # Port uniqueness
    ports = [spec.networking.serverPort, spec.networking.restPort]
    if spec.networking.brokerPort:
        ports.append(spec.networking.brokerPort)
    if len(ports) != len(set(ports)):
        errors.append("Ports must be unique (serverPort, restPort, brokerPort)")

    # Blockchain ledger connection format
    ledger_pattern = r"^[a-zA-Z0-9.-]+:[0-9]+$"
    if not re.match(ledger_pattern, spec.blockchain.ledgerConn):
        errors.append(
            f"spec.blockchain.ledgerConn must be in format 'host:port', got '{spec.blockchain.ledgerConn}'"
        )

    # Database type validation
    if spec.database.type not in ["sqlite", "psql"]:
        errors.append(f"spec.database.type must be 'sqlite' or 'psql', got '{spec.database.type}'")

    # PostgreSQL requires credentials
    if spec.database.type == "psql":
        if not spec.database.user:
            errors.append("spec.database.user is required when using PostgreSQL")
        if not spec.database.password and not spec.database.passwordSecretRef:
            errors.append(
                "spec.database.password or passwordSecretRef is required when using PostgreSQL"
            )

    # MQTT validation
    if spec.mqtt.enabled:
        if not spec.mqtt.broker:
            errors.append("spec.mqtt.broker is required when MQTT is enabled")

    # OPC-UA validation
    if spec.opcua.enabled:
        if not spec.opcua.url:
            errors.append("spec.opcua.url is required when OPC-UA is enabled")

    # EtherNet/IP validation
    if spec.etherip.enabled:
        if not spec.etherip.url and not spec.etherip.simulatorMode:
            errors.append(
                "spec.etherip.url is required when EtherNet/IP is enabled (unless simulatorMode is true)"
            )

    # Service type validation
    valid_service_types = ["ClusterIP", "NodePort", "LoadBalancer"]
    if spec.networking.serviceType not in valid_service_types:
        errors.append(
            f"spec.networking.serviceType must be one of {valid_service_types}, "
            f"got '{spec.networking.serviceType}'"
        )

    # NodePort range validation
    if spec.networking.serviceType == "NodePort":
        for port_name, port in [
            ("serverPort", spec.networking.serverPort),
            ("restPort", spec.networking.restPort),
        ]:
            if port < 30000 or port > 32767:
                errors.append(
                    f"spec.networking.{port_name} should be in NodePort range 30000-32767, "
                    f"got {port}"
                )

    # Partition validation
    if spec.operator.partitioning.enabled:
        if spec.operator.partitioning.keep < 1:
            errors.append("spec.operator.partitioning.keep must be at least 1")

    return errors


def validate_ledger_connection(ledger_conn: str) -> Optional[str]:
    """Validate and parse ledger connection string.

    Args:
        ledger_conn: Connection string in format 'host:port'

    Returns:
        Error message if invalid, None if valid
    """
    pattern = r"^([a-zA-Z0-9.-]+):([0-9]+)$"
    match = re.match(pattern, ledger_conn)

    if not match:
        return f"Invalid ledger connection format: {ledger_conn}"

    port = int(match.group(2))
    if not (1 <= port <= 65535):
        return f"Invalid port in ledger connection: {port}"

    return None
