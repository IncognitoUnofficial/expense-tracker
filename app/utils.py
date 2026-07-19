from datetime import date

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def month_bounds(year, month):
    """Return (start, end_exclusive) dates for the given calendar month."""
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def shift_month(year, month, delta):
    """Shift (year, month) by delta months (can be negative)."""
    index = (year * 12 + (month - 1)) + delta
    return index // 12, index % 12 + 1
