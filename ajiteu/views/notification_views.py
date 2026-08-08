from flask import Blueprint, redirect, url_for, g, render_template, jsonify

from ajiteu import db
from ajiteu.models import Notification
from ajiteu.views.auth_views import login_required
from ajiteu.jwt_utils import jwt_required_api

bp = Blueprint('notification', __name__, url_prefix='/notification')


@bp.route('/list/')
@login_required
def list_notifications():
    notifications = (
        Notification.query.filter_by(user_id=g.user.id)
        .order_by(Notification.create_date.desc())
        .limit(50)
        .all()
    )
    return render_template('notifications.html', notifications=notifications)


@bp.route('/read/<int:notification_id>/')
@login_required
def mark_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=g.user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    if notification.post_id:
        return redirect(url_for('post.detail', post_id=notification.post_id))
    return redirect(url_for('notification.list_notifications'))


@bp.route('/api/list')
@jwt_required_api
def api_list():
    notifications = (
        Notification.query.filter_by(user_id=g.user.id)
        .order_by(Notification.create_date.desc())
        .limit(50)
        .all()
    )
    return jsonify({
        'notifications': [
            {
                'id': n.id,
                'type': n.type,
                'message': n.message,
                'is_read': n.is_read,
                'post_id': n.post_id,
                'created_at': n.create_date.strftime('%Y.%m.%d %H:%M'),
            }
            for n in notifications
        ]
    })
