"""add condition ondelete

Revision ID: 0006
Revises: 0005
Create Date: 2022-06-08 18:35:12.354622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('families_parent_id_fkey', 'families', type_='foreignkey')
    op.drop_constraint('families_student_id_fkey', 'families', type_='foreignkey')
    op.create_foreign_key(None, 'families', 'parents', ['parent_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'families', 'students', ['student_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'families', type_='foreignkey')
    op.drop_constraint(None, 'families', type_='foreignkey')
    op.create_foreign_key('families_student_id_fkey', 'families', 'students', ['student_id'], ['id'])
    op.create_foreign_key('families_parent_id_fkey', 'families', 'parents', ['parent_id'], ['id'])
    # ### end Alembic commands ###
