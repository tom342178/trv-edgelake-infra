"""Status models for EdgeLakeOperator CRD."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OperatorPhase(str, Enum):
    """Phases of the EdgeLake operator lifecycle."""

    PENDING = "Pending"
    CREATING = "Creating"
    RUNNING = "Running"
    UPDATING = "Updating"
    FAILED = "Failed"
    DELETING = "Deleting"


class ConditionStatus(str, Enum):
    """Status values for conditions."""

    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


class ConditionType(str, Enum):
    """Types of conditions."""

    READY = "Ready"
    AVAILABLE = "Available"
    PROGRESSING = "Progressing"
    DEGRADED = "Degraded"
    CONFIG_VALID = "ConfigValid"
    RESOURCES_CREATED = "ResourcesCreated"


class Condition(BaseModel):
    """A condition in the status."""

    type: str
    status: str
    lastTransitionTime: str = Field(alias="last_transition_time")
    reason: str
    message: str

    class Config:
        populate_by_name = True

    @classmethod
    def create(
        cls,
        condition_type: ConditionType,
        status: ConditionStatus,
        reason: str,
        message: str,
    ) -> "Condition":
        """Create a new condition with current timestamp."""
        return cls(
            type=condition_type.value,
            status=status.value,
            lastTransitionTime=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            message=message,
        )


class Endpoints(BaseModel):
    """Service endpoints for the operator."""

    tcp: Optional[str] = None
    rest: Optional[str] = None
    broker: Optional[str] = None


class OperatorStatus(BaseModel):
    """Status of an EdgeLakeOperator resource."""

    phase: str = OperatorPhase.PENDING.value
    conditions: list[Condition] = Field(default_factory=list)
    observedGeneration: Optional[int] = Field(default=None, alias="observed_generation")
    deploymentName: Optional[str] = Field(default=None, alias="deployment_name")
    serviceName: Optional[str] = Field(default=None, alias="service_name")
    configMapName: Optional[str] = Field(default=None, alias="config_map_name")
    secretName: Optional[str] = Field(default=None, alias="secret_name")
    pvcNames: list[str] = Field(default_factory=list, alias="pvc_names")
    endpoints: Endpoints = Field(default_factory=Endpoints)

    class Config:
        populate_by_name = True

    def set_condition(
        self,
        condition_type: ConditionType,
        status: ConditionStatus,
        reason: str,
        message: str,
    ) -> None:
        """Set or update a condition."""
        new_condition = Condition.create(condition_type, status, reason, message)

        # Find and replace existing condition of same type
        for i, cond in enumerate(self.conditions):
            if cond.type == condition_type.value:
                self.conditions[i] = new_condition
                return

        # Add new condition
        self.conditions.append(new_condition)

    def to_dict(self) -> dict:
        """Convert to dictionary for status update."""
        return self.model_dump(by_alias=True, exclude_none=True)
