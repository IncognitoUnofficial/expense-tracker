from app.extensions import db
from app.models import Category, User
from tests.conftest import login, register


def test_register_creates_user_and_default_categories(client):
    response = register(client)
    assert response.status_code == 200
    assert b"Dashboard" in response.data

    with client.application.app_context():
        user = db.session.execute(db.select(User)).scalar_one()
        assert user.email == "jane@example.com"
        categories = db.session.execute(
            db.select(Category).filter_by(user_id=user.id)
        ).scalars().all()
        assert len(categories) == 7


def test_register_rejects_duplicate_email(client):
    register(client)
    client.post("/logout")
    response = register(client, name="Jane Two")
    assert b"already exists" in response.data


def test_login_rejects_wrong_password(client):
    register(client)
    client.post("/logout")
    response = login(client, password="wrong-password")
    assert b"Invalid email or password" in response.data


def test_login_succeeds_with_correct_credentials(client):
    register(client)
    client.post("/logout")
    response = login(client)
    assert b"Dashboard" in response.data


def test_protected_route_redirects_to_login_when_logged_out(client):
    response = client.get("/expenses/", follow_redirects=True)
    assert b"Log in" in response.data


def test_logout_ends_session(client):
    register(client)
    client.post("/logout")
    response = client.get("/expenses/", follow_redirects=True)
    assert b"Log in" in response.data
