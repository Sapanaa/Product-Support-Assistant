"""
AgentOrchestrator
-----------------
Lightweight deterministic agent.
Routing is keyword/pattern-based (no LLM required), making behavior fully
predictable and testable. The architecture is designed so a real LLM router
can be dropped in by replacing _route().
"""

import re
from app.models.task import Task, TaskStatus, TaskResult, AgentStep
from app.agents.tools import (
    CatalogSearchTool,
    CatalogSearchInput,
    VariantLookupTool,
    VariantLookupInput,
    RelatedItemsTool,
    RelatedItemsInput,
    StockCheckTool,
    StockCheckInput,
)


class AgentOrchestrator:
    def __init__(
        self,
        catalog_search: CatalogSearchTool,
        variant_lookup: VariantLookupTool,
        related_items: RelatedItemsTool,
        stock_check: StockCheckTool,
    ) -> None:
        self._catalog_search = catalog_search
        self._variant_lookup = variant_lookup
        self._related_items = related_items
        self._stock_check = stock_check

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, task: Task) -> Task:
        try:
            steps: list[AgentStep] = []
            result = self._route(task.input, steps)
            return task.model_copy(
                update={
                    "status": TaskStatus.completed,
                    "result": result,
                    "steps": steps,
                }
            )
        except Exception as exc:
            return task.model_copy(
                update={
                    "status": TaskStatus.failed,
                    "error": str(exc),
                }
            )

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def _route(self, user_input: str, steps: list[AgentStep]) -> TaskResult:
        text = user_input.lower()

        # Intent: variant lookup (model code + size)
        size_pattern = re.search(
            r"\b(xs|s|m|l|xl|xxl|3xl|4xl|one size)\b", text, re.IGNORECASE
        )
        model_pattern = re.search(r"\bmodel\s+(\w+)\b", text, re.IGNORECASE)
        if model_pattern and size_pattern:
            return self._handle_variant_lookup(
                model_pattern.group(1),
                size_pattern.group(1).upper(),
                steps,
            )

        # Intent: out of stock / related items / alternatives
        if any(
            kw in text
            for kw in (
                "out of stock",
                "unavailable",
                "similar",
                "alternative",
                "replacement",
                "related",
            )
        ):
            return self._handle_related_items(user_input, steps)

        # Intent: stock check only
        if any(kw in text for kw in ("in stock", "available", "stock")):
            return self._handle_stock_check(user_input, steps)

        # Default: catalog search
        return self._handle_catalog_search(user_input, steps)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_catalog_search(self, query: str, steps: list[AgentStep]) -> TaskResult:
        inp = CatalogSearchInput(query=query)
        out = self._catalog_search.run(inp)
        steps.append(
            AgentStep(
                tool_name=self._catalog_search.name,
                input={"query": query},
                output={
                    "matches": [m["item_code"] for m in out.matches],
                    "total": out.total,
                },
            )
        )

        if not out.matches:
            return TaskResult(
                answer="No matching products found in the catalog for your query.",
                item_code=None,
                matched_product=None,
            )

        best = out.matches[0]
        return TaskResult(
            answer=f"The item code is {best['item_code']}.",
            item_code=best["item_code"],
            matched_product={
                "model_code": best["model_code"],
                "description": best["description"],
            },
        )

    def _handle_variant_lookup(
        self, model_code: str, size: str, steps: list[AgentStep]
    ) -> TaskResult:
        inp = VariantLookupInput(model_code=model_code, size=size)
        out = self._variant_lookup.run(inp)
        steps.append(
            AgentStep(
                tool_name=self._variant_lookup.name,
                input={"model_code": model_code, "size": size},
                output={"found": out.found, "item_code": out.item_code},
            )
        )

        if not out.found or not out.product:
            return TaskResult(
                answer=f"No item found for model {model_code} in size {size}.",
                item_code=None,
                matched_product=None,
            )

        return TaskResult(
            answer=f"The item code for model {model_code} in size {size} is {out.item_code}.",
            item_code=out.item_code,
            matched_product={
                "model_code": out.product["model_code"],
                "description": out.product["description"],
            },
        )

    def _handle_related_items(self, query: str, steps: list[AgentStep]) -> TaskResult:
        # First find the product being referenced
        search_inp = CatalogSearchInput(query=query)
        search_out = self._catalog_search.run(search_inp)
        steps.append(
            AgentStep(
                tool_name=self._catalog_search.name,
                input={"query": query},
                output={"matches": [m["item_code"] for m in search_out.matches]},
            )
        )

        if not search_out.matches:
            return TaskResult(
                answer="Could not identify the product. Please provide more details.",
            )

        primary = search_out.matches[0]
        item_code = primary["item_code"]

        # Check stock
        stock_inp = StockCheckInput(item_code=item_code)
        stock_out = self._stock_check.run(stock_inp)
        steps.append(
            AgentStep(
                tool_name=self._stock_check.name,
                input={"item_code": item_code},
                output={"in_stock": stock_out.in_stock, "quantity": stock_out.quantity},
            )
        )

        # Get related items
        related_inp = RelatedItemsInput(item_code=item_code)
        related_out = self._related_items.run(related_inp)
        steps.append(
            AgentStep(
                tool_name=self._related_items.name,
                input={"item_code": item_code},
                output={
                    "related": [r["item_code"] for r in related_out.related],
                    "total": related_out.total,
                },
            )
        )

        stock_msg = (
            f"Item {item_code} is currently out of stock."
            if not stock_out.in_stock
            else f"Item {item_code} is in stock (qty: {stock_out.quantity})."
        )

        if related_out.total == 0:
            return TaskResult(
                answer=f"{stock_msg} No alternative items are currently available.",
                item_code=item_code,
                matched_product={
                    "model_code": primary["model_code"],
                    "description": primary["description"],
                },
                related_items=[],
            )

        related_summary = ", ".join(r["item_code"] for r in related_out.related[:5])
        return TaskResult(
            answer=(
                f"{stock_msg} "
                f"Here are {related_out.total} alternative item(s) in stock: {related_summary}."
            ),
            item_code=item_code,
            matched_product={
                "model_code": primary["model_code"],
                "description": primary["description"],
            },
            related_items=related_out.related[:5],
        )

    def _handle_stock_check(self, query: str, steps: list[AgentStep]) -> TaskResult:
        search_inp = CatalogSearchInput(query=query)
        search_out = self._catalog_search.run(search_inp)
        steps.append(
            AgentStep(
                tool_name=self._catalog_search.name,
                input={"query": query},
                output={"matches": [m["item_code"] for m in search_out.matches]},
            )
        )

        if not search_out.matches:
            return TaskResult(answer="Product not found.")

        primary = search_out.matches[0]
        stock_inp = StockCheckInput(item_code=primary["item_code"])
        stock_out = self._stock_check.run(stock_inp)
        steps.append(
            AgentStep(
                tool_name=self._stock_check.name,
                input={"item_code": primary["item_code"]},
                output={"in_stock": stock_out.in_stock, "quantity": stock_out.quantity},
            )
        )

        status = "in stock" if stock_out.in_stock else "out of stock"
        return TaskResult(
            answer=f"Item {primary['item_code']} ({primary['description']}) is currently {status} (qty: {stock_out.quantity}).",
            item_code=primary["item_code"],
            matched_product={
                "model_code": primary["model_code"],
                "description": primary["description"],
            },
        )
