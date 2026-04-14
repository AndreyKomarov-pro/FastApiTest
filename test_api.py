import httpx
import asyncio

BASE = "http://localhost:8000/api/v1"


async def main():
    async with httpx.AsyncClient(base_url=BASE) as client:

        print("\n=== 1. CATEGORY ===")
        r = await client.post("/categories/", json={"name": "Electronics", "description": "Tech stuff"})
        print(f"CREATE: {r.status_code} {r.json()}")
        category_id = r.json()["id"]

        r = await client.get("/categories/")
        print(f"LIST:   {r.status_code} total={r.json()['total']}")

        print("\n=== 2. PRODUCT ===")
        r = await client.post(f"/categories/{category_id}/products", json={
            "name": "Laptop",
            "description": "Good laptop",
            "price": "999.99",
            "quantity": 10,
        })
        print(f"CREATE: {r.status_code} {r.json()}")
        product_id = r.json()["id"]

        r = await client.get(f"/categories/{category_id}/products")
        print(f"LIST:   {r.status_code} total={r.json()['total']}")

        print("\n=== 3. USER ===")
        r = await client.post("/users/", json={"username": "john_doe"})
        print(f"CREATE: {r.status_code} {r.json()}")
        user_id = r.json()["id"]

        r = await client.get("/users/")
        print(f"LIST:   {r.status_code} total={r.json()['total']}")

        print("\n=== 4. CART ===")
        r = await client.post(f"/users/{user_id}/cart", json={"product_ids": [product_id]})
        print(f"CREATE: {r.status_code} {r.json()}")

        r = await client.get(f"/users/{user_id}/cart")
        print(f"GET:    {r.status_code} {r.json()}")

        print("\n=== 5. ORDER ===")
        r = await client.post("/orders/", json={
            "user_id": user_id,
            "item_ids": [{"product_id": product_id, "quantity": 2}],
        })
        print(f"CREATE: {r.status_code} {r.json()}")
        order_id = r.json()["id"]

        r = await client.get("/orders/")
        print(f"LIST:   {r.status_code} total={r.json()['total']}")

        print("\n=== 6. ORDER ITEM ===")
        r = await client.post(f"/orders/{order_id}/items", json={"product_id": product_id, "quantity": 3})
        print(f"CREATE: {r.status_code} {r.json()}")

        r = await client.get(f"/orders/{order_id}/items")
        print(f"LIST:   {r.status_code} count={len(r.json())}")

        print("\nDone!")


asyncio.run(main())
