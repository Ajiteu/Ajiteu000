from ajiteu import db
from ajiteu.models import Post, User
from ajiteu.views.auth_views import login_required
from ajiteu.views.posts_views import build_post_query, CATEGORIES, detect_category
from ajiteu.views.trend_views import get_weekly_trends
from ajiteu.forms import PostForm, CommentForm, ImageUploadForm
from ajiteu.notification_service import create_notification
from ajiteu.models import Bookmark
from flask import (
    Blueprint, render_template, url_for, redirect, request, g, flash,
    current_app, session, send_from_directory,
)
from datetime import datetime
import os
import uuid


bp = Blueprint('post', __name__, url_prefix='/post')


def _save_post_images(image_files):
    image_paths = []
    today = datetime.now().strftime('%Y%m%d')
    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'posts', today)
    os.makedirs(upload_folder, exist_ok=True)

    if image_files:
        for image_file in image_files:
            if image_file and image_file.filename:
                ext = os.path.splitext(image_file.filename)[1]
                filename = f'{uuid.uuid4()}{ext}'
                file_path = os.path.join(upload_folder, filename)
                image_file.save(file_path)
                image_paths.append(f'images/posts/{today}/{filename}')
    return ','.join(image_paths) if image_paths else None


@bp.route('/list/<int:username_id>')
@login_required
def _list(username_id):
    user = User.query.get_or_404(username_id)
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    category = request.args.get('category', type=str, default='all')
    so = request.args.get('so', type=str, default='recent')

    post_list = build_post_query(category=category, kw=kw, so=so).paginate(page=page, per_page=10)
    weekly_trends = get_weekly_trends()

    return render_template(
        'main.html',
        post_list=post_list,
        page=page,
        kw=kw,
        so=so,
        category=category,
        user=user,
        is_my_posts=False,
        categories=CATEGORIES,
        weekly_trends=weekly_trends,
    )


@bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
def user_posts(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    category = request.args.get('category', type=str, default='all')
    so = request.args.get('so', type=str, default='recent')

    post_list = build_post_query(
        category=category, kw=kw, user_id=user_id, so=so,
    ).paginate(page=page, per_page=10)
    weekly_trends = get_weekly_trends()

    return render_template(
        'main.html',
        post_list=post_list,
        page=page,
        kw=kw,
        so=so,
        category=category,
        user=user,
        is_my_posts=(user_id == g.user.id),
        categories=CATEGORIES,
        weekly_trends=weekly_trends,
    )


@bp.route('/create/<int:username_id>', methods=('GET', 'POST'))
@login_required
def create(username_id):
    user = User.query.get_or_404(username_id)
    if g.user.id != username_id:
        flash('본인 계정으로만 글을 작성할 수 있습니다.', 'danger')
        return redirect(url_for('post._list', username_id=g.user.id))

    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        post = Post(
            content=form.content.data,
            category=detect_category(form.content.data),
            create_date=datetime.now(),
            user=g.user,
            image_path=_save_post_images(form.image.data),
        )
        db.session.add(post)
        db.session.commit()
        flash('게시글이 등록되었습니다.', 'success')
        return redirect(url_for('post._list', username_id=user.id))

    weekly_trends = get_weekly_trends()
    return render_template(
        'post_create.html',
        form=form,
        user=user,
        categories=CATEGORIES,
        weekly_trends=weekly_trends,
    )


@bp.route('/detail/<int:post_id>/')
@login_required
def detail(post_id):
    comment_form = CommentForm()
    post = Post.query.get_or_404(post_id)

    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    category = request.args.get('category', type=str, default='all')
    so = request.args.get('so', type=str, default='recent')

    viewed_key = f'viewed_post_{post_id}'
    if not session.get(viewed_key):
        post.view_count = (post.view_count or 0) + 1
        session[viewed_key] = True
        db.session.commit()

    is_liked = g.user in post.liker
    is_bookmarked = Bookmark.query.filter_by(user_id=g.user.id, post_id=post_id).first() is not None

    prev_post = (
        Post.query.filter(Post.create_date > post.create_date)
        .order_by(Post.create_date.asc())
        .first()
    )
    next_post = (
        Post.query.filter(Post.create_date < post.create_date)
        .order_by(Post.create_date.desc())
        .first()
    )

    post_list = build_post_query(category=category, kw=kw, so=so).paginate(page=page, per_page=10)
    weekly_trends = get_weekly_trends()
    back_url = url_for('post._list', username_id=g.user.id, category=category, kw=kw, so=so, page=page)
    return render_template(
        'post_detail.html',
        post=post,
        comment_form=comment_form,
        user=g.user,
        post_list=post_list,
        page=page,
        kw=kw,
        so=so,
        category=category,
        is_my_posts=False,
        categories=CATEGORIES,
        weekly_trends=weekly_trends,
        back_url=back_url,
        is_liked=is_liked,
        is_bookmarked=is_bookmarked,
        prev_post=prev_post,
        next_post=next_post,
    )


@bp.route('/media/<path:filename>')
@login_required
def media(filename):
    safe_dir = os.path.normpath(os.path.join(current_app.root_path, os.path.dirname(filename)))
    root_dir = os.path.normpath(current_app.root_path)
    if not safe_dir.startswith(root_dir):
        flash('잘못된 이미지 경로입니다.', 'danger')
        return redirect(url_for('post._list', username_id=g.user.id))
    return send_from_directory(safe_dir, os.path.basename(filename))


@bp.route('/detail/<int:post_id>/upload/', methods=('POST',))
@login_required
def upload_images(post_id):
    post = Post.query.get_or_404(post_id)
    form = ImageUploadForm()
    if g.user != post.user:
        flash('본인 게시글만 이미지를 추가할 수 있습니다.', 'danger')
        return redirect(url_for('post.detail', post_id=post_id))

    if not form.validate_on_submit():
        flash('이미지 업로드 요청이 올바르지 않습니다.', 'danger')
        return redirect(url_for('post.detail', post_id=post_id))

    image_files = form.image.data
    new_paths = []
    today = datetime.now().strftime('%Y%m%d')
    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'posts', today)
    os.makedirs(upload_folder, exist_ok=True)

    for image_file in image_files:
        if image_file and image_file.filename:
            ext = os.path.splitext(image_file.filename)[1]
            filename = f'{uuid.uuid4()}{ext}'
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)
            new_paths.append(f'images/posts/{today}/{filename}')

    if new_paths:
        existing = [p.strip() for p in (post.image_path or '').split(',') if p.strip()]
        post.image_path = ','.join(existing + new_paths)
        db.session.commit()
        flash('이미지가 업로드되었습니다.', 'success')
    else:
        flash('업로드할 이미지를 선택해주세요.', 'warning')

    return redirect(url_for('post.detail', post_id=post_id))


