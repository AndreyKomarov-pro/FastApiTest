from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.users_service import UsersService


def get_users_service(session: AsyncSession = Depends(get_db)) -> UsersService:
    return UsersService(session)
