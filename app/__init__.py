from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # 注册自定义过滤器
    @app.template_filter('slice')
    def slice_filter(iterable, limit):
        return list(iterable)[:limit]

    @app.template_filter('datetime')
    def datetime_filter(value):
        if isinstance(value, str):
            return value
        try:
            return value.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(value)

    from app.routes import main, auth, devices
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(devices.bp)

    return app 