"""empty message

Revision ID: 17996805fe42
Revises: 
Create Date: 2017-01-01 13:55:25.435007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17996805fe42'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('host',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('create_at', sa.DateTime(), nullable=False),
    sa.Column('ip', sa.String(length=15), nullable=False),
    sa.Column('hostname', sa.String(length=50), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=True),
    sa.Column('state', sa.Enum(u'\u65b0\u52a0\u5165', u'\u914d\u7f6e\u4e2d', u'\u914d\u7f6e\u5b8c\u6210', u'\u914d\u7f6e\u5931\u8d25'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('service',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('host_service_map',
    sa.Column('host_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['host_id'], [u'host.id'], ),
    sa.ForeignKeyConstraint(['service_id'], [u'service.id'], ),
    sa.PrimaryKeyConstraint('host_id', 'service_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('host_service_map')
    op.drop_table('service')
    op.drop_table('host')
    # ### end Alembic commands ###
