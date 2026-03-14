from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    model_code: str
    description: str
    keywords: str
    item_code: str
    size: str
    category_code: str
    colors: Optional[str] = None
    material: Optional[str] = None
    simple_material: Optional[str] = None
    related_items: Optional[str] = None
    green_points: Optional[int] = None
