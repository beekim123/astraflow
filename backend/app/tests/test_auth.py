import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_me_without_token_is_401():
    client = TestClient(app)
    response = client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.skipif(os.getenv("RUN_DB_TESTS") != "1", reason="requires local PostgreSQL seed data")
def test_login_success_returns_token():
    client = TestClient(app)
    response = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123456"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["access_token"]
    assert data["refresh_token"]

