"""ConfigMap builder for EdgeLake Operator configuration."""

from typing import Any

from ..constants import ANYLOG_PATH, LOCAL_SCRIPTS_PATH, TEST_DIR_PATH
from ..models.spec import EdgeLakeOperatorSpec


def build_configmap(
    name: str,
    namespace: str,
    spec: EdgeLakeOperatorSpec,
    resource_names: dict[str, str],
) -> dict[str, Any]:
    """Build ConfigMap resource from EdgeLakeOperator spec.

    Args:
        name: Name of the EdgeLakeOperator CR
        namespace: Namespace of the CR
        spec: Parsed spec from the CR
        resource_names: Generated resource names

    Returns:
        ConfigMap manifest as dictionary
    """
    data = {
        # Kubernetes indicator
        "IS_KUBERNETES": "true",
        "INIT_TYPE": "prod",
        # Directories (fixed paths in container)
        "ANYLOG_PATH": ANYLOG_PATH,
        "LOCAL_SCRIPTS": LOCAL_SCRIPTS_PATH,
        "TEST_DIR": TEST_DIR_PATH,
        # General
        "NODE_TYPE": "operator",
        "NODE_NAME": spec.general.nodeName,
        "COMPANY_NAME": spec.general.companyName,
        "DISABLE_CLI": str(spec.general.disableCli).lower(),
        "REMOTE_CLI": str(spec.general.remoteCli).lower(),
        # Networking
        "ANYLOG_SERVER_PORT": str(spec.networking.serverPort),
        "ANYLOG_REST_PORT": str(spec.networking.restPort),
        "TCP_BIND": str(spec.networking.tcpBind).lower(),
        "REST_BIND": str(spec.networking.restBind).lower(),
        "BROKER_BIND": str(spec.networking.brokerBind).lower(),
        "TCP_THREADS": str(spec.networking.tcpThreads),
        "REST_TIMEOUT": str(spec.networking.restTimeout),
        "REST_THREADS": str(spec.networking.restThreads),
        "BROKER_THREADS": str(spec.networking.brokerThreads),
        # Database
        "DB_TYPE": spec.database.type,
        "DB_IP": spec.database.host,
        "DB_PORT": str(spec.database.port),
        "AUTOCOMMIT": str(spec.database.autocommit).lower(),
        "SYSTEM_QUERY": str(spec.database.systemQuery).lower(),
        "MEMORY": str(spec.database.memory).lower(),
        # NoSQL
        "ENABLE_NOSQL": str(spec.database.nosql.enabled).lower(),
        "NOSQL_TYPE": spec.database.nosql.type,
        "NOSQL_IP": spec.database.nosql.host,
        "NOSQL_PORT": str(spec.database.nosql.port),
        "BLOBS_DBMS": str(spec.database.nosql.blobsDbms).lower(),
        "BLOBS_REUSE": str(spec.database.nosql.blobsReuse).lower(),
        # Blockchain
        "LEDGER_CONN": spec.blockchain.ledgerConn,
        "SYNC_TIME": spec.blockchain.syncTime,
        "BLOCKCHAIN_SYNC": spec.blockchain.syncTime,
        "BLOCKCHAIN_SOURCE": spec.blockchain.source,
        "BLOCKCHAIN_DESTINATION": spec.blockchain.destination,
        # Operator
        "CLUSTER_NAME": spec.operator.clusterName,
        "DEFAULT_DBMS": spec.operator.defaultDbms,
        "ENABLE_HA": str(spec.operator.enableHa).lower(),
        "START_DATE": str(spec.operator.startDate),
        "OPERATOR_THREADS": str(spec.operator.threads),
        # Partitioning
        "ENABLE_PARTITIONS": str(spec.operator.partitioning.enabled).lower(),
        "TABLE_NAME": spec.operator.partitioning.tableName,
        "PARTITION_COLUMN": spec.operator.partitioning.column,
        "PARTITION_INTERVAL": spec.operator.partitioning.interval,
        "PARTITION_KEEP": str(spec.operator.partitioning.keep),
        "PARTITION_SYNC": spec.operator.partitioning.sync,
        # MQTT
        "ENABLE_MQTT": str(spec.mqtt.enabled).lower(),
        "MQTT_PORT": str(spec.mqtt.port),
        "MQTT_LOG": str(spec.mqtt.log).lower(),
        # OPC-UA
        "ENABLE_OPCUA": str(spec.opcua.enabled).lower(),
        # EtherNet/IP
        "ENABLE_ETHERIP": str(spec.etherip.enabled).lower(),
        "SIMULATOR_MODE": str(spec.etherip.simulatorMode).lower(),
        # Aggregations
        "ENABLE_AGGREGATIONS": str(spec.aggregations.enabled).lower(),
        "AGGREGATION_TIME_COLUMN": spec.aggregations.timeColumn,
        "AGGREGATION_VALUE_COLUMN": spec.aggregations.valueColumn,
        # Monitoring
        "MONITOR_NODES": str(spec.monitoring.enabled).lower(),
        "STORE_MONITORING": str(spec.monitoring.storeMonitoring).lower(),
        "SYSLOG_MONITORING": str(spec.monitoring.syslogMonitoring).lower(),
        # MCP
        "MCP_AUTOSTART": str(spec.mcp.autostart).lower(),
        # Advanced
        "DEPLOY_LOCAL_SCRIPT": str(spec.advanced.deployLocalScript).lower(),
        "DEBUG_MODE": str(spec.advanced.debugMode).lower(),
        "COMPRESS_FILE": str(spec.advanced.compressFile).lower(),
        "QUERY_POOL": str(spec.advanced.queryPool),
        "WRITE_IMMEDIATE": str(spec.advanced.writeImmediate).lower(),
        "THRESHOLD_TIME": spec.advanced.thresholdTime,
        "THRESHOLD_VOLUME": spec.advanced.thresholdVolume,
        # Nebula
        "ENABLE_NEBULA": str(spec.nebula.enabled).lower(),
        "NEBULA_NEW_KEYS": str(spec.nebula.newKeys).lower(),
        "IS_LIGHTHOUSE": str(spec.nebula.isLighthouse).lower(),
    }

    # Optional fields - only add if set
    if spec.general.licenseKey and not spec.general.licenseKeySecretRef:
        # If using inline license and no secret ref, it will be in the secret
        pass  # Handled via env var from secret

    if spec.networking.overlayIp:
        data["OVERLAY_IP"] = spec.networking.overlayIp

    if spec.networking.brokerPort:
        data["ANYLOG_BROKER_PORT"] = str(spec.networking.brokerPort)

    if spec.networking.configName:
        data["CONFIG_NAME"] = spec.networking.configName

    if spec.networking.nicType:
        data["NIC_TYPE"] = spec.networking.nicType

    # Geolocation
    if spec.geolocation.location:
        data["LOCATION"] = spec.geolocation.location
    if spec.geolocation.country:
        data["COUNTRY"] = spec.geolocation.country
    if spec.geolocation.state:
        data["STATE"] = spec.geolocation.state
    if spec.geolocation.city:
        data["CITY"] = spec.geolocation.city

    # Database user (password handled via secret)
    if spec.database.user:
        data["DB_USER"] = spec.database.user

    # NoSQL user (password handled via secret)
    if spec.database.nosql.user:
        data["NOSQL_USER"] = spec.database.nosql.user

    # MQTT
    if spec.mqtt.broker:
        data["MQTT_BROKER"] = spec.mqtt.broker
    if spec.mqtt.user:
        data["MQTT_USER"] = spec.mqtt.user
    if spec.mqtt.message.topic:
        data["MSG_TOPIC"] = spec.mqtt.message.topic
        data["MSG_DBMS"] = spec.mqtt.message.dbms or spec.operator.defaultDbms
        data["MSG_TABLE"] = spec.mqtt.message.table
        data["MSG_TIMESTAMP_COLUMN"] = spec.mqtt.message.timestampColumn
        data["MSG_VALUE_COLUMN"] = spec.mqtt.message.valueColumn
        data["MSG_VALUE_COLUMN_TYPE"] = spec.mqtt.message.valueColumnType

    # OPC-UA
    if spec.opcua.url:
        data["OPCUA_URL"] = spec.opcua.url
    if spec.opcua.node:
        data["OPCUA_NODE"] = spec.opcua.node
    if spec.opcua.frequency:
        data["OPCUA_FREQUENCY"] = spec.opcua.frequency

    # EtherNet/IP
    if spec.etherip.url:
        data["ETHERIP_URL"] = spec.etherip.url
    if spec.etherip.frequency:
        data["ETHERIP_FREQUENCY"] = spec.etherip.frequency

    # Operator member
    if spec.operator.member:
        data["MEMBER"] = spec.operator.member

    # Nebula
    if spec.nebula.cidrOverlayAddress:
        data["CIDR_OVERLAY_ADDRESS"] = spec.nebula.cidrOverlayAddress
    if spec.nebula.lighthouseIp:
        data["LIGHTHOUSE_IP"] = spec.nebula.lighthouseIp
    if spec.nebula.lighthouseNodeIp:
        data["LIGHTHOUSE_NODE_IP"] = spec.nebula.lighthouseNodeIp

    # Service discovery - K8s DNS name
    service_name = resource_names["service"]
    data["PROXY_IP"] = f"{service_name}.{namespace}.svc.cluster.local"

    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": resource_names["configmap"],
            "namespace": namespace,
            "labels": _build_labels(name),
        },
        "data": data,
    }


def _build_labels(name: str) -> dict[str, str]:
    """Build standard labels for resources."""
    return {
        "app.kubernetes.io/name": "edgelake-operator",
        "app.kubernetes.io/instance": name,
        "app.kubernetes.io/component": "operator",
        "app.kubernetes.io/managed-by": "edgelake-kube-operator",
    }
