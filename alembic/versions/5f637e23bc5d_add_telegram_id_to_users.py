"""add_telegram_id_to_users

Add telegram_id column to users table for Telegram user identification.

Revision ID: 5f637e23bc5d
Revises: 6f83ab8ac77e
Create Date: 2026-01-28 20:53:55.425961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f637e23bc5d'
down_revision: Union[str, Sequence[str], None] = '6f83ab8ac77e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add telegram_id column with unique index."""
    op.add_column('users', sa.Column('telegram_id', sa.BigInteger(), nullable=True))
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)


def downgrade() -> None:
    """Remove telegram_id column and index."""
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_column('users', 'telegram_id')
