from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.orders_service import OrdersService


def get_orders_service(session: AsyncSession = Depends(get_db)) -> OrdersService:
    return OrdersService(session)
