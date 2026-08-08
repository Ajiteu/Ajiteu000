from datetime import datetime

from flask import Blueprint, jsonify, request, g
from sqlalchemy import func, distinct, or_

from ajiteu import db
from ajiteu.models import Post, Comment, User, post_liker
from ajiteu.views.auth_views import login_required

bp = Blueprint('posts_api', __name__)

CATEGORIES = {
    'all': '전체',
    'travel': '여행',
    'exercise': '운동',
    'food': '음식',
}

CATEGORY_KEYWORDS = {
    'travel': ['여행', 'trip', 'travel', '관광', '휴가', '해외', '국내여행'],
    'exercise': ['운동', 'exercise', '헬스', '러닝', '런닝', '요가', '필라테스', '근력'],
    'food': ['음식', 'food', '맛집', '요리', '먹방', '카페', '식당', '맛있'],
}


def detect_category(content: str) -> str:
    """본문 키워드로 카테고리 자동 분류."""
    if not content:
        return 'all'
    text = content.lower()
    for cat_key, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return cat_key
    return 'all'


def build_category_filter(category: str):
    """내용에 카테고리 키워드가 포함된 글만 필터."""
    if not category or category == 'all':
        return None
    keywords = CATEGORY_KEYWORDS.get(category, [])
    if not keywords:
        return None
    return or_(*[Post.content.ilike(f'%{keyword}%') for keyword in keywords])


def build_post_query(category='all', kw='', user_id=None, so='recent'):
    """게시글 목록 공통 쿼리 (카테고리·검색·내 글 필터)."""
    post_list = Post.query

    if user_id is not None:
        post_list = post_list.filter(Post.user_id == user_id)

    category_filter = build_category_filter(category)
    if category_filter is not None:
        post_list = post_list.filter(category_filter)

    if kw:
        search = f'%%{kw}%%'
        sub_query = (
            db.session.query(Comment.post_id, Comment.content, User.username)
            .join(User, Comment.user_id == User.id)
            .subquery()
        )
        post_list = (
            post_list
            .outerjoin(sub_query, sub_query.c.post_id == Post.id)
            .filter(
                Post.content.ilike(search)
                | sub_query.c.content.ilike(search)
                | Post.user.has(User.username.ilike(search))
                | sub_query.c.username.ilike(search)
            )
        )

    if so == 'recommend':
        post_list = (
            post_list
            .outerjoin(post_liker, Post.id == post_liker.c.post_id)
            .group_by(Post.id)
            .order_by(func.count(distinct(Comment.id)).desc(), Post.create_date.desc())
        )
    elif so == 'popular':
        post_list = (
            post_list
            .outerjoin(post_liker, Post.id == post_liker.c.post_id)
            .group_by(Post.id)
            .order_by(func.count(post_liker.c.user_id).desc(), Post.create_date.desc())
        )
    else:
        post_list = post_list.group_by(Post.id).order_by(Post.create_date.desc())

    return post_list


def serialize_post(post):
    return {
        'id': post.id,
        'author': post.user.nickname or post.user.username,
        'created_at': post.create_date.strftime('%Y.%m.%d'),
        'content': post.content,
        'category': post.category,
        'like_count': len(post.liker),
        'comment_count': len(post.comment_set),
        'view_count': post.view_count or 0,
        'detail_url': f'/post/detail/{post.id}/',
    }


@bp.route('/api/posts')
@login_required
def api_posts():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').strip()
    mine = request.args.get('mine', 'false').lower() == 'true'
    so = request.args.get('so', 'recent')

    user_id = g.user.id if mine else None
    posts = build_post_query(
        category=category,
        kw=search,
        user_id=user_id,
        so=so,
    ).limit(50).all()

    return jsonify({
        'posts': [serialize_post(post) for post in posts],
        'category': category,
        'search': search,
        'mine': mine,
    })
