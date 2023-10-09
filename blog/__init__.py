from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_restful import Resource, Api


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'

    db.init_app(app)
    api = Api(app)

    from .controllers import controllers
    from .authentication import authentication
    

    app.register_blueprint(authentication, url_prefix="/")
    app.register_blueprint(controllers, url_prefix="/")

    

    from .models import User, Post, Comment, Like, Caption

    create_database(app)

    

    login_manager = LoginManager()
    login_manager.login_view = "authentication.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app, api



def create_database(app):
    if not path.exists("blog/" + "database.sqlite3"):
        with app.app_context():
            db.create_all()