@bp.route('/modify/<int:post_id>/', methods=('GET', 'POST'))
@login_required
def modify(post_id):
    post = Post.query.get_or_404(post_id)
    if g.user != post.user and g.user.role != 'admin':
        flash('수정권한이 없습니다', 'danger')
        return redirect(url_for('post.detail', post_id=post_id))

    form = PostForm(obj=post)
    if request.method == 'POST' and form.validate_on_submit():
        post.content = form.content.data
        post.category = detect_category(form.content.data)
        post.modify_date = datetime.now()
        if form.image.data:
            saved = _save_post_images(form.image.data)
            if saved:
                post.image_path = saved
        db.session.commit()
        flash('게시글이 수정되었습니다.', 'success')
        return redirect(url_for('post.detail', post_id=post_id))

    weekly_trends = get_weekly_trends()
    return render_template(
        'edit.html',
        form=form,
        post=post,
        user=g.user,
        categories=CATEGORIES,
        weekly_trends=weekly_trends,
    )


@bp.route('/delete/<int:post_id>/')
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if g.user != post.user and g.user.role != 'admin':
        flash('삭제 권한이 없습니다', 'danger')
        return redirect(url_for('post.detail', post_id=post_id))
    db.session.delete(post)
    db.session.commit()
    flash('게시글이 삭제되었습니다.', 'success')
    return redirect(url_for('post._list', username_id=g.user.id))


@bp.route('/like/<int:post_id>/')
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    source = request.args.get('source', 'detail')
    list_url = url_for('post._list', username_id=g.user.id)
    detail_url = url_for('post.detail', post_id=post_id)

    if g.user == post.user:
        flash('본인이 작성한 글은 추천할 수 없습니다', 'warning')
        return redirect(detail_url if source == 'detail' else (request.referrer or list_url))

    if g.user in post.liker:
        post.liker.remove(g.user)
        db.session.commit()
        flash('추천을 취소했습니다.', 'info')
    else:
        post.liker.append(g.user)
        create_notification(
            user_id=post.user_id,
            actor_id=g.user.id,
            ntype='like',
            message=f'{g.user.nickname}님이 회원님의 글을 좋아합니다.',
            post_id=post.id,
        )
        db.session.commit()
        flash('추천했습니다.', 'success')

    if source == 'list':
        return redirect(request.referrer or list_url)
    return redirect(detail_url)
