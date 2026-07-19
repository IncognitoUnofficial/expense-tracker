from tests.conftest import login, register


def test_account_page_loads(client, registered_user):
    response = client.get("/account/")
    assert b"Jane" in response.data
    assert b"jane@example.com" in response.data


def test_update_profile_success(client, registered_user):
    response = client.post(
        "/account/profile",
        data={"name": "Jane Updated", "email": "jane-updated@example.com"},
        follow_redirects=True,
    )
    assert b"Profile updated" in response.data
    assert b"Jane Updated" in response.data


def test_update_profile_duplicate_email_rejected(client, registered_user):
    client.post("/logout")
    register(client, email="other@example.com", name="Other")
    client.post("/logout")
    login(client)

    response = client.post(
        "/account/profile",
        data={"name": "Jane", "email": "other@example.com"},
        follow_redirects=True,
    )
    assert b"already uses that email" in response.data


def test_change_password_wrong_current_rejected(client, registered_user):
    response = client.post(
        "/account/password",
        data={
            "current_password": "wrong-password",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123",
        },
        follow_redirects=True,
    )
    assert b"Current password is incorrect" in response.data


def test_change_password_success_then_login_with_new_password(client, registered_user):
    response = client.post(
        "/account/password",
        data={
            "current_password": "hunter2pass",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123",
        },
        follow_redirects=True,
    )
    assert b"Password changed" in response.data

    client.post("/logout")
    response = login(client, password="newpassword123")
    assert b"Dashboard" in response.data
