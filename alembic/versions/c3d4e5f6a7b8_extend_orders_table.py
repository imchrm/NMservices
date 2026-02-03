"""extend_orders_table

Add service_id, address_text, scheduled_at columns to orders table.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add service_id, address_text, scheduled_at to orders table."""
    op.add_column('orders', sa.Column('service_id', sa.Integer(), nullable=True))
    op.add_column('orders', sa.Column('address_text', sa.Text(), nullable=True))
    op.add_column('orders', sa.Column('scheduled_at', sa.DateTime(), nullable=True))

    op.create_foreign_key(
        'fk_orders_service_id',
        'orders', 'services',
        ['service_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('idx_orders_service_id', 'orders', ['service_id'])


def downgrade() -> None:
    """Remove service_id, address_text, scheduled_at from orders table."""
    op.drop_index('idx_orders_service_id', table_name='orders')
    op.drop_constraint('fk_orders_service_id', 'orders', type_='foreignkey')
    op.drop_column('orders', 'scheduled_at')
    op.drop_column('orders', 'address_text')
    op.drop_column('orders', 'service_id')
