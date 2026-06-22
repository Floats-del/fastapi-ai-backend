"""creating post table

Revision ID: 65cd913f8c9c
Revises: 
Create Date: 2026-06-05 19:24:34.243383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65cd913f8c9c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    #u can look up the docomentaion for each operation dw
    
    op.create_table('posts', 
                    (sa.Column('post_id', sa.Integer(), nullable=False, primary_key=True)),\
                    (sa.Column('title', sa.String(), nullable=False))
    )
                    
    #tables created, ik idh content rn... dw its on purpose! ill add that in new snapshot ;)


def downgrade() -> None:
    """Downgrade schema."""
    
    #if we make table we must delete it too ;)
    op.drop_table('posts')
    
