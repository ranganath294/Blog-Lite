from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like, Caption
from . import db

controllers = Blueprint("controllers", __name__)


@controllers.route("/")
@controllers.route("/home")
@login_required
def home():
    # posts = Post.query.all()
    posts = current_user.followed_posts()
    return render_template("home.html", user=current_user, posts=posts)


@controllers.route("/explore")
@login_required
def explore():
    posts = current_user.explore_posts()
    return render_template("explore.html", user=current_user, posts=posts)


@controllers.route("/edit-user/<id>", methods=["GET", "POST"])
@login_required
def edit(id):
    if request.method == "POST":
        user = User.query.filter_by(id=id).first()
        email = request.form.get("email")
        username = request.form.get("username")
        if not user:
            flash("User does not exist", category="error")
        elif current_user.id != user.id:
            flash("You do not have permission to edit this user", category="error")
        elif (not username) or (not email):
            flash("Username and Email cannot be empty", category="error")
            return redirect(
                url_for("controllers.user_info", username=current_user.username)
            )
        elif username != user.username:
            user.username = username
            db.session.commit()
        elif email != user.email:
            user.email = email
            db.session.commit()

        return redirect(
            url_for("controllers.user_info", username=current_user.username)
        )

    return render_template("edit_user.html", user=current_user)


@controllers.route("/delete-my-account/<id>")
@login_required
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        flash("User does not exist", category="error")
    elif current_user.id != user.id:
        flash("You do not have permission to delete this user", category="error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("Your account is deleted", category="success")

    return redirect(url_for("authentication.sign_up"))


@controllers.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get("text")
        captions = request.form.get("captions")
        if not text:
            flash("Post cannot be empty", category="error")
        else:
            post = Post(text=text, author_id=current_user.id)
            db.session.add(post)
            db.session.commit()

            if captions:
                post_id = (Post.query.filter_by(author_id=current_user.id).first()).id
                caption = Caption(captions=captions, post_id=post_id)
                db.session.add(caption)
                db.session.commit()

            flash("Post created", category="success")
            return redirect(url_for("controllers.home"))

    return render_template("create_post.html", user=current_user)


@controllers.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash("Post does not exist", category="error")
    elif current_user.id != post.author_id:
        flash("You do not have permission to delete this post", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted", category="success")

    return redirect(url_for("controllers.home"))


@controllers.route("/edit-post/<id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()
    if request.method == "POST":
        text = request.form.get("text")
        caption = request.form.get("captions")
        if not text:
            flash("Post cannot be empty", category="error")
            return redirect(url_for("controllers.home"))
        elif not caption:
            captions = Caption.query.filter_by(post_id=post.id).first()
            db.session.delete(captions)
            db.session.commit()
            flash("caption deleted", category="success")
            return redirect(
                url_for("controllers.user_info", username=current_user.username)
            )
        elif post.captions:
            if post.text == text and (post.captions[0]).captions == caption:
                return redirect(
                    url_for("controllers.user_info", username=current_user.username)
                )
        elif post.text != text:
            post.text = text
            db.session.commit()
            flash("Post updated", category="success")
        elif post.captions:
            if (post.captions[0]).captions != caption:
                (post.captions[0]).captions = caption
                db.session.commit()
                flash("caption updated", category="success")
        elif not post.captions:
            caption_new = Caption(captions=caption, post_id=post.id)
            db.session.add(caption_new)
            db.session.commit()
            flash("caption updated", category="success")

        return redirect(
            url_for("controllers.user_info", username=current_user.username)
        )

    if not post:
        flash("Post does not exist", category="error")
    elif current_user.id != post.author_id:
        flash("You do not have permission to edit this post", category="error")
    else:
        if post.captions:
            return render_template(
                "edit-post.html",
                post=post,
                user=current_user,
                captions=post.captions[0],
            )
        else:
            return render_template(
                "edit-post.html", post=post, user=current_user, captions=post.captions
            )


@controllers.route("/<username>/profile")
@login_required
def user_info(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("No user with that username exists", category="error")
        return redirect(url_for("controllers.home"))

    # posts = user.posts
    own_posts = user.own_posts()
    own_posts_length = own_posts.count()

    followers = user.followers.all()

    followings = user.followed.all()

    return render_template(
        "user_info.html",
        user=user,
        posts=own_posts,
        own_posts_length=own_posts_length,
        username=username,
        followers=followers,
        followings=followings,
    )


@controllers.route("/create-comment/<post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    comment = request.form.get("comment")

    if not comment:
        flash("Comment cannot be empty", category="error")
    else:
        post = Post.query.filter_by(id=post_id).first()
        if post:
            comment_1 = Comment(
                comment=comment, author_id=current_user.id, post_id=post_id
            )
            db.session.add(comment_1)
            db.session.commit()
        else:
            flash("Post does not exist", category="error")

    return redirect(url_for("controllers.home"))


@controllers.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash("Comment does not exist", category="error")
    elif (
        current_user.id != comment.author_id
        or current_user.id != comment.post.author_id
    ):
        flash("You do not have permission to delete this comment", category="error")
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for("controllers.home"))


@controllers.route("/edit-comment/<comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    post = comment.post

    if request.method == "POST":
        text = request.form.get("text")
        if not text:
            flash("Comment cannot be empty", category="error")
            return redirect(url_for("controllers.home"))
        elif comment.comment == text:
            return redirect(url_for("controllers.home"))
        else:
            comment.comment = text
            db.session.commit()
            flash("Comment updated", category="success")
            return redirect(url_for("controllers.home"))

    if not comment:
        flash("Comment does not exist", category="error")
    elif current_user.id != comment.author_id:
        flash("You do not have permission to edit this comment", category="error")
    else:
        return render_template(
            "edit_comment.html", comment=comment, user=current_user, post=post
        )


@controllers.route("/like-post/<post_id>", methods=["GET", "POST"])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author_id=current_user.id, post_id=post_id).first()
    if not post:
        flash("Post does not exist", category="error")
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for("controllers.home"))


@controllers.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("No user with that username", category="error")
        return redirect(url_for("controllers.home"))
    if user == current_user:
        flash("You can't follow yourself")
        return redirect(url_for("controllers.user_info", username=username))
    current_user.follow(user)
    db.session.commit()
    flash("You followed" + username)
    return redirect(url_for("controllers.user_info", username=username))


@controllers.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("No user with that username", category="error")
        return redirect(url_for("controllers.home"))
    if user == current_user:
        flash("You can't follow yourself")
        return redirect(url_for("controllers.user_info", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash("You unfollowed " + username)
    return redirect(url_for("controllers.user_info", username=username))


@controllers.route("/search", methods=["GET", "POST"])
@login_required
def followers():
    if request.method == "POST":
        search_text = request.form.get("search_text")
        if search_text:
            user = User.query.filter(User.username.contains(search_text)).all()
            return render_template("search.html", users=user, searched_text=search_text)
        return render_template("search.html")
    return render_template("search.html")
