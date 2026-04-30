from fastapi.testclient import TestClient

from app.main import app


def test_captcha_can_be_generated():
    client = TestClient(app)
    response = client.get("/api/security/visitor-captcha")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["captcha_id"]
    assert "?" in data["question"]


def test_captcha_wrong_answer_fails():
    client = TestClient(app)
    captcha = client.get("/api/security/visitor-captcha").json()["data"]
    response = client.post(
        "/api/security/visitor-captcha/verify",
        json={"captcha_id": captcha["captcha_id"], "answer": "wrong"},
    )
    assert response.status_code == 400

