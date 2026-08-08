def format_datetime(value, fmt='%Y년 %m월 %d일 %H:%M'):
    return value.strftime(fmt)


def post_image_url(image_path: str) -> str:
    from flask import url_for

    path = (image_path or '').strip()
    if not path:
        return ''
    if path.startswith('images/') or path.startswith('photo/'):
        return url_for('static', filename=path)
    return url_for('post.media', filename=path)