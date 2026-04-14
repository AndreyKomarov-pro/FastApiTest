from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.catalog_service import CatalogService


def get_catalog_service(session: AsyncSession = Depends(get_db)) -> CatalogService:
    return CatalogService(session)
