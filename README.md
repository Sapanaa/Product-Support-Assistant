# Product Support Assistant


## Product Repository

The `ProductRepository` is responsible for loading product data from a CSV file and providing methods to search and retrieve products.

### Features

- Load products from `data/products_feed.csv`
- Search products using text (description + keywords)
- Retrieve products by item code
- Retrieve products by model code
- Retrieve products by model code and size


## Available Methods

- all() – return all loaded products
- search_by_text(query) – search products by keywords
- find_by_item_code(item_code) – find a product by item code
- find_by_model_code(model_code) – get all products with the same model
- find_by_model_and_size(model_code, size) – find a product by model and size

----

## Stock Repository

The `StockRepository` simulates a simple inventory system.  
It provides stock information for products using a dummy in-memory dataset.

This repository is used for development and testing purposes. In a real production system, it would connect to an external inventory or warehouse management system.

### Features

- Retrieve stock quantity by item code
- Check if a product is in stock
- Access the full stock dataset

### Available Methods

- get_quantity(item_code) – returns the quantity available for an item
- is_in_stock(item_code) – returns True if the product is available
- get_stock_map() – returns all stock data

---
## Task Repository

The `TaskRepository` is an in-memory storage used to manage tasks.  
It stores tasks in a dictionary where the key is the `task_id`.

This repository is mainly used for temporary storage during runtime.

### Features

- Save tasks
- Retrieve tasks by ID
- List all stored tasks
- Returns a `404` error if a task is not found


### Available Methods

- save(task) – stores a task in memory
- get(task_id) – retrieves a task by ID
- all() – returns all stored tasks

User
  │
  ▼
FastAPI Endpoint
  │
  ▼
Task.create()
  │
  ▼
TaskRepository.save()
  │
  ▼
Agent processes request
  │
  ▼
Task updated with result

----

## Catalog Service

The `CatalogService` provides a layer between the API/agent and the product repository.  
It exposes simple methods for searching products and retrieving product information.

### Features

- Search products by text query
- Retrieve product by item code
- Retrieve product by model code and size
- Retrieve all variants of a product model

### Methods

- search(query) – search products using description and keywords
- get_by_item_code(item_code) – retrieve a product by item code
- get_by_model_and_size(model_code, size) – retrieve a product variant
- get_variants(model_code) – return all variants of a product mode

---
## Stock Service

The `StockService` handles stock availability and quantity checks for products.  
It combines data from the `StockRepository` and `ProductRepository` to provide inventory information and suggest alternatives when a product is out of stock.

### Features

- Check if a product is in stock
- Retrieve the available quantity of a product
- Suggest related or variant products that are currently in stock

### Methods

- is_in_stock(item_code) – returns True if the product is available in stock
- get_quantity(item_code) – returns the quantity available for the item
- get_related_in_stock(item_code) – returns related or variant products that are currently in stock