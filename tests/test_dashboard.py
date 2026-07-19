import re

from tests.test_expenses import create_expense


def _month_total_shown(response_data):
    match = re.search(rb"Month total.*?\$([\d,.]+)", response_data, re.DOTALL)
    assert match, "could not find the month total figure on the dashboard"
    return match.group(1).decode()


def test_dashboard_shows_empty_state_with_no_expenses(client, registered_user):
    response = client.get("/")
    assert b"haven&#39;t logged any expenses" in response.data or b"haven't logged any expenses" in response.data


def test_dashboard_shows_month_total(client, registered_user, first_category_id):
    create_expense(client, first_category_id, amount="30.00", expense_date="2026-07-05")
    create_expense(client, first_category_id, amount="20.00", expense_date="2026-07-10")

    response = client.get("/?month=2026-07")
    assert _month_total_shown(response.data) == "50.00"


def test_dashboard_excludes_other_months_from_total(client, registered_user, first_category_id):
    # Note: "recent expenses" is intentionally a global activity feed (not
    # scoped to the selected month), so the January expense will still show
    # up there — only the "month total" figure itself should exclude it.
    create_expense(client, first_category_id, amount="30.00", expense_date="2026-07-05")
    create_expense(client, first_category_id, amount="999.00", expense_date="2026-01-05")

    response = client.get("/?month=2026-07")
    assert _month_total_shown(response.data) == "30.00"


def test_dashboard_recent_expenses_lists_latest_first(client, registered_user, first_category_id):
    create_expense(client, first_category_id, description="First", expense_date="2026-07-01")
    create_expense(client, first_category_id, description="Second", expense_date="2026-07-15")

    response = client.get("/")
    first_index = response.data.find(b"First")
    second_index = response.data.find(b"Second")
    assert second_index < first_index
