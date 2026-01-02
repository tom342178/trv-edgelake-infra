"""Pydantic models for EdgeLakeOperator CRD spec."""

from typing import Optional

from pydantic import BaseModel, Field

from ..constants import (
    DEFAULT_ACCESS_MODE,
    DEFAULT_BLOCKCHAIN_DESTINATION,
    DEFAULT_BLOCKCHAIN_SOURCE,
    DEFAULT_BROKER_THREADS,
    DEFAULT_CPU_LIMIT,
    DEFAULT_CPU_REQUEST,
    DEFAULT_DB_HOST,
    DEFAULT_DB_PORT,
    DEFAULT_DB_TYPE,
    DEFAULT_IMAGE_PULL_POLICY,
    DEFAULT_IMAGE_REPOSITORY,
    DEFAULT_IMAGE_TAG,
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_MEMORY_REQUEST,
    DEFAULT_NOSQL_HOST,
    DEFAULT_NOSQL_PORT,
    DEFAULT_NOSQL_TYPE,
    DEFAULT_OPERATOR_THREADS,
    DEFAULT_PARTITION_COLUMN,
    DEFAULT_PARTITION_ENABLED,
    DEFAULT_PARTITION_INTERVAL,
    DEFAULT_PARTITION_KEEP,
    DEFAULT_PARTITION_SYNC,
    DEFAULT_PARTITION_TABLE,
    DEFAULT_PVC_ANYLOG_SIZE,
    DEFAULT_PVC_BLOCKCHAIN_SIZE,
    DEFAULT_PVC_DATA_SIZE,
    DEFAULT_PVC_SCRIPTS_SIZE,
    DEFAULT_QUERY_POOL,
    DEFAULT_REST_PORT,
    DEFAULT_REST_THREADS,
    DEFAULT_REST_TIMEOUT,
    DEFAULT_SERVER_PORT,
    DEFAULT_SERVICE_TYPE,
    DEFAULT_START_DATE,
    DEFAULT_SYNC_TIME,
    DEFAULT_TCP_THREADS,
    DEFAULT_THRESHOLD_TIME,
    DEFAULT_THRESHOLD_VOLUME,
)


class SecretRef(BaseModel):
    """Reference to a Kubernetes secret."""

    name: str
    key: str


class ImageSpec(BaseModel):
    """Docker image configuration."""

    repository: str = DEFAULT_IMAGE_REPOSITORY
    tag: str = DEFAULT_IMAGE_TAG
    pullPolicy: str = Field(default=DEFAULT_IMAGE_PULL_POLICY, alias="pull_policy")
    pullSecretName: Optional[str] = Field(default=None, alias="pull_secret_name")

    class Config:
        populate_by_name = True


class ResourceRequirements(BaseModel):
    """CPU and memory requirements."""

    cpu: str = DEFAULT_CPU_REQUEST
    memory: str = DEFAULT_MEMORY_REQUEST


class ResourceLimits(BaseModel):
    """CPU and memory limits."""

    cpu: str = DEFAULT_CPU_LIMIT
    memory: str = DEFAULT_MEMORY_LIMIT


class ResourcesSpec(BaseModel):
    """Resource limits and requests."""

    limits: ResourceLimits = Field(default_factory=ResourceLimits)
    requests: ResourceRequirements = Field(default_factory=ResourceRequirements)


class VolumeSize(BaseModel):
    """Volume size configuration."""

    size: str = "1Gi"


class PersistenceSpec(BaseModel):
    """Persistent volume configuration."""

    enabled: bool = True
    storageClassName: Optional[str] = Field(default=None, alias="storage_class_name")
    accessMode: str = Field(default=DEFAULT_ACCESS_MODE, alias="access_mode")
    retainOnDelete: bool = Field(default=True, alias="retain_on_delete")
    anylog: VolumeSize = Field(default_factory=lambda: VolumeSize(size=DEFAULT_PVC_ANYLOG_SIZE))
    blockchain: VolumeSize = Field(
        default_factory=lambda: VolumeSize(size=DEFAULT_PVC_BLOCKCHAIN_SIZE)
    )
    data: VolumeSize = Field(default_factory=lambda: VolumeSize(size=DEFAULT_PVC_DATA_SIZE))
    scripts: VolumeSize = Field(default_factory=lambda: VolumeSize(size=DEFAULT_PVC_SCRIPTS_SIZE))

    class Config:
        populate_by_name = True


class GeneralSpec(BaseModel):
    """General node identity and settings."""

    nodeName: str = Field(..., alias="node_name", min_length=1)
    companyName: str = Field(..., alias="company_name", min_length=1)
    licenseKey: Optional[str] = Field(default=None, alias="license_key")
    licenseKeySecretRef: Optional[SecretRef] = Field(default=None, alias="license_key_secret_ref")
    disableCli: bool = Field(default=False, alias="disable_cli")
    remoteCli: bool = Field(default=False, alias="remote_cli")

    class Config:
        populate_by_name = True


