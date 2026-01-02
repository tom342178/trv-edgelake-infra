"""Hashing utilities for configuration change detection."""

import hashlib
import json
from typing import Any


def compute_config_hash(spec: dict[str, Any]) -> str:
    """Compute a hash of the spec for change detection.

    This is used to trigger rolling updates when configuration changes.
    The hash is stored as an annotation on the Deployment.

    Args:
        spec: The EdgeLakeOperator spec dictionary

    Returns:
        SHA256 hash of the spec (first 16 characters)
    """
    # Create a normalized JSON string (sorted keys for consistency)
    spec_json = json.dumps(spec, sort_keys=True, default=str)

    # Compute SHA256 hash
    hash_obj = hashlib.sha256(spec_json.encode())

    # Return first 16 characters for brevity
    return hash_obj.hexdigest()[:16]
