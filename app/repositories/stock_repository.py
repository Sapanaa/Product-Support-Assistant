"""
Dummy stock repository.
In production this would integrate with a real inventory system.
"""

# item_code -> quantity in stock
_DUMMY_STOCK: dict[str, int] = {
    "12039601": 0,  # out of stock intentionally for demo
    "12043500": 15,
    "12045200": 8,
    "12046000": 0,  # out of stock
    "12046050": 3,
    "12046090": 12,
    "12046100": 7,
    "12046101": 2,
    "12046102": 5,
    "12046103": 9,
    "12046104": 4,
    "12046111": 0,  # out of stock
    "12046131": 6,
    "12046137": 11,
    "12046150": 1,
    "38011001": 20,
    "38011002": 18,
    "38011003": 14,
    "38011004": 0,  # out of stock
    "38011005": 3,
}


class StockRepository:
    def get_quantity(self, item_code: str) -> int:
        return _DUMMY_STOCK.get(item_code, 0)

    def is_in_stock(self, item_code: str) -> bool:
        return self.get_quantity(item_code) > 0

    def get_stock_map(self) -> dict[str, int]:
        return dict(_DUMMY_STOCK)
