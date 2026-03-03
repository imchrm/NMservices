"""add_language_code_to_users

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
    """No-op: language_code already created in initial_schema."""
    pass


def downgrade() -> None:
    """No-op."""
    pass
