from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from src.database import get_db
from src.cache.redis_client import RedisClient, get_redis
from src.clients.product_info_client import ProductInfoClient
from src.repositories.category_repository import CategoryRepository
from src.repositories.user_repository import UserRepository
from src.repositories.orders_repository import OrdersRepository
from src.services.category_service import CategoryService
from src.services.users_service import UsersService
from src.services.orders_service import OrdersService


def get_redis_client(client: redis.Redis = Depends(get_redis)) -> RedisClient:
    return RedisClient(client)


def get_product_info_client() -> ProductInfoClient:
    return ProductInfoClient()


def get_category_service(
    session: AsyncSession = Depends(get_db),
    cache: RedisClient = Depends(get_redis_client),
    product_info_client: ProductInfoClient = Depends(get_product_info_client),
) -> CategoryService:
    return CategoryService(CategoryRepository(session), cache, product_info_client)


def get_users_service(
    session: AsyncSession = Depends(get_db),
    cache: RedisClient = Depends(get_redis_client),
) -> UsersService:
    return UsersService(UserRepository(session), cache)


def get_orders_service(
    session: AsyncSession = Depends(get_db),
    cache: RedisClient = Depends(get_redis_client),
) -> OrdersService:
    return OrdersService(OrdersRepository(session), cache)
