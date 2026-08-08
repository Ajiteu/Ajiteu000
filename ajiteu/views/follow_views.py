from datetime import datetime

from flask import Blueprint, redirect, url_for, flash, g, render_template, request

from ajiteu import db
from ajiteu.models import Follow, User
from ajiteu.notification_service import create_notification
from ajiteu.views.auth_views import login_required

bp = Blueprint('follow', __name__, url_prefix='/follow')


@bp.route('/add/<int:user_id>/')
@login_required
def add(user_id):
    target = User.query.get_or_404(user_id)
    if g.user.id == user_id:
        flash('본인은 팔로우할 수 없습니다.', 'warning')
        return redirect(request.referrer or url_for('post._list', username_id=g.user.id))

    exists = Follow.query.filter_by(follower_id=g.user.id, following_id=user_id).first()
    if exists:
        flash('이미 팔로우 중입니다.', 'info')
    else:
        follow = Follow(follower_id=g.user.id, following_id=user_id, create_date=datetime.now())
        db.session.add(follow)
        create_notification(
            user_id=user_id,
            actor_id=g.user.id,
            ntype='follow',
            message=f'{g.user.nickname}님이 회원님을 팔로우했습니다.',
        )
        db.session.commit()
        flash('팔로우했습니다.', 'success')
    return redirect(request.referrer or url_for('profile.view', username_id=user_id))


@bp.route('/remove/<int:user_id>/')
@login_required
def remove(user_id):
    follow = Follow.query.filter_by(follower_id=g.user.id, following_id=user_id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash('언팔로우했습니다.', 'success')
    return redirect(request.referrer or url_for('profile.view', username_id=user_id))


@bp.route('/followers/<int:user_id>/')
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    follows = Follow.query.filter_by(following_id=user_id).all()
    users = [f.follower for f in follows]
    return render_template('follow_list.html', title='팔로워', users=users, target_user=user)


@bp.route('/following/<int:user_id>/')
@login_required
def following(user_id):
    user = User.query.get_or_404(user_id)
    follows = Follow.query.filter_by(follower_id=user_id).all()
    users = [f.following for f in follows]
    return render_template('follow_list.html', title='팔로잉', users=users, target_user=user)
