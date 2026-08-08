from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import func

from ajiteu import db
from ajiteu.models import Post, post_liker
from ajiteu.views.auth_views import login_required

bp = Blueprint('trend', __name__)


def get_weekly_trends(limit=5):
    """최근 7일 게시글 중 좋아요 수 상위 글."""
    week_ago = datetime.now() - timedelta(days=7)

    return (
        db.session.query(Post)
        .filter(Post.create_date >= week_ago)
        .outerjoin(post_liker, Post.id == post_liker.c.post_id)
        .group_by(Post.id)
        .order_by(func.count(post_liker.c.user_id).desc(), Post.create_date.desc())
        .limit(limit)
        .all()
    )


@bp.route('/api/trends/weekly')
@login_required
def weekly_trends_api():
    trends = get_weekly_trends()
    return jsonify({
        'trends': [
            {
                'id': post.id,
                'title': post.content[:30] + ('...' if len(post.content) > 30 else ''),
                'like_count': len(post.liker),
                'detail_url': f'/post/detail/{post.id}/',
            }
            for post in trends
        ]
    })
