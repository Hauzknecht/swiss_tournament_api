"""empty message

Revision ID: 937f8046f5a6
Revises: 366e631bd5a9
Create Date: 2024-04-11 12:22:47.931087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '937f8046f5a6'
down_revision = '366e631bd5a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=80), nullable=False))

    # ### end Alembic commands ###
