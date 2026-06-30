from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.enums.category_status import CategoryStatus
from src.models.category import CategoryModel

CLAIM_THRESHOLD_SECONDS = 300


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.products))
            .where(CategoryModel.is_deleted == False)
            .order_by(CategoryModel.created_at.desc())
            .with_for_update(skip_locked=True)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, category_id: UUID) -> CategoryModel | None:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.products))
            .where(CategoryModel.id == category_id, CategoryModel.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, category_id: UUID) -> CategoryModel | None:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.products))
            .where(CategoryModel.id == category_id, CategoryModel.is_deleted == False)
            .with_for_update(skip_locked=True)
        )
        return result.scalar_one_or_none()

    async def create(self, category: CategoryModel) -> CategoryModel:
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category, attribute_names=["products"])
        return category

    async def update(self, category: CategoryModel) -> CategoryModel:
        await self.session.flush()
        await self.session.refresh(category, attribute_names=["products"])
        return category

    async def delete(self, category: CategoryModel) -> None:
        category.is_deleted = True
        await self.session.flush()

    async def claim_pending(self, limit: int) -> list[CategoryModel]:
        subquery = (
            select(CategoryModel.id)
            .where(
                CategoryModel.status == CategoryStatus.PENDING,
                CategoryModel.is_deleted == False,
                (CategoryModel.claimed_at.is_(None)) | (CategoryModel.claimed_at < text(f"now() - interval '{CLAIM_THRESHOLD_SECONDS} seconds'")),
                (CategoryModel.next_retry_at.is_(None)) | (CategoryModel.next_retry_at <= text("now()")),
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        stmt = (
            update(CategoryModel)
            .where(CategoryModel.id.in_(subquery))
            .values(claimed_at=text("now()"))
            .returning(CategoryModel)
        )
        result = await self.session.execute(stmt)
        categories = list(result.scalars().all())
        await self.session.commit()
        for cat in categories:
            await self.session.refresh(cat, attribute_names=["products"])
        return categories

    async def update_status(
        self,
        category_id: UUID,
        new_status: CategoryStatus,
        expected_status: CategoryStatus | None = None,
        last_error: str | None = None,
    ) -> None:
        conditions = [CategoryModel.id == category_id]
        if expected_status:
            conditions.append(CategoryModel.status == expected_status)
        values = {
            "status": new_status,
            "claimed_at": None,
            "last_error": last_error,
        }
        await self.session.execute(
            update(CategoryModel).where(*conditions).values(**values)
        )
        await self.session.commit()

    async def increment_retry(
        self,
        category_id: UUID,
        next_retry_at: datetime,
        last_error: str | None = None,
    ) -> None:
        await self.session.execute(
            update(CategoryModel)
            .where(
                CategoryModel.id == category_id,
                CategoryModel.status == CategoryStatus.PENDING,
            )
            .values(
                retry_count=CategoryModel.retry_count + 1,
                next_retry_at=next_retry_at,
                claimed_at=None,
                last_error=last_error,
            )
        )
        await self.session.commit()
