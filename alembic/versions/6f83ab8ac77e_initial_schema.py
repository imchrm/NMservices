"""initial_schema

Baseline migration for existing database.
Tables 'users' and 'orders' already exist.

Revision ID: 6f83ab8ac77e
Revises:
Create Date: 2026-01-28 20:53:05.634474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f83ab8ac77e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline migration - tables already exist in DB."""
    # Existing tables: users, orders
    # This migration marks the starting point for Alembic tracking
    pass


def downgrade() -> None:
    """Cannot downgrade baseline migration."""
    pass
