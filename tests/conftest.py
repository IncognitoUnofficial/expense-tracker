import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models import Category, Expense, User


@pytest.fixture
def app():
    application = create_app(TestConfig)

    with application.app_context():
        _db.create_all()

    # Deliberately not holding the app context open across `yield`: if it stayed
    # pushed, every client.post()/get() below would silently reuse this same
    # context (and its DB session/transaction) instead of opening its own, and
    # under MySQL's REPEATABLE READ isolation that session's snapshot goes stale
    # the moment another context commits — the delete-guard test saw exactly
    # this, reading a category's expenses as empty after they'd been committed.
    yield application

    with application.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


def register(client, email="jane@example.com", password="hunter2pass", name="Jane"):
    return client.post(
        "/register",
        data={
            "name": name,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email="jane@example.com", password="hunter2pass"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


@pytest.fixture
def registered_user(client, db):
    register(client)
    with client.application.app_context():
        user = db.session.execute(db.select(User)).scalar_one()
        return user.id


@pytest.fixture
def first_category_id(client, registered_user, db):
    with client.application.app_context():
        category = db.session.execute(
            db.select(Category).filter_by(user_id=registered_user)
        ).scalars().first()
        return category.id
