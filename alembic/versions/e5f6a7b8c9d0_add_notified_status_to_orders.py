"""add notified_status to orders

Add notified_status column to orders table for tracking
which status change the user has been notified about.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-02-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("notified_status", sa.String(50), nullable=True),
    )
    # Set notified_status = status for existing orders
    # (assume all existing users have already been notified)
    op.execute("UPDATE orders SET notified_status = status")


def downgrade() -> None:
    op.drop_column("orders", "notified_status")
