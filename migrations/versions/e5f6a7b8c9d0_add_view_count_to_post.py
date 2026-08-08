"""add view_count to post

Revision ID: e5f6a7b8c9d0
Revises: d4e1f2a3b4c5
Create Date: 2026-08-07 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e5f6a7b8c9d0'
down_revision = 'd4e1f2a3b4c5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('view_count', sa.Integer(), server_default='0', nullable=False)
        )


def downgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('view_count')
