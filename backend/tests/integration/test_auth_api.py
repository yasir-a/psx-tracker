from __future__ import annotations

from flask.testing import FlaskClient


def test_full_auth_lifecycle(client: FlaskClient) -> None:
    # 1. Register
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "ahmed.ali@example.com",
            "password": "Password123!",
            "full_name": "Ahmed Ali",
        },
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.get_json()
    assert reg_data["user"]["email"] == "ahmed.ali@example.com"
    access_token = reg_data["tokens"]["access_token"]
    refresh_token = reg_data["tokens"]["refresh_token"]

    # 2. Access protected /me route
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.get_json()
    assert me_data["user"]["full_name"] == "Ahmed Ali"

    # 3. Refresh token
    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    new_access_token = refresh_resp.get_json()["access_token"]
    assert new_access_token is not None

    # 4. Login with same credentials
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ahmed.ali@example.com",
            "password": "Password123!",
        },
    )
    assert login_resp.status_code == 200

    # 5. Invalid login attempt
    bad_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ahmed.ali@example.com",
            "password": "WrongPassword!",
        },
    )
    assert bad_login.status_code == 401