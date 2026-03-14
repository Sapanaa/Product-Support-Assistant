from app.models.task import Task
from fastapi import HTTPException


class TaskRepository:
    def __init__(self) -> None:
        self._store: dict[str, Task] = {}

    def save(self, task: Task) -> Task:
        self._store[task.task_id] = task
        return task

    def get(self, task_id: str) -> Task:
        task = self._store.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
        return task

    def all(self) -> list[Task]:
        return list(self._store.values())