class GeolocationSpec(BaseModel):
    """Geographic location metadata."""

    location: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class NetworkingSpec(BaseModel):
    """Network and port configuration."""

    serviceType: str = Field(default=DEFAULT_SERVICE_TYPE, alias="service_type")
    overlayIp: Optional[str] = Field(default=None, alias="overlay_ip")
    serverPort: int = Field(default=DEFAULT_SERVER_PORT, alias="server_port", ge=1, le=65535)
    restPort: int = Field(default=DEFAULT_REST_PORT, alias="rest_port", ge=1, le=65535)
    brokerPort: Optional[int] = Field(default=None, alias="broker_port", ge=1, le=65535)
    tcpBind: bool = Field(default=False, alias="tcp_bind")
    restBind: bool = Field(default=False, alias="rest_bind")
    brokerBind: bool = Field(default=False, alias="broker_bind")
    configName: Optional[str] = Field(default=None, alias="config_name")
    nicType: Optional[str] = Field(default=None, alias="nic_type")
    tcpThreads: int = Field(default=DEFAULT_TCP_THREADS, alias="tcp_threads")
    restTimeout: int = Field(default=DEFAULT_REST_TIMEOUT, alias="rest_timeout")
    restThreads: int = Field(default=DEFAULT_REST_THREADS, alias="rest_threads")
    brokerThreads: int = Field(default=DEFAULT_BROKER_THREADS, alias="broker_threads")

    class Config:
        populate_by_name = True


class NoSqlSpec(BaseModel):
    """NoSQL (MongoDB) configuration."""

    enabled: bool = False
    type: str = DEFAULT_NOSQL_TYPE
    user: Optional[str] = None
    password: Optional[str] = None
    passwordSecretRef: Optional[SecretRef] = Field(default=None, alias="password_secret_ref")
    host: str = DEFAULT_NOSQL_HOST
    port: int = DEFAULT_NOSQL_PORT
    blobsDbms: bool = Field(default=False, alias="blobs_dbms")
    blobsReuse: bool = Field(default=True, alias="blobs_reuse")

    class Config:
        populate_by_name = True


class DatabaseSpec(BaseModel):
    """Database configuration."""

    type: str = DEFAULT_DB_TYPE
    user: Optional[str] = None
    password: Optional[str] = None
    passwordSecretRef: Optional[SecretRef] = Field(default=None, alias="password_secret_ref")
    host: str = DEFAULT_DB_HOST
    port: int = DEFAULT_DB_PORT
    autocommit: bool = False
    systemQuery: bool = Field(default=False, alias="system_query")
    memory: bool = False
    nosql: NoSqlSpec = Field(default_factory=NoSqlSpec)

    class Config:
        populate_by_name = True


class BlockchainSpec(BaseModel):
    """Blockchain/Master node configuration."""

    ledgerConn: str = Field(..., alias="ledger_conn", pattern=r"^[a-zA-Z0-9.-]+:[0-9]+$")
    syncTime: str = Field(default=DEFAULT_SYNC_TIME, alias="sync_time")
    source: str = DEFAULT_BLOCKCHAIN_SOURCE
    destination: str = DEFAULT_BLOCKCHAIN_DESTINATION

    class Config:
        populate_by_name = True


class PartitioningSpec(BaseModel):
    """Data partitioning configuration."""

    enabled: bool = DEFAULT_PARTITION_ENABLED
    tableName: str = Field(default=DEFAULT_PARTITION_TABLE, alias="table_name")
    column: str = DEFAULT_PARTITION_COLUMN
    interval: str = DEFAULT_PARTITION_INTERVAL
    keep: int = DEFAULT_PARTITION_KEEP
    sync: str = DEFAULT_PARTITION_SYNC

    class Config:
        populate_by_name = True


class OperatorSpec(BaseModel):
    """Operator node specific settings."""

    clusterName: str = Field(..., alias="cluster_name", min_length=1)
    defaultDbms: str = Field(..., alias="default_dbms", min_length=1)
    member: Optional[str] = None
    enableHa: bool = Field(default=False, alias="enable_ha")
    startDate: int = Field(default=DEFAULT_START_DATE, alias="start_date")
    threads: int = DEFAULT_OPERATOR_THREADS
    partitioning: PartitioningSpec = Field(default_factory=PartitioningSpec)

    class Config:
        populate_by_name = True


class MqttMessageSpec(BaseModel):
    """MQTT message processing configuration."""

    topic: Optional[str] = None
    dbms: Optional[str] = None
    table: str = "bring [table]"
    timestampColumn: str = Field(default="bring [timestamp]", alias="timestamp_column")
    valueColumn: str = Field(default="bring [value]", alias="value_column")
    valueColumnType: str = Field(default="float", alias="value_column_type")

    class Config:
        populate_by_name = True


