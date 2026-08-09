from datetime import datetime

from ajiteu import db
from sqlalchemy import Table, UniqueConstraint

# 중간테이블
post_liker = Table(
    'post_liker',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True),
)

comment_liker = Table(
    'comment_liker',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), primary_key=True),
)

reply_liker = Table(
    'reply_liker',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('reply_id', db.Integer, db.ForeignKey('reply.id', ondelete='CASCADE'), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(120), nullable=False)
    user_intro = db.Column(db.Text(), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, server_default='user')
    is_active = db.Column(db.Boolean, nullable=False, server_default='1')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=False)
    category = db.Column(db.String(20), nullable=False, server_default='all')
    view_count = db.Column(db.Integer, nullable=False, server_default='0')
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    image_path = db.Column(db.Text(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('post_set'))
    liker = db.relationship(
        'User',
        secondary=post_liker,
        backref=db.backref('post_liker_set', lazy='dynamic'),
    )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    post = db.relationship(
        'Post',
        backref=db.backref('comment_set', cascade='all, delete-orphan'),
    )
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    image_path = db.Column(db.Text(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('comment_set'))
    liker = db.relationship(
        'User', secondary=comment_liker, backref=db.backref('comment_liker_set', lazy='dynamic')
    )


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('reply_set'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=True)
    post = db.relationship('Post', backref=db.backref('reply_set'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), nullable=True)
    comment = db.relationship(
        'Comment',
        backref=db.backref('reply_set', cascade='all, delete-orphan'),
    )
    liker = db.relationship(
        'User', secondary=reply_liker, backref=db.backref('reply_liker_set', lazy='dynamic')
    )


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    user = db.relationship('User', backref=db.backref('bookmark_set'))
    post = db.relationship(
        'Post',
        backref=db.backref('bookmark_set', cascade='all, delete-orphan'),
    )

    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='uq_bookmark_user_post'),)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, server_default='0')
    create_date = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notification_set'))
    actor = db.relationship('User', foreign_keys=[actor_id])


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    reason = db.Column(db.Text(), nullable=False)
    status = db.Column(db.String(20), nullable=False, server_default='pending')
    create_date = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref=db.backref('report_set'))
