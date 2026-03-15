# Product Support Assistant

A FastAPI support agent that answers retail product questions by querying a live product catalog — returning item codes, stock status, and alternative suggestions when items are unavailable.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-red?logo=pydantic&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Pytest-yellow?logo=pytest&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker&logoColor=white)
![Docker Hub](https://img.shields.io/badge/Docker_Hub-sapana444%2Fproduct--support--assistant-2496ED?logo=docker&logoColor=white)

---

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`  
Swagger UI at `http://localhost:8000/docs`

---

## Dataset

Place your catalog file at `data/products_feed.csv`. 

The file is loaded into memory on startup — no database setup required. Required columns:

```
model_code, description, keywords, item_code, size,
category_code, colors, material, simple_material, related_items, green_points
```

To use your own dataset, replace the file and restart the server.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/tasks` | Create and run a support task |
| `GET` | `/tasks/{task_id}` | Retrieve a task by ID |

**Example request:**

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"input": "Find the item code for the Papyrus large cooler bag", "task_type": "product_support"}'
```

**Example response:**

```json
{
  "task_id": "3f7a1c22-...",
  "status": "completed",
  "result": {
    "answer": "The item code is 12039601.",
    "item_code": "12039601",
    "matched_product": {
      "model_code": "120396",
      "description": "Papyrus large cooler bag 6L"
    }
  },
  "steps": [
    {
      "tool_name": "catalog_search",
      "input": { "query": "Find the item code for the Papyrus large cooler bag" },
      "output": { "matches": ["12039601"], "total": 1 }
    }
  ]
}
```

---

## Agent Tools

The agent routes each query to the appropriate tool chain based on intent.

| Tool | Purpose |
|------|---------|
| `catalog_search` | Fuzzy search by product name or description |
| `variant_lookup` | Exact lookup by model code + size |
| `stock_check` | Check availability for an item code |
| `related_items` | Find in-stock alternatives when an item is unavailable |

---

## Stock Fallback

When an item is out of stock, `related_items` searches for alternatives in two ways:

1. **Explicit relations** — parses item codes from the product's `related_items` CSV field and returns those currently in stock
2. **Size variants** — finds all items sharing the same `model_code` and returns available sizes

---

## Design

- **Deterministic routing** — no LLM required. Intent is detected via keyword matching in `orchestrator.py`. The routing method is isolated so an LLM can be swapped in without touching any other layer.
- **Layered architecture** — `HTTP → Service → Agent → Tools → Repositories`. Each layer is independently replaceable.
- **In-memory persistence** — tasks stored in a dictionary. The `TaskRepository` interface supports a drop-in SQLite or PostgreSQL replacement.
- **Execution trace** — every response includes the full list of tool calls and their outputs for observability.

---

## Tests

```bash
pytest tests/ -v
```

---

## Docker

A pre-built image is available on Docker Hub.

```bash
# Pull and run the published image
docker pull sapana444/product-support-assistant:latest
docker run -p 8000:8000 sapana444/product-support-assistant:latest
```

Or build locally from source:

```bash
docker build -t catalogagent .
docker run -p 8000:8000 catalogagent
```

> **Image:** [`sapana444/product-support-assistant`](https://hub.docker.com/r/sapana444/product-support-assistant)

---

## CI/CD

GitHub Actions pipeline defined in `.github/workflows/ci-cd.yml`:

```
push → Lint → Test → Build → Deploy (main branch only)
```

Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` to your repository secrets to enable the deploy step.