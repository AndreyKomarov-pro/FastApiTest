import httpx
import asyncio

BASE = "http://localhost:8000/api/v1"


async def main():
    async with httpx.AsyncClient(base_url=BASE) as client:

        print("\n=== 1. CATEGORY ===")
        r = await client.post("/categories/", json={"name": "Electronics", "description": "Tech stuff"})
        print(f"CREATE: {r.status_code} {r.json()}")
        category_id = r.json()["id"]

        r = await client.get(f"/categories/{category_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.patch(f"/categories/{category_id}", json={"name": "Updated", "description": "Updated"})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 2. USER ===")
        r = await client.post("/users/", json={"username": "john_doe"})
        print(f"CREATE: {r.status_code} {r.json()}")
        user_id = r.json()["id"]

        r = await client.get(f"/users/{user_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.patch(f"/users/{user_id}", json={"username": "john_updated"})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 3. PRODUCT (вложенная категория) ===")
        r = await client.post("/products/", json={
            "name": "Laptop",
            "description": "Good",
            "price": 999.99,
            "quantity": 10,
            "category": {"name": "Electronics", "description": "Tech stuff"}
        })
        print(f"CREATE: {r.status_code} {r.json()}")
        product_id = r.json()["id"]

        r = await client.get(f"/products/{product_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.patch(f"/products/{product_id}", json={
            "name": "Laptop Pro",
            "price": 1299.99,
            "quantity": 5
        })
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 4. CART (вложенный пользователь) ===")
        r = await client.post("/carts/", json={
            "user": {"username": "cart_user"}
        })
        print(f"CREATE: {r.status_code} {r.json()}")
        cart_id = r.json()["id"]

        r = await client.get(f"/carts/{cart_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        print("\n=== 5. ORDER (вложенный пользователь + вложенные items) ===")
        r = await client.post("/orders/", json={
            "user": {"username": "order_user"},
            "items": [
                {
                    "product": {
                        "name": "Laptop Pro",
                        "description": "Best laptop",
                        "price": 1299.99,
                        "quantity": 5,
                        "category": {"name": "Electronics", "description": "Tech"}
                    },
                    "quantity": 2
                }
            ]
        })
        print(f"CREATE: {r.status_code} {r.json()}")
        order_id = r.json()["id"]

        r = await client.get(f"/orders/{order_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.patch(f"/orders/{order_id}", json={"status": "paid"})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 6. ORDER ITEM (вложенный продукт) ===")
        r = await client.post(f"/order-items/{order_id}/items", json={
            "product": {
                "name": "Mouse",
                "description": "Wireless",
                "price": 49.99,
                "quantity": 100,
                "category": {"name": "Accessories", "description": "PC accessories"}
            },
            "quantity": 3
        })
        print(f"CREATE: {r.status_code} {r.json()}")
        item_id = r.json()["id"]

        r = await client.get(f"/order-items/{item_id}")
        print(f"GET:    {r.status_code} {r.json()}")

        r = await client.patch(f"/order-items/{item_id}", json={"quantity": 5})
        print(f"UPDATE: {r.status_code} {r.json()}")

        print("\n=== 7. DELETE ===")
        r = await client.delete(f"/order-items/{item_id}")
        print(f"DELETE order_item: {r.status_code}")

        r = await client.delete(f"/orders/{order_id}")
        print(f"DELETE order:      {r.status_code}")

        r = await client.delete(f"/carts/{cart_id}")
        print(f"DELETE cart:       {r.status_code}")

        r = await client.delete(f"/products/{product_id}")
        print(f"DELETE product:    {r.status_code}")

        r = await client.delete(f"/users/{user_id}")
        print(f"DELETE user:       {r.status_code}")

        r = await client.delete(f"/categories/{category_id}")
        print(f"DELETE category:   {r.status_code}")

        print("\n✅ Готово!")


asyncio.run(main())

# ЗАПУСК:
# python test_api.py