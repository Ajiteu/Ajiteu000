from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from ajiteu import db
from ajiteu.forms import UserCreateForm, UserLoginForm
from ajiteu.models import User
from ajiteu.jwt_utils import create_access_token, jwt_required_api
import functools


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        email_user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('이미 존재하는 사용자입니다.', 'danger')
        elif email_user:
            flash('이미 사용 중인 이메일입니다.', 'danger')
        else:
            user = User(
                username=form.username.data,
                password=generate_password_hash(form.password1.data),
                email=form.email.data,
                nickname=form.username.data,
                image_path='images/default.png',
            )
            db.session.add(user)
            db.session.commit()
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('post._list', username_id=user.id))
    return render_template('auth/signup.html', form=form)


@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = '존재하지 않는 사용자입니다.'
        elif not user.is_active:
            error = '비활성화된 계정입니다.'
        elif not check_password_hash(user.password, form.password.data):
            error = '비밀번호가 올바르지 않습니다'
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('post._list', username_id=user.id))
        flash(error, 'danger')
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not username or not email or not password:
        return jsonify({'error': 'username, email, password가 필요합니다.'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '이미 존재하는 사용자입니다.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '이미 사용 중인 이메일입니다.'}), 400

    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        nickname=username,
        image_path='images/default.png',
    )
    db.session.add(user)
    db.session.commit()
    token = create_access_token(user.id)
    return jsonify({'access_token': token, 'user_id': user.id, 'username': user.username}), 201


@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    user = User.query.filter_by(username=username).first()
    if not user or not user.is_active:
        return jsonify({'error': '존재하지 않거나 비활성화된 사용자입니다.'}), 401
    if not check_password_hash(user.password, password):
        return jsonify({'error': '비밀번호가 올바르지 않습니다.'}), 401

    token = create_access_token(user.id)
    return jsonify({'access_token': token, 'user_id': user.id, 'username': user.username})


@bp.route('/api/me')
@jwt_required_api
def api_me():
    return jsonify({
        'id': g.user.id,
        'username': g.user.username,
        'nickname': g.user.nickname,
        'email': g.user.email,
        'role': g.user.role,
    })


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if not g.user.is_active:
            flash('비활성화된 계정입니다.', 'danger')
            return redirect(url_for('auth.logout'))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if g.user.role != 'admin':
            flash('관리자 권한이 필요합니다.', 'danger')
            return redirect(url_for('post._list', username_id=g.user.id))
        return view(*args, **kwargs)
    return wrapped_view
