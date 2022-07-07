"""delete condition nullable in teacher table

Revision ID: 0023
Revises: 0022
Create Date: 2022-07-05 19:14:09.437711

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0023'
down_revision = '0022'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('groups_teacher_id_fkey', 'groups', type_='foreignkey')
    op.create_foreign_key(None, 'groups', 'teachers', ['teacher_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'groups', type_='foreignkey')
    op.create_foreign_key('groups_teacher_id_fkey', 'groups', 'teachers', ['teacher_id'], ['id'])
    # ### end Alembic commands ###