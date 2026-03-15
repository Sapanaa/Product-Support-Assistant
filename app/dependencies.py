"""
Dependency container – single source of truth for wiring all services.
Import get_task_service() wherever the service is needed (FastAPI Depends, tests, etc.)
"""

from functools import lru_cache
from app.repositories.product_repository import ProductRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.task_repository import TaskRepository
from app.services.catalog_service import CatalogService
from app.services.stock_service import StockService
from app.services.task_service import TaskService
from app.agents.tools import (
    CatalogSearchTool,
    VariantLookupTool,
    RelatedItemsTool,
    StockCheckTool,
)
from app.agents.orchestrator import AgentOrchestrator


@lru_cache(maxsize=1)
def _build_container() -> TaskService:
    product_repo = ProductRepository()
    stock_repo = StockRepository()
    task_repo = TaskRepository()

    catalog_svc = CatalogService(product_repo)
    stock_svc = StockService(stock_repo, product_repo)

    orchestrator = AgentOrchestrator(
        catalog_search=CatalogSearchTool(catalog_svc),
        variant_lookup=VariantLookupTool(catalog_svc),
        related_items=RelatedItemsTool(stock_svc),
        stock_check=StockCheckTool(stock_svc),
    )

    return TaskService(task_repo=task_repo, orchestrator=orchestrator)


def get_task_service() -> TaskService:
    return _build_container()
