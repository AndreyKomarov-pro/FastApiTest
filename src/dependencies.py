from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.repositories.catalog_repository import CatalogRepository
from src.repositories.user_repository import UserRepository
from src.repositories.orders_repository import OrdersRepository
from src.services.catalog_service import CatalogService
from src.services.users_service import UsersService
from src.services.orders_service import OrdersService

def get_catalog_service(session: AsyncSession = Depends(get_db)) -> CatalogService:
    return CatalogService(CatalogRepository(session))

def get_users_service(session: AsyncSession = Depends(get_db)) -> UsersService:
    return UsersService(UserRepository(session))

def get_orders_service(session: AsyncSession = Depends(get_db)) -> OrdersService:
    return OrdersService(OrdersRepository(session))
