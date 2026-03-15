"""
Agent tool definitions.
Each tool is a plain callable that accepts structured input and returns structured output.
Tools are stateless; dependencies are injected at construction time.
"""
from dataclasses import dataclass, field
from typing import Optional
from app.services.catalog_service import CatalogService
from app.services.stock_service import StockService
from app.models.product import Product


# ---------------------------------------------------------------------------
# Input / Output dataclasses (lightweight, no HTTP concern)
# ---------------------------------------------------------------------------

@dataclass
class CatalogSearchInput:
    query: str
    top_k: int = 5


@dataclass
class CatalogSearchOutput:
    matches: list[dict]
    total: int


@dataclass
class VariantLookupInput:
    model_code: str
    size: str


@dataclass
class VariantLookupOutput:
    item_code: Optional[str]
    product: Optional[dict]
    found: bool


@dataclass
class RelatedItemsInput:
    item_code: str


@dataclass
class RelatedItemsOutput:
    related: list[dict]
    total: int


@dataclass
class StockCheckInput:
    item_code: str


@dataclass
class StockCheckOutput:
    item_code: str
    in_stock: bool
    quantity: int


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _product_to_dict(p: Product) -> dict:
    return {
        "item_code": p.item_code,
        "model_code": p.model_code,
        "description": p.description,
        "size": p.size,
        "material": p.simple_material or p.material,
        "green_points": p.green_points,
    }


class CatalogSearchTool:
    name = "catalog_search"

    def __init__(self, catalog: CatalogService) -> None:
        self._catalog = catalog

    def run(self, inp: CatalogSearchInput) -> CatalogSearchOutput:
        results = self._catalog.search(inp.query, inp.top_k)
        return CatalogSearchOutput(
            matches=[_product_to_dict(p) for p in results],
            total=len(results),
        )


class VariantLookupTool:
    name = "variant_lookup"

    def __init__(self, catalog: CatalogService) -> None:
        self._catalog = catalog

    def run(self, inp: VariantLookupInput) -> VariantLookupOutput:
        product = self._catalog.get_by_model_and_size(inp.model_code, inp.size)
        if product:
            return VariantLookupOutput(
                item_code=product.item_code,
                product=_product_to_dict(product),
                found=True,
            )
        return VariantLookupOutput(item_code=None, product=None, found=False)


class RelatedItemsTool:
    name = "related_items"

    def __init__(self, stock: StockService) -> None:
        self._stock = stock

    def run(self, inp: RelatedItemsInput) -> RelatedItemsOutput:
        products = self._stock.get_related_in_stock(inp.item_code)
        return RelatedItemsOutput(
            related=[_product_to_dict(p) for p in products],
            total=len(products),
        )


class StockCheckTool:
    name = "stock_check"

    def __init__(self, stock: StockService) -> None:
        self._stock = stock

    def run(self, inp: StockCheckInput) -> StockCheckOutput:
        return StockCheckOutput(
            item_code=inp.item_code,
            in_stock=self._stock.is_in_stock(inp.item_code),
            quantity=self._stock.get_quantity(inp.item_code),
        )
