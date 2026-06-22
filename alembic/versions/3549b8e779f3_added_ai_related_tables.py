"""added ai related tables

Revision ID: 3549b8e779f3
Revises: f5f22ea69882
Create Date: 2026-06-14 01:59:32.816752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3549b8e779f3'
down_revision: Union[str, Sequence[str], None] = 'f5f22ea69882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Inside your Alembic migration file

def upgrade() -> None:
    # 1. Manually add the explicit table creation block
    op.create_table(
        'ai_usage_tracker',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('last_used', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_ai_usage_tracker_id'), 'ai_usage_tracker', ['id'], unique=False)


def downgrade() -> None:
    # 2. Manually add the explicit table destruction block
    op.drop_index(op.f('ix_ai_usage_tracker_id'), table_name='ai_usage_tracker')
    op.drop_table('ai_usage_tracker')
