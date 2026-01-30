"""add_language_code_to_users

Add language_code column to users table for storing user's preferred language.

Revision ID: a1b2c3d4e5f6
Revises: 5f637e23bc5d
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5f637e23bc5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add language_code column to users table."""
    op.add_column('users', sa.Column('language_code', sa.String(5), nullable=True))


def downgrade() -> None:
    """Remove language_code column from users table."""
    op.drop_column('users', 'language_code')
