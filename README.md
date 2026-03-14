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