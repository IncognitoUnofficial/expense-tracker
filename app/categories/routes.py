from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.categories.forms import CategoryForm
from app.extensions import db
from app.models import Category

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


def _get_owned_category(category_id):
    category = db.session.get(Category, category_id)
    if category is None or category.user_id != current_user.id:
        abort(404)
    return category


@categories_bp.route("/", methods=["GET"])
@login_required
def list_categories():
    categories = db.session.execute(
        db.select(Category)
        .filter_by(user_id=current_user.id)
        .order_by(Category.name)
    ).scalars().all()
    form = CategoryForm()
    return render_template("categories/list.html", categories=categories, form=form)


@categories_bp.route("/", methods=["POST"])
@login_required
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(user_id=current_user.id, name=form.name.data.strip())
        db.session.add(category)
        try:
            db.session.commit()
            flash(f'Category "{category.name}" created.', "success")
        except IntegrityError:
            db.session.rollback()
            flash(f'You already have a category named "{form.name.data.strip()}".', "error")
    else:
        flash("Please provide a valid category name.", "error")

    return redirect(url_for("categories.list_categories"))


@categories_bp.route("/<int:category_id>/edit", methods=["POST"])
@login_required
def edit_category(category_id):
    category = _get_owned_category(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        try:
            db.session.commit()
            flash("Category updated.", "success")
        except IntegrityError:
            db.session.rollback()
            flash(f'You already have a category named "{form.name.data.strip()}".', "error")
    else:
        flash("Please provide a valid category name.", "error")

    return redirect(url_for("categories.list_categories"))


@categories_bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    category = _get_owned_category(category_id)

    if category.expense_count > 0:
        flash(
            f'"{category.name}" has {category.expense_count} expense(s) linked to it. '
            "Reassign or delete those expenses before deleting this category.",
            "error",
        )
        return redirect(url_for("categories.list_categories"))

    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" deleted.', "success")
    return redirect(url_for("categories.list_categories"))
