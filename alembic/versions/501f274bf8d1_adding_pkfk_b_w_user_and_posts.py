"""adding pkfk b/w user and posts

Revision ID: 501f274bf8d1
Revises: 6478c405f7d7
Create Date: 2026-06-05 20:24:55.329828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '501f274bf8d1'
down_revision: Union[str, Sequence[str], None] = '6478c405f7d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.add_column('posts', sa.Column('user_id', sa.Integer(), nullable=False))
    
    op.create_foreign_key(
        'posts_user_fk',  #name of foregin key
        source_table='posts',  #where does it exits
        referent_table='users', #which table does it refferance
        local_cols=['user_id'],  #in source_table which col u want matched with referenct_table
        remote_cols=['user_id'], #the name of col we match in ref table
        ondelete='CASCADE', #yk
        onupdate='SET DEFAULT' #yk make sure no underscore!
    )
    
    #Explain:
    """
        user_id = Column(
        Integer, 
        ForeignKey("users.user_id", ondelete="CASCADE", onupdate="SET_DEFAULT"), 
        nullable=False
    )
    
    """

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('posts_user_fk', table_name='posts')
    op.drop_column('posts', 'user_id')
    pass