class MqttSpec(BaseModel):
    """MQTT data ingestion configuration."""

    enabled: bool = False
    broker: Optional[str] = None
    port: int = 1883
    user: Optional[str] = None
    password: Optional[str] = None
    passwordSecretRef: Optional[SecretRef] = Field(default=None, alias="password_secret_ref")
    log: bool = False
    message: MqttMessageSpec = Field(default_factory=MqttMessageSpec)

    class Config:
        populate_by_name = True


class OpcuaSpec(BaseModel):
    """OPC-UA client configuration."""

    enabled: bool = False
    url: Optional[str] = None
    node: Optional[str] = None
    frequency: Optional[str] = None


class EtheripSpec(BaseModel):
    """EtherNet/IP (Allen-Bradley PLC) configuration."""

    enabled: bool = False
    simulatorMode: bool = Field(default=False, alias="simulator_mode")
    url: Optional[str] = None
    frequency: Optional[str] = None

    class Config:
        populate_by_name = True


class AggregationsSpec(BaseModel):
    """Data aggregation configuration."""

    enabled: bool = False
    timeColumn: str = Field(default="insert_timestamp", alias="time_column")
    valueColumn: str = Field(default="value", alias="value_column")

    class Config:
        populate_by_name = True


class MonitoringSpec(BaseModel):
    """Node monitoring configuration."""

    enabled: bool = False
    storeMonitoring: bool = Field(default=False, alias="store_monitoring")
    syslogMonitoring: bool = Field(default=False, alias="syslog_monitoring")

    class Config:
        populate_by_name = True


class McpSpec(BaseModel):
    """Model Context Protocol configuration."""

    autostart: bool = False


class AdvancedSpec(BaseModel):
    """Advanced configuration options."""

    deployLocalScript: bool = Field(default=False, alias="deploy_local_script")
    debugMode: bool = Field(default=False, alias="debug_mode")
    compressFile: bool = Field(default=True, alias="compress_file")
    queryPool: int = Field(default=DEFAULT_QUERY_POOL, alias="query_pool")
    writeImmediate: bool = Field(default=False, alias="write_immediate")
    thresholdTime: str = Field(default=DEFAULT_THRESHOLD_TIME, alias="threshold_time")
    thresholdVolume: str = Field(default=DEFAULT_THRESHOLD_VOLUME, alias="threshold_volume")

    class Config:
        populate_by_name = True


class NebulaSpec(BaseModel):
    """Nebula VPN configuration."""

    enabled: bool = False
    newKeys: bool = Field(default=False, alias="new_keys")
    isLighthouse: bool = Field(default=False, alias="is_lighthouse")
    cidrOverlayAddress: Optional[str] = Field(default=None, alias="cidr_overlay_address")
    lighthouseIp: Optional[str] = Field(default=None, alias="lighthouse_ip")
    lighthouseNodeIp: Optional[str] = Field(default=None, alias="lighthouse_node_ip")

    class Config:
        populate_by_name = True


class EdgeLakeOperatorSpec(BaseModel):
    """Complete EdgeLakeOperator CRD spec."""

    image: ImageSpec = Field(default_factory=ImageSpec)
    resources: ResourcesSpec = Field(default_factory=ResourcesSpec)
    persistence: PersistenceSpec = Field(default_factory=PersistenceSpec)
    general: GeneralSpec
    geolocation: GeolocationSpec = Field(default_factory=GeolocationSpec)
    networking: NetworkingSpec = Field(default_factory=NetworkingSpec)
    database: DatabaseSpec = Field(default_factory=DatabaseSpec)
    blockchain: BlockchainSpec
    operator: OperatorSpec
    mqtt: MqttSpec = Field(default_factory=MqttSpec)
    opcua: OpcuaSpec = Field(default_factory=OpcuaSpec)
    etherip: EtheripSpec = Field(default_factory=EtheripSpec)
    aggregations: AggregationsSpec = Field(default_factory=AggregationsSpec)
    monitoring: MonitoringSpec = Field(default_factory=MonitoringSpec)
    mcp: McpSpec = Field(default_factory=McpSpec)
    advanced: AdvancedSpec = Field(default_factory=AdvancedSpec)
    nebula: NebulaSpec = Field(default_factory=NebulaSpec)

    class Config:
        populate_by_name = True

    @classmethod
    def from_dict(cls, data: dict) -> "EdgeLakeOperatorSpec":
        """Create spec from dictionary (handles both camelCase and snake_case)."""
        return cls.model_validate(data)

    def has_inline_secrets(self) -> bool:
        """Check if any inline secrets are defined that need to be stored in a Secret."""
        return any(
            [
                self.database.password and not self.database.passwordSecretRef,
                self.database.nosql.password and not self.database.nosql.passwordSecretRef,
                self.mqtt.password and not self.mqtt.passwordSecretRef,
                self.general.licenseKey and not self.general.licenseKeySecretRef,
            ]
        )
