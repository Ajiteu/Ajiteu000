"""add social and admin models

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2026-08-07 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f1a2b3c4d5e6'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=20), server_default='user', nullable=False))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))

    op.create_table(
        'bookmark',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'post_id', name='uq_bookmark_user_post'),
    )
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
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('comment_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['comment_id'], ['comment.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'report',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('reported_user_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reported_user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reporter_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('report')
    op.drop_table('notification')
    op.drop_table('follow')
    op.drop_table('bookmark')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_active')
        batch_op.drop_column('role')
