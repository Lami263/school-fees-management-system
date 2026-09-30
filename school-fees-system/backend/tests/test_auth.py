"""
Basic API-level (integration) tests for authentication, using Flask's
test client rather than calling services directly.
"""
import pytest


@pytest.fixture()
def client(app):
    return app.test_client()


def test_register_and_login_success(client):
    resp = client.post("/api/auth/register", json={
        "username": "newadmin", "password": "Secret123", "role": "admin"
    })
    assert resp.status_code == 201

    resp = client.post("/api/auth/login", json={
        "username": "newadmin", "password": "Secret123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_with_wrong_password_is_rejected(client):
    client.post("/api/auth/register", json={
        "username": "someuser", "password": "Correct123", "role": "bursar"
    })
    resp = client.post("/api/auth/login", json={
        "username": "someuser", "password": "WrongPassword"
    })
    assert resp.status_code == 401


def test_duplicate_username_registration_rejected(client):
    client.post("/api/auth/register", json={
        "username": "dupeuser", "password": "Secret123", "role": "bursar"
    })
    resp = client.post("/api/auth/register", json={
        "username": "dupeuser", "password": "Another123", "role": "bursar"
    })
    assert resp.status_code == 409


def test_protected_endpoint_requires_token(client):
    resp = client.get("/api/students")
    assert resp.status_code == 401
