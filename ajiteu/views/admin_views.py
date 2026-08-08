from datetime import datetime

from flask import Blueprint, redirect, url_for, flash, g, render_template, request

from ajiteu import db
from ajiteu.models import Report, Post, User
from ajiteu.views.auth_views import login_required, admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@admin_required
def dashboard():
    reports = Report.query.filter_by(status='pending').order_by(Report.create_date.desc()).all()
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin.html', reports=reports, users=users)


@bp.route('/report/', methods=('POST',))
@login_required
def create_report():
    post_id = request.form.get('post_id', type=int)
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('신고 사유를 입력해주세요.', 'danger')
        return redirect(request.referrer or url_for('post._list', username_id=g.user.id))

    report = Report(
        reporter_id=g.user.id,
        post_id=post_id,
        reason=reason,
        status='pending',
        create_date=datetime.now(),
    )
    db.session.add(report)
    db.session.commit()
    flash('신고가 접수되었습니다.', 'success')
    return redirect(request.referrer or url_for('post._list', username_id=g.user.id))


@bp.route('/report/<int:report_id>/resolve/')
@admin_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = 'resolved'
    db.session.commit()
    flash('신고를 처리했습니다.', 'success')
    return redirect(url_for('admin.dashboard'))


@bp.route('/post/delete/<int:post_id>/')
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('게시글을 삭제했습니다.', 'success')
    return redirect(url_for('admin.dashboard'))


@bp.route('/user/deactivate/<int:user_id>/')
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == g.user.id:
        flash('본인 계정은 비활성화할 수 없습니다.', 'danger')
        return redirect(url_for('admin.dashboard'))
    user.is_active = False
    db.session.commit()
    flash('회원을 비활성화했습니다.', 'success')
    return redirect(url_for('admin.dashboard'))


@bp.route('/user/activate/<int:user_id>/')
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash('회원을 활성화했습니다.', 'success')
    return redirect(url_for('admin.dashboard'))
