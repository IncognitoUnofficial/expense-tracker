from app.extensions import db
from app.models import Expense


def create_expense(client, category_id, amount="42.00", expense_date="2026-07-15", description="Groceries run"):
    return client.post(
        "/expenses/new",
        data={
            "amount": amount,
            "category_id": category_id,
            "expense_date": expense_date,
            "description": description,
        },
        follow_redirects=True,
    )


def test_create_expense(client, registered_user, first_category_id):
    response = create_expense(client, first_category_id)
    assert b"Groceries run" in response.data
    assert b"42.00" in response.data


def test_list_filters_by_category(client, registered_user, first_category_id):
    create_expense(client, first_category_id, description="Coffee")

    response = client.get(f"/expenses/?category={first_category_id}")
    assert b"Coffee" in response.data

    response = client.get("/expenses/?category=999999")
    assert b"No expenses match" in response.data


def test_list_filters_by_month(client, registered_user, first_category_id):
    create_expense(client, first_category_id, expense_date="2026-07-15", description="July expense")
    create_expense(client, first_category_id, expense_date="2026-01-10", description="January expense")

    response = client.get("/expenses/?month=2026-07")
    assert b"July expense" in response.data
    assert b"January expense" not in response.data


def test_list_filters_by_search(client, registered_user, first_category_id):
    create_expense(client, first_category_id, description="Coffee with team")
    create_expense(client, first_category_id, description="Bus ticket")

    response = client.get("/expenses/?q=coffee")
    assert b"Coffee with team" in response.data
    assert b"Bus ticket" not in response.data


def test_edit_expense(client, registered_user, first_category_id):
    create_expense(client, first_category_id, description="Old description")
    with client.application.app_context():
        expense = db.session.execute(db.select(Expense)).scalar_one()
        expense_id = expense.id

    response = client.post(
        f"/expenses/{expense_id}/edit",
        data={
            "amount": "99.99",
            "category_id": first_category_id,
            "expense_date": "2026-07-20",
            "description": "New description",
        },
        follow_redirects=True,
    )
    assert b"New description" in response.data
    assert b"99.99" in response.data


def test_delete_expense(client, registered_user, first_category_id):
    create_expense(client, first_category_id, description="Delete me")
    with client.application.app_context():
        expense = db.session.execute(db.select(Expense)).scalar_one()
        expense_id = expense.id

    response = client.post(f"/expenses/{expense_id}/delete", follow_redirects=True)
    assert b"Delete me" not in response.data


def test_csv_export_returns_all_matching_rows(client, registered_user, first_category_id):
    create_expense(client, first_category_id, amount="10.00", description="Coffee")
    create_expense(client, first_category_id, amount="20.00", description="Bus ticket")

    response = client.get("/expenses/export")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]

    body = response.data.decode()
    rows = body.strip().splitlines()
    assert rows[0] == "Date,Category,Description,Amount"
    assert any("Coffee" in row and "10.00" in row for row in rows[1:])
    assert any("Bus ticket" in row and "20.00" in row for row in rows[1:])


def test_csv_export_respects_filters(client, registered_user, first_category_id):
    create_expense(client, first_category_id, description="Coffee", expense_date="2026-07-05")
    create_expense(client, first_category_id, description="Bus ticket", expense_date="2026-07-05")

    response = client.get("/expenses/export?q=coffee")
    body = response.data.decode()
    assert "Coffee" in body
    assert "Bus ticket" not in body


def test_cannot_access_another_users_expense(client, registered_user, first_category_id):
    create_expense(client, first_category_id, description="Mine")
    with client.application.app_context():
        expense = db.session.execute(db.select(Expense)).scalar_one()
        expense_id = expense.id

    client.post("/logout")
    from tests.conftest import register

    register(client, email="other@example.com", name="Other")

    response = client.get(f"/expenses/{expense_id}/edit")
    assert response.status_code == 404
