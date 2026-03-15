# from app.repositories.product_repository import ProductRepository

# repo = ProductRepository()

# # Test 1: total products loaded
# products = repo.all()
# print("Total products:", len(products))

# # Test 2: search
# results = repo.search_by_text("cooler bag")
# print("\nSearch results:")
# for p in results:
#     print(p.item_code, "-", p.description)

# # Test 3: find by item code
# product = repo.find_by_item_code("12039601")
# print("\nFind by item code:")
# print(product)

# # Test 4: find by model + size
# product = repo.find_by_model_and_size("120396", "")
# print("\nFind by model + size:")
# print(product)


# from app.repositories.stock_repository import StockRepository

# repo = StockRepository()

# # Test 1: quantity lookup
# print("Quantity for 12043500:", repo.get_quantity("12043500"))

# # Test 2: check stock availability
# print("Is 12039601 in stock?", repo.is_in_stock("12039601"))
# print("Is 12043500 in stock?", repo.is_in_stock("12043500"))

# # Test 3: get full stock map
# stock = repo.get_stock_map()
# print("Total items in stock map:", len(stock))
# print("Sample:", list(stock.items())[:5])

# from app.repositories.task_repository import TaskRepository
# from app.models.task import Task, TaskType

# repo = TaskRepository()

# # create task using factory method
# task = Task.create(
#     input="Find item code for cooler bag",
#     task_type=TaskType.product_support,
# )

# # save task
# repo.save(task)

# # retrieve task
# retrieved = repo.get(task.task_id)
# print("Retrieved task:", retrieved)

# # list all tasks
# print("All tasks:", repo.all())

# from app.repositories.product_repository import ProductRepository
# from app.services.catalog_service import CatalogService

# # create repository
# repo = ProductRepository()

# # create service
# catalog = CatalogService(repo)

# # Test 1: search
# results = catalog.search("cooler bag")
# print("\nSearch results:")
# for p in results:
#     print(p.item_code, "-", p.description)

# # Test 2: get by item code
# product = catalog.get_by_item_code("12039601")
# print("\nProduct by item code:")
# print(product)

# # Test 3: get by model and size
# product = catalog.get_by_model_and_size("38106", "2XL")
# print("\nProduct by model + size:")
# print(product)

# # Test 4: get variants
# variants = catalog.get_variants("38106")
# print("\nVariants for model 38106:")
# for v in variants:
#     print(v.item_code, v.size)



from app.repositories.product_repository import ProductRepository
from app.repositories.stock_repository import StockRepository
from app.services.stock_service import StockService


# initialize repositories
product_repo = ProductRepository()
stock_repo = StockRepository()

# create service
stock_service = StockService(stock_repo, product_repo)


# Test 1: quantity
print("\nQuantity for 12043500:")
print(stock_service.get_quantity("12043500"))


# Test 2: stock check
print("\nIs 12039601 in stock?")
print(stock_service.is_in_stock("12039601"))


# Test 3: related items in stock
print("\nRelated items in stock for 12039601:")

related = stock_service.get_related_in_stock("12046050")

for p in related:
    print(p.item_code, "-", p.description)