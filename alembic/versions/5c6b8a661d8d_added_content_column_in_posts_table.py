"""added content column in posts table

Revision ID: 5c6b8a661d8d
Revises: 65cd913f8c9c
Create Date: 2026-06-05 19:41:52.355665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c6b8a661d8d'
down_revision: Union[str, Sequence[str], None] = '65cd913f8c9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
