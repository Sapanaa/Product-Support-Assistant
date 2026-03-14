from typing import Optional
from app.repositories.product_repository import ProductRepository
from app.models.product import Product


class CatalogService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    def search(self, query: str, top_k: int = 5) -> list[Product]:
        return self._repo.search_by_text(query, top_k)

    def get_by_model_and_size(
        self, model_code: str, size: str
    ) -> Optional[Product]:
        return self._repo.find_by_model_and_size(model_code, size)

    def get_by_item_code(self, item_code: str) -> Optional[Product]:
        return self._repo.find_by_item_code(item_code)

    def get_variants(self, model_code: str) -> list[Product]:
        return self._repo.find_by_model_code(model_code)
