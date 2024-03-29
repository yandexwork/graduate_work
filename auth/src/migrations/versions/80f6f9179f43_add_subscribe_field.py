"""add subscribe field

Revision ID: 80f6f9179f43
Revises: 4523b79517b2
Create Date: 2024-01-23 17:10:16.355956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80f6f9179f43'
down_revision: Union[str, None] = '4523b79517b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_subscribe', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_subscribe')
    # ### end Alembic commands ###
