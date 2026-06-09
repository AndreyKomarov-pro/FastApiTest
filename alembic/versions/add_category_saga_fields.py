"""add category saga fields

Revision ID: a1b2c3d4e5f6
Revises: 7cffbf0f2224
Create Date: 2026-06-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7cffbf0f2224'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'))
    op.add_column('categories', sa.Column('idempotency_key', sa.Uuid(), nullable=True))
    op.add_column('categories', sa.Column('payload_json', sa.Text(), nullable=True))
    op.add_column('categories', sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('categories', sa.Column('retry_count', sa.Integer(), nullable=False, server_default=sa.text('0')))
    op.add_column('categories', sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('categories', sa.Column('last_error', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('categories', 'last_error')
    op.drop_column('categories', 'claimed_at')
    op.drop_column('categories', 'retry_count')
    op.drop_column('categories', 'next_retry_at')
    op.drop_column('categories', 'payload_json')
    op.drop_column('categories', 'idempotency_key')
    op.drop_column('categories', 'status')
