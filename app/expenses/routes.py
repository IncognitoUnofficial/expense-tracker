import csv
import io

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.expenses.forms import ExpenseForm
from app.extensions import db
from app.models import Category, Expense
from app.utils import month_bounds

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


def _get_owned_expense(expense_id):
    expense = db.session.get(Expense, expense_id)
    if expense is None or expense.user_id != current_user.id:
        abort(404)
    return expense


def _user_categories():
    return db.session.execute(
        db.select(Category).filter_by(user_id=current_user.id).order_by(Category.name)
    ).scalars().all()


def _parse_month(month_str):
    """Parse a 'YYYY-MM' string into (start_date, end_date_exclusive), or None if invalid."""
    if not month_str:
        return None
    try:
        year, month = (int(part) for part in month_str.split("-"))
    except (ValueError, TypeError):
        return None
    if not 1 <= month <= 12:
        return None
    return month_bounds(year, month)


def _filtered_expenses_query():
    """Build the expenses select for the current user, applying the
    category/month/q query-string filters shared by the list view and the
    CSV export."""
    category_id = request.args.get("category", type=int)
    month_str = request.args.get("month", "")
    search = request.args.get("q", "").strip()

    query = db.select(Expense).filter_by(user_id=current_user.id)

    if category_id:
        query = query.filter(Expense.category_id == category_id)

    month_range = _parse_month(month_str)
    if month_range:
        start, end = month_range
        query = query.filter(Expense.expense_date >= start, Expense.expense_date < end)

    if search:
        query = query.filter(Expense.description.ilike(f"%{search}%"))

    return query.order_by(Expense.expense_date.desc(), Expense.id.desc())


@expenses_bp.route("/", methods=["GET"])
@login_required
def list_expenses():
    page = request.args.get("page", 1, type=int)
    pagination = db.paginate(_filtered_expenses_query(), page=page, per_page=20, error_out=False)

    return render_template(
        "expenses/list.html",
        pagination=pagination,
        expenses=pagination.items,
        categories=_user_categories(),
        selected_category=request.args.get("category", type=int),
        selected_month=request.args.get("month", ""),
        search=request.args.get("q", "").strip(),
    )


@expenses_bp.route("/export", methods=["GET"])
@login_required
def export_expenses():
    expenses = db.session.execute(_filtered_expenses_query()).scalars().all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Date", "Category", "Description", "Amount"])
    for expense in expenses:
        writer.writerow([
            expense.expense_date.isoformat(),
            expense.category.name,
            expense.description or "",
            f"{expense.amount:.2f}",
        ])

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )


@expenses_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_expense():
    form = ExpenseForm()
    categories = _user_categories()
    form.set_category_choices(categories)

    if not categories:
        flash("Create a category before adding an expense.", "error")
        return redirect(url_for("categories.list_categories"))

    if form.validate_on_submit():
        expense = Expense(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            description=form.description.data.strip() if form.description.data else None,
            expense_date=form.expense_date.data,
        )
        db.session.add(expense)
        db.session.commit()
        flash("Expense added.", "success")
        return redirect(url_for("expenses.list_expenses"))

    return render_template("expenses/form.html", form=form, mode="new")


@expenses_bp.route("/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = _get_owned_expense(expense_id)
    form = ExpenseForm(obj=expense)
    form.set_category_choices(_user_categories())

    if form.validate_on_submit():
        expense.category_id = form.category_id.data
        expense.amount = form.amount.data
        expense.description = form.description.data.strip() if form.description.data else None
        expense.expense_date = form.expense_date.data
        db.session.commit()
        flash("Expense updated.", "success")
        return redirect(url_for("expenses.list_expenses"))

    if request.method == "GET":
        form.category_id.data = expense.category_id

    return render_template("expenses/form.html", form=form, mode="edit", expense=expense)


@expenses_bp.route("/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = _get_owned_expense(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses.list_expenses"))
