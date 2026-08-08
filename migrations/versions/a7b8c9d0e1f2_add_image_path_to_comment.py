"""add image_path to comment

Revision ID: a7b8c9d0e1f2
Revises: f1a2b3c4d5e6
Create Date: 2026-08-08 01:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a7b8c9d0e1f2'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_path', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_column('image_path')
