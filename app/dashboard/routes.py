from datetime import date

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models import Category, Expense
from app.utils import MONTH_NAMES, month_bounds, shift_month

dashboard_bp = Blueprint("dashboard", __name__)


def _month_total(user_id, start, end):
    return db.session.execute(
        db.select(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.user_id == user_id,
            Expense.expense_date >= start,
            Expense.expense_date < end,
        )
    ).scalar_one()


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    month_str = request.args.get("month", "")
    try:
        year, month = (int(part) for part in month_str.split("-"))
        date(year, month, 1)
    except (ValueError, TypeError):
        today = date.today()
        year, month = today.year, today.month

    start, end = month_bounds(year, month)
    selected_month_label = f"{MONTH_NAMES[month - 1]} {year}"
    selected_month_value = f"{year:04d}-{month:02d}"

    month_total = _month_total(current_user.id, start, end)

    prev_year, prev_month = shift_month(year, month, -1)
    prev_start, prev_end = month_bounds(prev_year, prev_month)
    prev_month_total = _month_total(current_user.id, prev_start, prev_end)

    if prev_month_total:
        month_over_month_percent = round(
            (float(month_total) - float(prev_month_total)) / float(prev_month_total) * 100
        )
    else:
        month_over_month_percent = None

    by_category_rows = db.session.execute(
        db.select(Category.id, Category.name, Category.monthly_budget, func.coalesce(func.sum(Expense.amount), 0))
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= start,
            Expense.expense_date < end,
        )
        .group_by(Category.id, Category.name, Category.monthly_budget)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    by_category = [
        {
            "name": name,
            "total": total,
            "percent": float(total) / float(month_total) * 100 if month_total else 0,
            "budget": budget,
            "budget_percent": float(total) / float(budget) * 100 if budget else None,
        }
        for _id, name, budget, total in by_category_rows
    ]

    trend_start_year, trend_start_month = shift_month(year, month, -5)
    trend_start, _ = month_bounds(trend_start_year, trend_start_month)

    trend_rows = dict(
        db.session.execute(
            db.select(
                func.date_format(Expense.expense_date, "%Y-%m"),
                func.coalesce(func.sum(Expense.amount), 0),
            )
            .filter(
                Expense.user_id == current_user.id,
                Expense.expense_date >= trend_start,
                Expense.expense_date < end,
            )
            .group_by(func.date_format(Expense.expense_date, "%Y-%m"))
        ).all()
    )

    trend = []
    for delta in range(-5, 1):
        trend_year, trend_month = shift_month(year, month, delta)
        key = f"{trend_year:04d}-{trend_month:02d}"
        trend.append(
            {
                "label": f"{MONTH_NAMES[trend_month - 1][:3]} {trend_year}",
                "total": trend_rows.get(key, 0),
            }
        )

    recent_expenses = db.session.execute(
        db.select(Expense)
        .filter_by(user_id=current_user.id)
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .limit(8)
    ).scalars().all()

    next_year, next_month = shift_month(year, month, 1)

    return render_template(
        "dashboard/index.html",
        month_total=month_total,
        month_over_month_percent=month_over_month_percent,
        by_category=by_category,
        trend=trend,
        category_chart_totals=[float(row["total"]) for row in by_category],
        trend_chart_totals=[float(row["total"]) for row in trend],
        recent_expenses=recent_expenses,
        selected_month_label=selected_month_label,
        selected_month_value=selected_month_value,
        prev_month_value=f"{prev_year:04d}-{prev_month:02d}",
        next_month_value=f"{next_year:04d}-{next_month:02d}",
        has_expenses=db.session.execute(
            db.select(Expense.id).filter_by(user_id=current_user.id).limit(1)
        ).first()
        is not None,
    )
