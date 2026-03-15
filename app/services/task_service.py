from app.models.task import Task, TaskType
from app.repositories.task_repository import TaskRepository
from app.agents.orchestrator import AgentOrchestrator


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        orchestrator: AgentOrchestrator,
    ) -> None:
        self._repo = task_repo
        self._orchestrator = orchestrator

    def create_and_run(self, input: str, task_type: TaskType) -> Task:
        task = Task.create(input=input, task_type=task_type)
        self._repo.save(task)
        completed = self._orchestrator.run(task)
        self._repo.save(completed)
        return completed

    def get(self, task_id: str) -> Task:
        return self._repo.get(task_id)
