from flask import Blueprint, render_template, request, g, url_for, redirect

from ajiteu.views.auth_views import login_required
from ajiteu.views.posts_views import build_post_query, CATEGORIES
from ajiteu.views.trend_views import get_weekly_trends

bp = Blueprint('my_posts', __name__)


@bp.route('/my-posts')
@login_required
def my_posts():
    if g.user is None:
        return redirect(url_for('auth.login'))

    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    category = request.args.get('category', type=str, default='all')
    so = request.args.get('so', type=str, default='recent')

    post_list = build_post_query(
        category=category,
        kw=kw,
        user_id=g.user.id,
        so=so,
    ).paginate(page=page, per_page=10)

    weekly_trends = get_weekly_trends()

    return render_template(
        'main.html',
        post_list=post_list,
        page=page,
        kw=kw,
        so=so,
        category=category,
        user=g.user,
        is_my_posts=True,
        categories=CATEGORIES,
        weekly_trends=weekly_trends,
    )
