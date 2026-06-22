"""adding the remaning cols in posts

Revision ID: c09a501f3371
Revises: 501f274bf8d1
Create Date: 2026-06-05 20:41:55.634898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c09a501f3371'
down_revision: Union[str, Sequence[str], None] = '501f274bf8d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Command 1: Add the published column
    op.add_column(
        'posts', 
        sa.Column('published', sa.Boolean(), nullable=False, server_default='true')
    )
    
    # Command 2: Add the created_at column (with its name string included!)
    op.add_column(
        'posts', 
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'created_at')
    op.drop_column('posts', 'published')
