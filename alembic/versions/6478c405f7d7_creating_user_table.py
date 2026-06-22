"""creating user table

Revision ID: 6478c405f7d7
Revises: 5c6b8a661d8d
Create Date: 2026-06-05 19:56:58.393909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6478c405f7d7'
down_revision: Union[str, Sequence[str], None] = '5c6b8a661d8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
