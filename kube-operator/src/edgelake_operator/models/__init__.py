"""Models for EdgeLake Operator CRD spec and status."""

from .spec import EdgeLakeOperatorSpec
from .status import OperatorPhase, OperatorStatus

__all__ = ["EdgeLakeOperatorSpec", "OperatorPhase", "OperatorStatus"]
