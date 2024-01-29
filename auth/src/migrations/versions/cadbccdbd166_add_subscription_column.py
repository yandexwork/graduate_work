"""add subscription column

Revision ID: cadbccdbd166
Revises: 80f6f9179f43
Create Date: 2024-01-29 09:47:05.814550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cadbccdbd166'
down_revision: Union[str, None] = '80f6f9179f43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('subscription', sa.String(length=36), nullable=True))
    op.drop_column('users', 'is_subscribe')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_subscribe', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('users', 'subscription')
    # ### end Alembic commands ###