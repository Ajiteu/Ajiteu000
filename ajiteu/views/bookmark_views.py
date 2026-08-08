from datetime import datetime

from flask import Blueprint, redirect, url_for, flash, g, render_template, request

from ajiteu import db
from ajiteu.models import Bookmark, Post
from ajiteu.views.auth_views import login_required
from ajiteu.views.posts_views import CATEGORIES, build_post_query
from ajiteu.views.trend_views import get_weekly_trends

bp = Blueprint('bookmark', __name__, url_prefix='/bookmark')


@bp.route('/add/<int:post_id>/')
@login_required
def add(post_id):
    post = Post.query.get_or_404(post_id)
    exists = Bookmark.query.filter_by(user_id=g.user.id, post_id=post_id).first()
    if exists:
        flash('이미 북마크한 글입니다.', 'info')
    else:
        bookmark = Bookmark(user_id=g.user.id, post_id=post_id, create_date=datetime.now())
        db.session.add(bookmark)
        db.session.commit()
        flash('북마크에 추가했습니다.', 'success')
    return redirect(request.referrer or url_for('post.detail', post_id=post_id))


@bp.route('/remove/<int:post_id>/')
@login_required
def remove(post_id):
    bookmark = Bookmark.query.filter_by(user_id=g.user.id, post_id=post_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        flash('북마크를 해제했습니다.', 'success')
    return redirect(request.referrer or url_for('bookmark.list_bookmarks'))


@bp.route('/list/')
@login_required
def list_bookmarks():
    page = request.args.get('page', type=int, default=1)
    post_ids = [b.post_id for b in Bookmark.query.filter_by(user_id=g.user.id).all()]
    if post_ids:
        post_list = (
            Post.query.filter(Post.id.in_(post_ids))
            .order_by(Post.create_date.desc())
            .paginate(page=page, per_page=10)
        )
    else:
        post_list = Post.query.filter(Post.id == -1).paginate(page=page, per_page=10)

    return render_template(
        'main.html',
        post_list=post_list,
        page=page,
        kw='',
        so='recent',
        category='all',
        user=g.user,
        is_my_posts=False,
        is_bookmarks=True,
        categories=CATEGORIES,
        weekly_trends=get_weekly_trends(),
    )
