"""drop follow table

Revision ID: b2c3d4e5f6a7
Revises: a7b8c9d0e1f2
Create Date: 2026-08-09 09:55:00.000000

"""
from alembic import op


revision = 'b2c3d4e5f6a7'
down_revision = 'a7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('follow')


def downgrade():
    import sqlalchemy as sa

    op.create_table(
        'follow',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('following_id', sa.Integer(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['following_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('follower_id', 'following_id', name='uq_follow_pair'),
    )
