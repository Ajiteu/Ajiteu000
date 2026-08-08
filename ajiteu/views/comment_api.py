from ajiteu import db
from ajiteu.models import Post, Comment
from ajiteu.forms import CommentForm
from ajiteu.notification_service import create_notification
from datetime import datetime
from flask import Blueprint, url_for, request, redirect, render_template, g, flash, current_app
from ajiteu.views.auth_views import login_required
import os
import uuid

bp = Blueprint('comment', __name__, url_prefix='/comment')


def _save_comment_images(image_files):
    image_paths = []
    today = datetime.now().strftime('%Y%m%d')
    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'comments', today)
    os.makedirs(upload_folder, exist_ok=True)

    if image_files:
        for image_file in image_files:
            if image_file and image_file.filename:
                ext = os.path.splitext(image_file.filename)[1]
                filename = f'{uuid.uuid4()}{ext}'
                file_path = os.path.join(upload_folder, filename)
                image_file.save(file_path)
                image_paths.append(f'images/comments/{today}/{filename}')
    return ','.join(image_paths) if image_paths else None


@bp.route('/create/<int:post_id>/', methods=('POST',))
@login_required
def create(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            image_path=_save_comment_images(form.image.data),
            create_date=datetime.now(),
            user=g.user,
            post_id=post_id,
        )
        db.session.add(comment)
        db.session.flush()
        create_notification(
            user_id=post.user_id,
            actor_id=g.user.id,
            ntype='comment',
            message=f'{g.user.nickname}님이 회원님의 글에 댓글을 남겼습니다.',
            post_id=post.id,
            comment_id=comment.id,
        )
        db.session.commit()
        flash('댓글이 등록되었습니다.', 'success')
        return redirect(url_for('post.detail', post_id=post_id))

    flash('댓글 내용을 입력해주세요.', 'danger')
    return redirect(url_for('post.detail', post_id=post_id))


@bp.route('/modify/<int:comment_id>/', methods=('GET', 'POST'))
@login_required
def modify(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if g.user != comment.user:
        flash('수정권한이 없습니다', 'danger')
        return redirect(url_for('post.detail', post_id=comment.post.id))

    form = CommentForm(obj=comment)
    if request.method == 'POST' and form.validate_on_submit():
        comment.content = form.content.data
        comment.modify_date = datetime.now()
        db.session.commit()
        flash('댓글이 수정되었습니다.', 'success')
        return redirect(url_for('post.detail', post_id=comment.post.id))

    return render_template('comment_edit.html', comment=comment, form=form)


@bp.route('/delete/<int:comment_id>/')
@login_required
def delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    if g.user != comment.user and g.user.role != 'admin':
        flash('삭제권한이 없습니다', 'danger')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('댓글이 삭제되었습니다.', 'success')
    return redirect(url_for('post.detail', post_id=post_id))
