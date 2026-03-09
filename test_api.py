import httpx
import asyncio

BASE = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient(base_url=BASE) as client:

        print("\n=== 1. CATEGORY ===")
        r = await client.post("/category/", json={"name": "Electronics", "description": "Tech stuff"})
        print(f"CREATE: {r.status_code} {r.json()}")
        category_id = r.json()["id"]

        r = await client.get(f"/category/{category_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.put(f"/category/{category_id}", json={"name": "Updated", "description": "Updated"})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 2. USER ===")
        r = await client.post("/users/", json={"username": "john_doe"})
        print(f"CREATE: {r.status_code} {r.json()}")
        user_id = r.json()["id"]

        r = await client.get(f"/users/{user_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.put(f"/users/{user_id}", json={"username": "john_updated"})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 3. PRODUCT ===")
        r = await client.post("/products/", json={"name": "Laptop", "description": "Good", "price": 999.99, "quantity": 10, "category_id": category_id})
        print(f"CREATE: {r.status_code} {r.json()}")
        product_id = r.json()["id"]

        r = await client.get(f"/products/{product_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.put(f"/products/{product_id}", json={"name": "Laptop Pro", "description": "Better", "price": 1299.99, "quantity": 5, "category_id": category_id})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 4. CART (1:1 с User) ===")
        r = await client.post("/carts/", json={"user_id": user_id})
        print(f"CREATE: {r.status_code} {r.json()}")
        cart_id = r.json()["id"]

        r = await client.get(f"/carts/{cart_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        print("\n=== 5. ORDER ===")
        r = await client.post("/orders/", json={"user_id": user_id, "items": [{"product_id": product_id, "quantity": 2}]})
        print(f"CREATE: {r.status_code} {r.json()}")
        order_id = r.json()["id"]

        r = await client.get(f"/orders/{order_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.put(f"/orders/{order_id}", json={"user_id": user_id, "items": []})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 6. ORDER ITEM ===")
        r = await client.post(f"/order-items/{order_id}/items", json={"product_id": product_id, "quantity": 3})
        print(f"CREATE: {r.status_code} {r.json()}")
        item_id = r.json()["id"]

        r = await client.get(f"/order-items/{item_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.put(f"/order-items/{item_id}", json={"product_id": product_id, "quantity": 5})
        print(f"UPDATE: {r.status_code} {r.json()}")

        #  РАЗКОМЕНТИТЬ, ЕСЛИ НУЖНО, ЧТО БЫ ПОСЛЕ ТЕСТОВ, БАЗА ОЧИЩАЛАСЬ ОТ ТЕСТ ЗНАЧЕНИЙ
        # print("\n=== 7. DELETE ===")
        # r = await client.delete(f"/order-items/{item_id}")
        # print(f"DELETE order_item: {r.status_code} {r.json()}")
        # r = await client.delete(f"/orders/{order_id}")
        # print(f"DELETE order:      {r.status_code} {r.json()}")
        # r = await client.delete(f"/carts/{cart_id}")
        # print(f"DELETE cart:       {r.status_code} {r.json()}")
        # r = await client.delete(f"/products/{product_id}")
        # print(f"DELETE product:    {r.status_code} {r.json()}")
        # r = await client.delete(f"/users/{user_id}")
        # print(f"DELETE user:       {r.status_code} {r.json()}")
        # r = await client.delete(f"/category/{category_id}")
        # print(f"DELETE category:   {r.status_code} {r.json()}")
        # print("\n✅ Готово!")

asyncio.run(main())

# ЗАПУСК:
#  python test_api.py


# cd C:\PyCharm\JetBrains\FastApiTest   docker compose down -v    docker compose up --build    docker compose exec app env