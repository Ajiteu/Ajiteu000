import functools
from datetime import datetime, timedelta

import jwt
from flask import current_app, g, jsonify, request

from ajiteu.models import User


def create_access_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config.get('JWT_EXPIRE_HOURS', 24)),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])


def jwt_required_api(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': '인증 토큰이 필요합니다.'}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = decode_access_token(token)
            user = User.query.get(payload.get('user_id'))
            if user is None or not user.is_active:
                return jsonify({'error': '유효하지 않은 사용자입니다.'}), 401
            g.user = user
        except jwt.PyJWTError:
            return jsonify({'error': '유효하지 않은 토큰입니다.'}), 401

        return view(*args, **kwargs)

    return wrapped_view
