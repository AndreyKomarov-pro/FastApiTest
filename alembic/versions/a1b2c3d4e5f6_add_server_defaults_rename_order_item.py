"""add server defaults to created_at, rename OrderItemModel to OrderItem

Revision ID: a1b2c3d4e5f6
Revises: 90127ec355d4
Create Date: 2026-03-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '90127ec355d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES_WITH_CREATED_AT = ("users", "categories", "products", "carts", "orders")


def upgrade() -> None:
    for table in TABLES_WITH_CREATED_AT:
        op.alter_column(
            table,
            "created_at",
            server_default=sa.text("now()"),
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )


def downgrade() -> None:
    for table in TABLES_WITH_CREATED_AT:
        op.alter_column(
            table,
            "created_at",
            server_default=None,
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
        )
