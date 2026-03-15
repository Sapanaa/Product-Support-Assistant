"""
Tests covering:
  - catalog search tool behavior
  - stock check and related-item fallback
  - variant lookup tool
  - FastAPI endpoints
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.product import Product
from app.services.catalog_service import CatalogService
from app.services.stock_service import StockService
from app.repositories.product_repository import ProductRepository
from app.repositories.stock_repository import StockRepository
from app.agents.tools import (
    CatalogSearchTool, CatalogSearchInput,
    VariantLookupTool, VariantLookupInput,
    RelatedItemsTool, RelatedItemsInput,
    StockCheckTool, StockCheckInput,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_product() -> Product:
    return Product(
        model_code="120396",
        description="Papyrus large cooler bag 6L",
        keywords="cooler bag papyrus",
        item_code="12039601",
        size="ONE SIZE",
        category_code="bags",
        material="Non-woven polypropylene",
        simple_material="Non-woven polypropylene",
        green_points=14,
    )


@pytest.fixture
def product_repo(sample_product) -> ProductRepository:
    repo = MagicMock(spec=ProductRepository)
    repo.search_by_text.return_value = [sample_product]
    repo.find_by_item_code.return_value = sample_product
    repo.find_by_model_and_size.return_value = None
    repo.find_by_model_code.return_value = [sample_product]
    return repo


@pytest.fixture
def stock_repo() -> StockRepository:
    repo = MagicMock(spec=StockRepository)
    repo.is_in_stock.return_value = False   # item is out of stock by default
    repo.get_quantity.return_value = 0
    return repo


@pytest.fixture
def catalog_service(product_repo) -> CatalogService:
    return CatalogService(product_repo)


@pytest.fixture
def stock_service(stock_repo, product_repo) -> StockService:
    return StockService(stock_repo, product_repo)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Unit tests – catalog search tool
# ---------------------------------------------------------------------------

class TestCatalogSearchTool:
    def test_returns_matches_for_known_query(self, catalog_service, sample_product):
        tool = CatalogSearchTool(catalog_service)
        result = tool.run(CatalogSearchInput(query="Papyrus cooler bag"))
        assert result.total == 1
        assert result.matches[0]["item_code"] == "12039601"

    def test_returns_empty_for_unknown_query(self, product_repo, catalog_service):
        product_repo.search_by_text.return_value = []
        tool = CatalogSearchTool(catalog_service)
        result = tool.run(CatalogSearchInput(query="nonexistent product xyz"))
        assert result.total == 0
        assert result.matches == []

    def test_respects_top_k(self, product_repo, catalog_service, sample_product):
        product_repo.search_by_text.return_value = [sample_product, sample_product]
        tool = CatalogSearchTool(catalog_service)
        result = tool.run(CatalogSearchInput(query="bag", top_k=2))
        assert result.total == 2


# ---------------------------------------------------------------------------
# 2. Unit tests – stock check + related item fallback
# ---------------------------------------------------------------------------

class TestStockCheckTool:
    def test_out_of_stock_item(self, stock_service):
        tool = StockCheckTool(stock_service)
        result = tool.run(StockCheckInput(item_code="12039601"))
        assert result.in_stock is False
        assert result.quantity == 0

    def test_in_stock_item(self, stock_service, stock_repo):
        stock_repo.is_in_stock.return_value = True
        stock_repo.get_quantity.return_value = 5
        tool = StockCheckTool(stock_service)
        result = tool.run(StockCheckInput(item_code="12043500"))
        assert result.in_stock is True
        assert result.quantity == 5


class TestRelatedItemsTool:
    def test_returns_in_stock_variants(self, stock_service, stock_repo, product_repo, sample_product):
        """
        Same-model variant is in stock → should appear in related items.
        """
        # Give the product a non-empty related_items so the early-return guard is bypassed
        product_with_related = sample_product.model_copy(update={"related_items": "{}"})
        variant = product_with_related.model_copy(update={"item_code": "12039602", "size": "M"})
        # Primary item out of stock; variant in stock
        product_repo.find_by_item_code.return_value = product_with_related
        product_repo.find_by_model_code.return_value = [product_with_related, variant]
        stock_repo.is_in_stock.side_effect = lambda code: code == "12039602"

        tool = RelatedItemsTool(stock_service)
        result = tool.run(RelatedItemsInput(item_code="12039601"))
        assert result.total >= 1
        codes = [r["item_code"] for r in result.related]
        assert "12039602" in codes

    def test_returns_empty_when_no_related(self, stock_service, product_repo, stock_repo):
        product_repo.find_by_item_code.return_value = None
        tool = RelatedItemsTool(stock_service)
        result = tool.run(RelatedItemsInput(item_code="99999999"))
        assert result.total == 0
        assert result.related == []


# ---------------------------------------------------------------------------
# 3. Unit tests – variant lookup tool
# ---------------------------------------------------------------------------

class TestVariantLookupTool:
    def test_found(self, catalog_service, product_repo, sample_product):
        product_repo.find_by_model_and_size.return_value = sample_product
        tool = VariantLookupTool(catalog_service)
        result = tool.run(VariantLookupInput(model_code="120396", size="ONE SIZE"))
        assert result.found is True
        assert result.item_code == "12039601"

    def test_not_found(self, catalog_service, product_repo):
        product_repo.find_by_model_and_size.return_value = None
        tool = VariantLookupTool(catalog_service)
        result = tool.run(VariantLookupInput(model_code="999999", size="XL"))
        assert result.found is False
        assert result.item_code is None


# ---------------------------------------------------------------------------
# 4. API endpoint tests
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestTasksEndpoint:
    def test_create_task_catalog_search(self, client):
        resp = client.post(
            "/tasks",
            json={
                "input": "Find the item code for the Papyrus large cooler bag",
                "task_type": "product_support",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "completed"
        assert data["task_id"]
        assert "answer" in data["result"]
        assert len(data["steps"]) >= 1

    def test_create_task_variant_lookup(self, client):
        resp = client.post(
            "/tasks",
            json={
                "input": "Find the item code for model 38011 in size M",
                "task_type": "product_support",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "completed"

    def test_get_task_by_id(self, client):
        # Create first
        create_resp = client.post(
            "/tasks",
            json={
                "input": "What is the item code for the Oriole RPE bag?",
                "task_type": "product_support",
            },
        )
        task_id = create_resp.json()["task_id"]

        # Then retrieve
        get_resp = client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["task_id"] == task_id

    def test_get_task_not_found(self, client):
        resp = client.get("/tasks/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_empty_input_validation(self, client):
        resp = client.post(
            "/tasks",
            json={"input": "   ", "task_type": "product_support"},
        )
        assert resp.status_code == 422

    def test_invalid_task_type_validation(self, client):
        resp = client.post(
            "/tasks",
            json={"input": "hello", "task_type": "invalid_type"},
        )
        assert resp.status_code == 422

    def test_out_of_stock_related_items(self, client):
        resp = client.post(
            "/tasks",
            json={
                "input": "This item is out of stock, what similar items can I offer instead for Pheebs bag?",
                "task_type": "product_support",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "completed"
        assert "answer" in data["result"]