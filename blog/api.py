from flask_restful import Resource
from .models import Post, User, Comment, Like, Caption
from . import db
from flask import request
from werkzeug.security import generate_password_hash


class UserAPI(Resource):
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user:
            return {
                "username": user.username,
                "email": user.email,
                "post_count": user.posts.count(),
                "follower_count": user.followers.count(),
                "followed_count": user.followed.count(),
            }
        else:
            return {}, 404

    def put(self, username):
        data = request.get_json()
        user = User.query.filter_by(username=username).first()
        if data["email"] == user.email:
            user.email = data["email"]
            db.session.commit()
            return {"email": "email_updated"}
        else:
            return {"email": "no_change"}, 400

    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data["username"]).first()
        if user:
            return {"user": "already exists"}
        else:
            data = request.get_json()
            new_user = User(
                email=data["email"],
                username=data["username"],
                password=generate_password_hash(data["password1"], method="sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            return {"user": "created"}

    def delete(self, username):
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return {"deleted": "successfully"}
        else:
            return {}, 404


class BlogAPI(Resource):
    def get(self, id):
        post = Post.query.filter_by(id=id).first()
        if post:
            user = User.query.filter_by(id=post.author_id).first()
            return {"post_text": post.text, "post_author": user.username}
        else:
            return {"post": "does not exist"}

    def delete(self, id):
        post = Post.query.filter_by(id=id).first()
        if not post:
            return {"post": "does not exist"}
        else:
            db.session.delete(post)
            db.session.commit()
            return {"post": "deleted"}

    def post(self, id):
        data = request.get_json()
        user = User.query.filter_by(id=id).first()
        if user:
            new_post = Post(text=data["text"], author_id=id)
            db.session.add(new_post)
            db.session.commit()

        if data["captions"]:
            post_id = (Post.query.filter_by(author_id=id).first()).id
            caption = Caption(captions=data["captions"], post_id=post_id)
            db.session.add(caption)
            db.session.commit()

        return {"post": "created"}

    def put(self, id):
        data = request.get_json()
        post = Post.query.filter_by(id=id).first()
        if not post:
            return {"post": "does not exist"}
        elif not data["text"]:
            return {"post": "cannot be empty"}
        elif not data["caption"]:
            captions = Caption.query.filter_by(post_id=id).first()
            db.session.delete(captions)
            db.session.commit()
        elif post.text != data["text"]:
            post.text = data["text"]
            db.session.commit()
        elif post.captions != data["captions"]:
            post.captions = data["captions"]
            db.session.commit()
        elif not post.captions:
            caption_new = Caption(captions=data["captions"], post_id=post.id)
            db.session.add(caption_new)
            db.session.commit()
        return {"post": "updated"}
