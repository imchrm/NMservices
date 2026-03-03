"""initial_schema

Create complete database schema: users, services, orders tables
with all columns, indexes, and seed data.

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
    """Create complete database schema."""
    # ── users ──────────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('language_code', sa.String(5), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_users_phone_number', 'users', ['phone_number'],
                    unique=True)
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'],
                    unique=True)

    # ── services ───────────────────────────────────────────────────────
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_price', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False,
                  server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('idx_services_is_active', 'services', ['is_active'])

    # ── orders ─────────────────────────────────────────────────────────
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(),
                  sa.ForeignKey('users.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('service_id', sa.Integer(),
                  sa.ForeignKey('services.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('status', sa.String(50), nullable=False,
                  server_default='pending'),
        sa.Column('notified_status', sa.String(50), nullable=True),
        sa.Column('total_amount', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('address_text', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('idx_orders_user_id', 'orders', ['user_id'])
    op.create_index('idx_orders_service_id', 'orders', ['service_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])

    # ── seed services ──────────────────────────────────────────────────
    op.execute("""
        INSERT INTO services (name, description, base_price, duration_minutes, is_active)
        VALUES
            ('Классический массаж', 'Расслабляющий массаж всего тела', 150000.00, 60, true),
            ('Спортивный массаж', 'Массаж для восстановления после тренировок', 180000.00, 60, true),
            ('Массаж спины', 'Массаж спины и шейно-воротниковой зоны', 100000.00, 30, true),
            ('Антицеллюлитный массаж', 'Массаж проблемных зон', 200000.00, 45, true)
    """)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('orders')
    op.drop_table('services')
    op.drop_table('users')
