from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app.account.forms import ChangePasswordForm, ProfileForm
from app.extensions import db
from app.models import User

account_bp = Blueprint("account", __name__, url_prefix="/account")


@account_bp.route("/", methods=["GET"])
@login_required
def settings():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    return render_template(
        "account/settings.html", profile_form=profile_form, password_form=password_form
    )


@account_bp.route("/profile", methods=["POST"])
@login_required
def update_profile():
    profile_form = ProfileForm()
    if profile_form.validate_on_submit():
        email = profile_form.email.data.lower()
        existing = db.session.execute(
            db.select(User).filter(User.email == email, User.id != current_user.id)
        ).scalar_one_or_none()

        if existing is not None:
            flash("Another account already uses that email.", "error")
        else:
            current_user.name = profile_form.name.data.strip()
            current_user.email = email
            db.session.commit()
            flash("Profile updated.", "success")
    else:
        flash("Please provide a valid name and email.", "error")

    return redirect(url_for("account.settings"))


@account_bp.route("/password", methods=["POST"])
@login_required
def change_password():
    password_form = ChangePasswordForm()
    if password_form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, password_form.current_password.data):
            flash("Current password is incorrect.", "error")
        else:
            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash("Password changed.", "success")
    else:
        flash("Please correct the errors in the password form.", "error")

    return redirect(url_for("account.settings"))
