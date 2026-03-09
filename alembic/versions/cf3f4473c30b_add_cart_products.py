"""add cart_products

Revision ID: cf3f4473c30b
Revises: fb03a1a093dd
Create Date: 2026-03-09 16:58:59.940522

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'cf3f4473c30b'
down_revision: Union[str, Sequence[str], None] = 'fb03a1a093dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cart_products',
        sa.Column('cart_id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('cart_id', 'product_id')
    )


def downgrade() -> None:
    op.drop_table('cart_products')