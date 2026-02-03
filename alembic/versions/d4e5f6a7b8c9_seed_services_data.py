"""seed_services_data

Add initial services data.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert initial services data."""
    op.execute("""
        INSERT INTO services (name, description, base_price, duration_minutes, is_active)
        VALUES
            ('Классический массаж', 'Расслабляющий массаж всего тела', 150000.00, 60, true),
            ('Спортивный массаж', 'Массаж для восстановления после тренировок', 180000.00, 60, true),
            ('Массаж спины', 'Массаж спины и шейно-воротниковой зоны', 100000.00, 30, true),
            ('Антицеллюлитный массаж', 'Массаж проблемных зон', 200000.00, 45, true)
    """)


def downgrade() -> None:
    """Remove initial services data."""
    op.execute("""
        DELETE FROM services
        WHERE name IN (
            'Классический массаж',
            'Спортивный массаж',
            'Массаж спины',
            'Антицеллюлитный массаж'
        )
    """)
