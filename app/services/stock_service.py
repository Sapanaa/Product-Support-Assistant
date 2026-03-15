import re
from typing import Optional
from app.repositories.stock_repository import StockRepository
from app.repositories.product_repository import ProductRepository
from app.models.product import Product


class StockService:
    def __init__(
        self,
        stock_repo: StockRepository,
        product_repo: ProductRepository,
    ) -> None:
        self._stock = stock_repo
        self._products = product_repo

    def is_in_stock(self, item_code: str) -> bool:
        return self._stock.is_in_stock(item_code)

    def get_quantity(self, item_code: str) -> int:
        return self._stock.get_quantity(item_code)

    def get_related_in_stock(self, item_code: str) -> list[Product]:
        """
        Parse the related_items JSON-like field for a product and return
        those that are currently in stock.
        """
        product = self._products.find_by_item_code(item_code)
        if not product or not product.related_items:
            return []

        # Extract all item codes referenced in related_items string
        related_codes = re.findall(r"\b\d{8}\b", product.related_items)

        results: list[Product] = []
        for code in related_codes:
            related = self._products.find_by_item_code(code)
            if related and self._stock.is_in_stock(code):
                results.append(related)

        # Also try same model_code, different size/variant
        same_model = self._products.find_by_model_code(product.model_code)
        for variant in same_model:
            if variant.item_code != item_code and self._stock.is_in_stock(
                variant.item_code
            ):
                if variant not in results:
                    results.append(variant)

        return results
