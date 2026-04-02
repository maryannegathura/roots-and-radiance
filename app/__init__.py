import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from config import config
from app.chat import api_bp
from app.admin import admin_bp

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
cors = CORS()

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='.', template_folder='templates')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    mail.init_app(app)

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return app.send_static_file('Home page.html')  # Default to home, or directory index

    return app

