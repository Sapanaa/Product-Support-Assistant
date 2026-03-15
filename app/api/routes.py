from fastapi import APIRouter, Depends
from app.agents.schemas import CreateTaskRequest, TaskResponse, HealthResponse
from app.services.task_service import TaskService
from app.dependencies import get_task_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", message="Support Agent API is running.")


@router.post("/tasks", response_model=TaskResponse, status_code=201, tags=["tasks"])
def create_task(
    body: CreateTaskRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = service.create_and_run(input=body.input, task_type=body.task_type)
    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        result=task.result,
        steps=task.steps,
        error=task.error,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = service.get(task_id)
    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        result=task.result,
        steps=task.steps,
        error=task.error,
    )
