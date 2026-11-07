import os
os.environ["DATABASE_URL"] = "sqlite:///./test_tracker.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_and_paper_crud():
    email = "test.user@example.com"
    client.post("/api/auth/register", json={"name": "Test User", "email": email, "password": "sample-password-123"})
    login = client.post("/api/auth/login", json={"email": email, "password": "sample-password-123"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    created = client.post("/api/papers", headers=headers, json={"title":"Testing retrieval augmented systems", "year":2024, "abstract":"A test paper on retrieval systems", "topics":["Information Retrieval"], "authors":["Example Author"]})
    assert created.status_code == 201
    paper_id = created.json()["id"]
    assert client.get(f"/api/papers/{paper_id}").json()["title"] == "Testing retrieval augmented systems"
    assert client.delete(f"/api/papers/{paper_id}", headers=headers).status_code == 204


def test_protected_write_and_topic_api():
    assert client.post("/api/papers", json={"title":"Unauthorized paper"}).status_code == 401
    assert client.get("/api/topics").status_code == 200


def test_nlp_and_chat_fallback():
    keywords = client.post("/api/nlp/keywords", params={"text":"Transformers improve natural language processing systems"})
    assert "transformers" in keywords.json()["keywords"]
    answer = client.post("/api/chat", json={"question":"Find papers about a missing subject"})
    assert answer.status_code == 200
    assert answer.json()["mode"] == "local-retrieval"


def test_jobs_prediction_search():
    assert client.get("/api/jobs/analytics").json()["sample_data"] is True
    assert client.get("/api/predictions").status_code == 200
    assert client.get("/api/search", params={"q":"transformer"}).status_code == 200
