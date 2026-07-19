from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.categories.forms import CategoryForm
from app.extensions import db
from app.models import Category, Expense
from app.utils import month_bounds
from datetime import date

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


def _get_owned_category(category_id):
    category = db.session.get(Category, category_id)
    if category is None or category.user_id != current_user.id:
        abort(404)
    return category


def _spent_this_month_by_category():
    today = date.today()
    start, end = month_bounds(today.year, today.month)
    rows = db.session.execute(
        db.select(Expense.category_id, func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= start,
            Expense.expense_date < end,
        )
        .group_by(Expense.category_id)
    ).all()
    return {category_id: total for category_id, total in rows}


@categories_bp.route("/", methods=["GET"])
@login_required
def list_categories():
    categories = db.session.execute(
        db.select(Category)
        .filter_by(user_id=current_user.id)
        .order_by(Category.name)
    ).scalars().all()
    form = CategoryForm()
    return render_template(
        "categories/list.html",
        categories=categories,
        form=form,
        spent_this_month=_spent_this_month_by_category(),
    )


@categories_bp.route("/", methods=["POST"])
@login_required
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            user_id=current_user.id,
            name=form.name.data.strip(),
            monthly_budget=form.monthly_budget.data,
        )
        db.session.add(category)
        try:
            db.session.commit()
            flash(f'Category "{category.name}" created.', "success")
        except IntegrityError:
            db.session.rollback()
            flash(f'You already have a category named "{form.name.data.strip()}".', "error")
    else:
        flash("Please provide a valid category name and budget.", "error")

    return redirect(url_for("categories.list_categories"))


@categories_bp.route("/<int:category_id>/edit", methods=["POST"])
@login_required
def edit_category(category_id):
    category = _get_owned_category(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.monthly_budget = form.monthly_budget.data
        try:
            db.session.commit()
            flash("Category updated.", "success")
        except IntegrityError:
            db.session.rollback()
            flash(f'You already have a category named "{form.name.data.strip()}".', "error")
    else:
        flash("Please provide a valid category name and budget.", "error")

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
