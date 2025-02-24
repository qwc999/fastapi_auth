"""Migration

Revision ID: c21300380edf
Revises: f93037fa2886
Create Date: 2025-02-24 23:27:22.609643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c21300380edf'
down_revision: Union[str, None] = 'f93037fa2886'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
