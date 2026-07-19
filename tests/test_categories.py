from datetime import date

from app.extensions import db
from app.models import Category, Expense


def test_list_shows_default_categories(client, registered_user):
    response = client.get("/categories/")
    assert b"Food" in response.data
    assert b"Transport" in response.data


def test_create_category(client, registered_user):
    response = client.post("/categories/", data={"name": "Pets"}, follow_redirects=True)
    assert b"Pets" in response.data


def test_create_duplicate_category_name_rejected(client, registered_user):
    client.post("/categories/", data={"name": "Pets"}, follow_redirects=True)
    response = client.post("/categories/", data={"name": "Pets"}, follow_redirects=True)
    assert b"already have a category" in response.data


def test_edit_category(client, registered_user, first_category_id):
    response = client.post(
        f"/categories/{first_category_id}/edit",
        data={"name": "Groceries"},
        follow_redirects=True,
    )
    assert b"Groceries" in response.data


def test_delete_category_without_expenses_succeeds(client, registered_user, first_category_id):
    response = client.post(f"/categories/{first_category_id}/delete", follow_redirects=True)
    assert b"deleted" in response.data


def test_delete_category_with_expenses_is_blocked(client, registered_user, first_category_id, db):
    with client.application.app_context():
        expense = Expense(
            user_id=registered_user,
            category_id=first_category_id,
            amount="12.50",
            expense_date=date(2026, 7, 1),
        )
        db.session.add(expense)
        db.session.commit()

    response = client.post(f"/categories/{first_category_id}/delete", follow_redirects=True)
    assert b"linked to it" in response.data

    with client.application.app_context():
        assert db.session.get(Category, first_category_id) is not None


def test_create_category_with_budget(client, registered_user):
    response = client.post(
        "/categories/", data={"name": "Pets", "monthly_budget": "150.00"}, follow_redirects=True
    )
    assert b"Pets" in response.data


def test_category_list_shows_budget_progress(client, registered_user, first_category_id, db):
    with client.application.app_context():
        category_name = db.session.get(Category, first_category_id).name

    client.post(
        f"/categories/{first_category_id}/edit",
        data={"name": category_name, "monthly_budget": "100.00"},
        follow_redirects=True,
    )

    with client.application.app_context():
        expense = Expense(
            user_id=registered_user,
            category_id=first_category_id,
            amount="40.00",
            expense_date=date.today(),
        )
        db.session.add(expense)
        db.session.commit()

    response = client.get("/categories/")
    assert b"100.00" in response.data
    assert b"40.00" in response.data


def test_category_over_budget_shows_label(client, registered_user, first_category_id, db):
    with client.application.app_context():
        category_name = db.session.get(Category, first_category_id).name

    client.post(
        f"/categories/{first_category_id}/edit",
        data={"name": category_name, "monthly_budget": "50.00"},
        follow_redirects=True,
    )

    with client.application.app_context():
        expense = Expense(
            user_id=registered_user,
            category_id=first_category_id,
            amount="75.00",
            expense_date=date.today(),
        )
        db.session.add(expense)
        db.session.commit()

    response = client.get("/categories/")
    assert b"Over budget" in response.data


def test_cannot_access_another_users_category(client, registered_user, first_category_id):
    client.post("/logout")
    from tests.conftest import register

    register(client, email="other@example.com", name="Other")

    response = client.post(f"/categories/{first_category_id}/delete")
    assert response.status_code == 404
