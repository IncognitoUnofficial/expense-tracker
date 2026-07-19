from datetime import date

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models import Category, Expense

dashboard_bp = Blueprint("dashboard", __name__)

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _month_bounds(year, month):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def _shift_month(year, month, delta):
    """Shift (year, month) by delta months (can be negative)."""
    index = (year * 12 + (month - 1)) + delta
    return index // 12, index % 12 + 1


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

    start, end = _month_bounds(year, month)
    selected_month_label = f"{MONTH_NAMES[month - 1]} {year}"
    selected_month_value = f"{year:04d}-{month:02d}"

    month_total = db.session.execute(
        db.select(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= start,
            Expense.expense_date < end,
        )
    ).scalar_one()

    by_category_rows = db.session.execute(
        db.select(Category.name, func.coalesce(func.sum(Expense.amount), 0))
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= start,
            Expense.expense_date < end,
        )
        .group_by(Category.name)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    by_category = [
        {
            "name": name,
            "total": total,
            "percent": float(total) / float(month_total) * 100 if month_total else 0,
        }
        for name, total in by_category_rows
    ]

    trend_start_year, trend_start_month = _shift_month(year, month, -5)
    trend_start, _ = _month_bounds(trend_start_year, trend_start_month)

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
        trend_year, trend_month = _shift_month(year, month, delta)
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

    prev_year, prev_month = _shift_month(year, month, -1)
    next_year, next_month = _shift_month(year, month, 1)

    return render_template(
        "dashboard/index.html",
        month_total=month_total,
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
