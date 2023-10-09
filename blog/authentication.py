from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse

authentication = Blueprint("authentication", __name__)


@authentication.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('controllers.home'))
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in", category='success')
                login_user(user, remember=True)

                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('controllers.home')
                return redirect(next_page)
            else:
                flash('Either Email or Password is incorrect', category='error')
        else:
            flash('Email does not exist', category='error')
        
    return render_template("login.html", user=current_user)


@authentication.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")


        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email already in use', category='error')
        elif username_exists:
            flash('Username already in use', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        elif len(username) < 2:
            flash('Username is too short', category='error')
        elif len(password1) < 8:
            flash('Password is too short', category='error')
        elif len(email) < 4:
            flash("Email is invalid", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Profile created Successfully')
            return redirect(url_for('authentication.login'))
    return render_template("signup.html", user=current_user)


@authentication.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("authentication.login"))
