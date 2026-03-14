import csv
import re
from pathlib import Path
from typing import Optional
from app.models.product import Product

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "products_feed.csv"


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()


class ProductRepository:
    def __init__(self, csv_path: Path = DATA_PATH):
        self._products: list[Product] = []
        self._load(csv_path)

    def _load(self, path: Path) -> None:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    gp = row.get("green_points", "").strip()
                    self._products.append(
                        Product(
                            model_code=row["model_code"].strip(),
                            description=row["description"].strip(),
                            keywords=row.get("keywords", "").strip(),
                            item_code=row["item_code"].strip(),
                            size=row.get("size", "ONE SIZE").strip(),
                            category_code=row.get("category_code", "").strip(),
                            colors=row.get("colors", ""),
                            material=row.get("material", ""),
                            simple_material=row.get("simple_material", ""),
                            related_items=row.get("related_items", ""),
                            green_points=int(gp) if gp.isdigit() else None,
                        )
                    )
                except Exception:
                    continue

    def all(self) -> list[Product]:
        return list(self._products)

    def search_by_text(self, query: str, top_k: int = 5) -> list[Product]:
        """Fuzzy text match across description + keywords."""
        query_tokens = set(_normalize(query).split())
        if not query_tokens:
            return []

        scored: list[tuple[int, Product]] = []
        for p in self._products:
            haystack = _normalize(f"{p.description} {p.keywords}")
            tokens = set(haystack.split())
            score = len(query_tokens & tokens)
            if score > 0:
                scored.append((score, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:top_k]]

    def find_by_model_and_size(
        self, model_code: str, size: str
    ) -> Optional[Product]:
        size_norm = size.strip().upper()
        for p in self._products:
            if p.model_code == model_code and p.size.upper() == size_norm:
                return p
        return None

    def find_by_item_code(self, item_code: str) -> Optional[Product]:
        for p in self._products:
            if p.item_code == item_code:
                return p
        return None

    def find_by_model_code(self, model_code: str) -> list[Product]:
        return [p for p in self._products if p.model_code == model_code]
