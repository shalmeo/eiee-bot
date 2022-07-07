"""add condition on delete set null

Revision ID: 0027
Revises: 0026
Create Date: 2022-07-07 01:33:08.554574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0027'
down_revision = '0026'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('groups_admin_id_fkey', 'groups', type_='foreignkey')
    op.create_foreign_key(None, 'groups', 'administrators', ['admin_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint('students_admin_id_fkey', 'students', type_='foreignkey')
    op.create_foreign_key(None, 'students', 'administrators', ['admin_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint('teachers_admin_id_fkey', 'teachers', type_='foreignkey')
    op.create_foreign_key(None, 'teachers', 'administrators', ['admin_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'teachers', type_='foreignkey')
    op.create_foreign_key('teachers_admin_id_fkey', 'teachers', 'administrators', ['admin_id'], ['id'])
    op.drop_constraint(None, 'students', type_='foreignkey')
    op.create_foreign_key('students_admin_id_fkey', 'students', 'administrators', ['admin_id'], ['id'])
    op.drop_constraint(None, 'groups', type_='foreignkey')
    op.create_foreign_key('groups_admin_id_fkey', 'groups', 'administrators', ['admin_id'], ['id'])
    # ### end Alembic commands ###
