from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from ajiteu.filter import format_datetime, post_image_url
import config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    from . import models
    db.init_app(app)
    migrate.init_app(app, db)

    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['post_image_url'] = post_image_url

    from .views import (
        main_views, post_api, reply_api, comment_api, auth_views, profile,
        posts_views, my_posts_views, trend_views, bookmark_views,
        notification_views, admin_views,
    )
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(post_api.bp)
    app.register_blueprint(reply_api.bp)
    app.register_blueprint(comment_api.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(posts_views.bp)
    app.register_blueprint(my_posts_views.bp)
    app.register_blueprint(trend_views.bp)
    app.register_blueprint(bookmark_views.bp)
    app.register_blueprint(notification_views.bp)
    app.register_blueprint(admin_views.bp)

    return app
