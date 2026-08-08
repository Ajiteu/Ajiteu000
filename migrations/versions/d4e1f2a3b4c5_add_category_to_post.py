"""add category to post

Revision ID: d4e1f2a3b4c5
Revises: 099b2efa47e8
Create Date: 2026-08-07 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e1f2a3b4c5'
down_revision = '099b2efa47e8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('category', sa.String(length=20), server_default='all', nullable=False)
        )


def downgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('category')
