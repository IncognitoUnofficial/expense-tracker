from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models import Category, User

auth_bp = Blueprint("auth", __name__)

DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Housing",
    "Utilities",
    "Entertainment",
    "Health",
    "Other",
]


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = db.session.execute(
            db.select(User).filter_by(email=form.email.data.lower())
        ).scalar_one_or_none()
        if existing is not None:
            flash("An account with that email already exists.", "error")
            return render_template("auth/register.html", form=form)

        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower(),
            password_hash=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.flush()

        for category_name in DEFAULT_CATEGORIES:
            db.session.add(Category(user_id=user.id, name=category_name))

        db.session.commit()

        login_user(user)
        flash("Welcome! Your account has been created.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).filter_by(email=form.email.data.lower())
        ).scalar_one_or_none()

        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", form=form)

        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
