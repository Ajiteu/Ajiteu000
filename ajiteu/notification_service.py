from datetime import datetime

from ajiteu import db
from ajiteu.models import Notification


def create_notification(user_id, actor_id, ntype, message, post_id=None, comment_id=None):
    """알림 생성 (본인 행동은 알림 제외)."""
    if user_id == actor_id:
        return None

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=ntype,
        message=message,
        post_id=post_id,
        comment_id=comment_id,
        is_read=False,
        create_date=datetime.now(),
    )
    db.session.add(notification)
    return notification
