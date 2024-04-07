from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def handle_bad_request(e):
    return render_template('error.html', e=e), 400

def handle_unauthorized(e):
    return render_template('error.html', e=e), 401

def handle_not_found(e):
    return render_template('error.html', e=e), 404

def handle_internal_server_error(e):
    return render_template('error.html', e=e), 500

def create_app():
    app = Flask(__name__)

    # ログ設定
    log_handler = logging.FileHandler('server.log')
    log_handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(log_handler)
    werkzeug = logging.getLogger('werkzeug')
    werkzeug.setLevel(logging.DEBUG)
    werkzeug.addHandler(log_handler)

    # ここでは公式ドキュメントにもある secret_key をそのまま使って公開していますが、
    # 実際の運用では secret_key は公開しないでください
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    if os.environ['FLASK_ENV'] == 'development':
        app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:postgres@postgres/development'
    else:
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:postgres@postgres/test'

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    app.register_error_handler(400, handle_bad_request)
    app.register_error_handler(401, handle_unauthorized)
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(500, handle_internal_server_error)

    from . import views
    app.register_blueprint(views.bp)

    return app
