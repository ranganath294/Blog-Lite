from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(200))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    posts = db.relationship(
        "Post", backref="user", cascade="all, delete", lazy="dynamic"
    )
    comments = db.relationship("Comment", backref="user", cascade="all, delete")
    likes = db.relationship("Like", backref="user", cascade="all, delete")

    # dp = db.relationship(
    #     "DisPic", backref="user", cascade="all, delete", lazy="dynamic"
    # )

    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
        # True if following, False if not following

    def followed_posts(self):
        followed_posts = Post.query.join(
            followers, (followers.c.followed_id == Post.author_id)
        ).filter(followers.c.follower_id == self.id)
        return followed_posts.order_by(Post.date_posted.desc())

    def own_posts(self):
        own_posts = Post.query.filter_by(author_id=self.id)
        return own_posts.order_by(Post.date_posted.desc())

    def explore_posts(self):
        posts = Post.query
        followed_posts = Post.query.join(
            followers, (followers.c.followed_id == Post.author_id)
        ).filter(followers.c.follower_id == self.id)
        own_posts = Post.query.filter_by(author_id=self.id)
        explore_posts = posts.except_(followed_posts.union(own_posts))
        return explore_posts.order_by(Post.date_posted.desc())


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    captions = db.relationship("Caption", backref="post", cascade="all, delete")
    comments = db.relationship("Comment", backref="post", cascade="all, delete")
    likes = db.relationship("Like", backref="post", cascade="all, delete")


class Caption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    captions = db.Column(db.Text, nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))


# class DisPic(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
