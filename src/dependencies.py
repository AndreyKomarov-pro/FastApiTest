from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.repositories.category_repository import CategoryRepository
from src.repositories.user_repository import UserRepository
from src.repositories.orders_repository import OrdersRepository
from src.services.category_service import CategoryService
from src.services.users_service import UsersService
from src.services.orders_service import OrdersService

def get_category_service(session: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(session))

def get_users_service(session: AsyncSession = Depends(get_db)) -> UsersService:
    return UsersService(UserRepository(session))

def get_orders_service(session: AsyncSession = Depends(get_db)) -> OrdersService:
    return OrdersService(OrdersRepository(session))
