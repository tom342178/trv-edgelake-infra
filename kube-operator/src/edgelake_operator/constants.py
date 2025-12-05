"""Constants and default values for the EdgeLake Operator."""

# CRD identifiers
API_GROUP = "edgelake.io"
API_VERSION = "v1alpha1"
PLURAL = "edgelakeoperators"
SINGULAR = "edgelakeoperator"
KIND = "EdgeLakeOperator"

# Labels
LABEL_APP_NAME = "app.kubernetes.io/name"
LABEL_INSTANCE = "app.kubernetes.io/instance"
LABEL_COMPONENT = "app.kubernetes.io/component"
LABEL_MANAGED_BY = "app.kubernetes.io/managed-by"

# Annotations
ANNOTATION_CONFIG_HASH = "edgelake.io/config-hash"

# Default values
DEFAULT_IMAGE_REPOSITORY = "anylogco/edgelake-network"
DEFAULT_IMAGE_TAG = "1.3.2500"
DEFAULT_IMAGE_PULL_POLICY = "IfNotPresent"

DEFAULT_CPU_LIMIT = "2000m"
DEFAULT_MEMORY_LIMIT = "4Gi"
DEFAULT_CPU_REQUEST = "500m"
DEFAULT_MEMORY_REQUEST = "1Gi"

DEFAULT_SERVER_PORT = 32148
DEFAULT_REST_PORT = 32149
DEFAULT_SERVICE_TYPE = "NodePort"

DEFAULT_DB_TYPE = "sqlite"
DEFAULT_DB_HOST = "127.0.0.1"
DEFAULT_DB_PORT = 5432

DEFAULT_NOSQL_TYPE = "mongo"
DEFAULT_NOSQL_HOST = "127.0.0.1"
DEFAULT_NOSQL_PORT = 27017

DEFAULT_BLOCKCHAIN_SOURCE = "master"
DEFAULT_BLOCKCHAIN_DESTINATION = "file"
DEFAULT_SYNC_TIME = "30 second"

DEFAULT_PARTITION_ENABLED = True
DEFAULT_PARTITION_TABLE = "*"
DEFAULT_PARTITION_COLUMN = "insert_timestamp"
DEFAULT_PARTITION_INTERVAL = "14 days"
DEFAULT_PARTITION_KEEP = 3
DEFAULT_PARTITION_SYNC = "1 day"

DEFAULT_OPERATOR_THREADS = 3
DEFAULT_START_DATE = 30

DEFAULT_TCP_THREADS = 6
DEFAULT_REST_THREADS = 6
DEFAULT_REST_TIMEOUT = 30
DEFAULT_BROKER_THREADS = 6

DEFAULT_QUERY_POOL = 6
DEFAULT_THRESHOLD_TIME = "60 seconds"
DEFAULT_THRESHOLD_VOLUME = "100KB"

# Container paths
ANYLOG_PATH = "/app"
LOCAL_SCRIPTS_PATH = "/app/deployment-scripts/node-deployment"
TEST_DIR_PATH = "/app/deployment-scripts/tests"

# Volume mount paths
VOLUME_MOUNT_ANYLOG = "/app/EdgeLake/anylog"
VOLUME_MOUNT_BLOCKCHAIN = "/app/EdgeLake/blockchain"
VOLUME_MOUNT_DATA = "/app/EdgeLake/data"
VOLUME_MOUNT_SCRIPTS = "/app/deployment-scripts"

# Default PVC sizes
DEFAULT_PVC_ANYLOG_SIZE = "5Gi"
DEFAULT_PVC_BLOCKCHAIN_SIZE = "1Gi"
DEFAULT_PVC_DATA_SIZE = "10Gi"
DEFAULT_PVC_SCRIPTS_SIZE = "1Gi"
DEFAULT_ACCESS_MODE = "ReadWriteOnce"
