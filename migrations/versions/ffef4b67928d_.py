"""empty message

Revision ID: ffef4b67928d
Revises: 
Create Date: 2017-02-04 03:21:54.022210

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffef4b67928d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('requests',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('meal_type', sa.String(length=64), nullable=True),
    sa.Column('location_string', sa.String(length=128), nullable=True),
    sa.Column('meal_time', sa.String(length=32), nullable=True),
    sa.Column('latitude', sa.String(length=32), nullable=True),
    sa.Column('longitude', sa.String(length=32), nullable=True),
    sa.Column('filled', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_location_string'), 'requests', ['location_string'], unique=False)
    op.create_index(op.f('ix_requests_meal_time'), 'requests', ['meal_time'], unique=False)
    op.create_index(op.f('ix_requests_meal_type'), 'requests', ['meal_type'], unique=False)
    op.add_column(u'users', sa.Column('created', sa.DateTime(), nullable=False))
    op.add_column(u'users', sa.Column('updated', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'users', 'updated')
    op.drop_column(u'users', 'created')
    op.drop_index(op.f('ix_requests_meal_type'), table_name='requests')
    op.drop_index(op.f('ix_requests_meal_time'), table_name='requests')
    op.drop_index(op.f('ix_requests_location_string'), table_name='requests')
    op.drop_table('requests')
    # ### end Alembic commands ###
