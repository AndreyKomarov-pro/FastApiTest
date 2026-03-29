from uuid import UUID, uuid4
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func


class Base(DeclarativeBase):
    metadata = sa.MetaData()

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
    )
