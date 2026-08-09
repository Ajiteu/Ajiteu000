from ajiteu import db
from ajiteu.models import User, Post
from ajiteu.forms import ProfileForm
from flask import Blueprint, render_template, url_for, redirect, g, flash, current_app
from datetime import datetime
import os
import uuid
from ajiteu.views.auth_views import login_required
from ajiteu.views.posts_views import CATEGORIES
from ajiteu.views.trend_views import get_weekly_trends


bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/view/<int:username_id>/')
@login_required
def view(username_id):
    user = User.query.get_or_404(username_id)
    is_me = g.user.id == username_id
    post_count = Post.query.filter_by(user_id=username_id).count()

    return render_template(
        'profile_view.html',
        profile_user=user,
        is_me=is_me,
        post_count=post_count,
        user=g.user,
        categories=CATEGORIES,
        weekly_trends=get_weekly_trends(),
    )


@bp.route('/detail/<int:username_id>/', methods=('GET', 'POST'))
@login_required
def detail(username_id):
    if g.user.id != username_id:
        return redirect(url_for('profile.view', username_id=username_id))

    user = User.query.get_or_404(username_id)
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.nickname = form.nickname.data
        user.user_intro = form.user_intro.data

        image_file = form.image.data
        if image_file:
            today = datetime.now().strftime('%Y%m%d')
            upload_folder = os.path.join(current_app.root_path, 'static/images', today)
            os.makedirs(upload_folder, exist_ok=True)
            ext = os.path.splitext(image_file.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)
            user.image_path = f'images/{today}/{filename}'

        db.session.commit()
        flash('프로필이 저장되었습니다.', 'success')
        return redirect(url_for('post._list', username_id=user.id))

    weekly_trends = get_weekly_trends()
    return render_template(
        'profile.html',
        user=user,
        form=form,
        categories=CATEGORIES,
        weekly_trends=weekly_trends,
    )
