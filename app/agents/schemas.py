from pydantic import BaseModel, field_validator
from typing import Any, Optional
from app.models.task import TaskType, TaskStatus, AgentStep, TaskResult


class CreateTaskRequest(BaseModel):
    input: str
    task_type: TaskType

    @field_validator("input")
    @classmethod
    def input_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("input must not be empty")
        return v.strip()


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[TaskResult] = None
    steps: list[AgentStep] = []
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
