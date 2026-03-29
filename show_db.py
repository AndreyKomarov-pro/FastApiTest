import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from src.database import SessionFactory
from src.models import UserModel, CategoryModel, ProductModel, OrderModel, OrderItemModel, CartModel


async def show_all():
    async with SessionFactory() as session:

        print("=== USERS ===")
        users = await session.execute(select(UserModel))
        for user in users.scalars():
            print(f"  ID: {user.id} | Username: {user.username} | Created: {user.created_at}")

        print("\n=== CATEGORIES ===")
        categories = await session.execute(select(CategoryModel))
        for cat in categories.scalars():
            print(f"  ID: {cat.id} | Name: {cat.name} | Desc: {cat.description}")

        print("\n=== PRODUCTS ===")
        products = await session.execute(select(ProductModel))
        for prod in products.scalars():
            print(f"  ID: {prod.id} | Name: {prod.name} | Price: {prod.price} | Category: {prod.category_id}")

        print("\n=== CARTS ===")
        carts = await session.execute(select(CartModel))
        for cart in carts.scalars():
            print(f"  ID: {cart.id} | User: {cart.user_id}")

        print("\n=== ORDERS ===")
        orders = await session.execute(select(OrderModel))
        for order in orders.scalars():
            print(f"  ID: {order.id} | User: {order.user_id} | Status: {order.status} | Total: {order.total_amount}")

        print("\n=== ORDER ITEMS ===")
        items = await session.execute(select(OrderItemModel))
        for item in items.scalars():
            print(f"  ID: {item.id} | Order: {item.order_id} | Product: {item.product_id} | Qty: {item.quantity} | Price: {item.price}")


asyncio.run(show_all())
