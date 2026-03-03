"""add_telegram_id_to_users

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
    """No-op: telegram_id already created in initial_schema."""
    pass


def downgrade() -> None:
    """No-op."""
    pass
