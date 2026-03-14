from app.repositories.product_repository import ProductRepository

repo = ProductRepository()

# Test 1: total products loaded
products = repo.all()
print("Total products:", len(products))

# Test 2: search
results = repo.search_by_text("cooler bag")
print("\nSearch results:")
for p in results:
    print(p.item_code, "-", p.description)

# Test 3: find by item code
product = repo.find_by_item_code("12039601")
print("\nFind by item code:")
print(product)

# Test 4: find by model + size
product = repo.find_by_model_and_size("120396", "")
print("\nFind by model + size:")
print(product)