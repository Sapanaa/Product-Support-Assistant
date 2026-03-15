from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum
import uuid
from datetime import datetime, timezone

UTC = timezone.utc


class TaskType(str, Enum):
    product_support = "product_support"


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class AgentStep(BaseModel):
    tool_name: str
    input: Any
    output: Any


class TaskResult(BaseModel):
    answer: str
    item_code: Optional[str] = None
    matched_product: Optional[dict] = None
    related_items: Optional[list] = None


class Task(BaseModel):
    task_id: str
    status: TaskStatus
    input: str
    task_type: TaskType
    result: Optional[TaskResult] = None
    steps: list[AgentStep] = []
    created_at: datetime
    error: Optional[str] = None

    @classmethod
    def create(cls, input: str, task_type: TaskType) -> "Task":
        return cls(
            task_id=str(uuid.uuid4()),
            status=TaskStatus.pending,
            input=input,
            task_type=task_type,
            created_at=datetime.now(UTC),
        )
