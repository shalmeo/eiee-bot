"""delete cloumn role

Revision ID: 0031
Revises: 0030
Create Date: 2022-07-11 01:10:17.201885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0031'
down_revision = '0030'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('unregistered_users', 'role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('unregistered_users', sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
