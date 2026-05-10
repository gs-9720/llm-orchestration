from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_models() -> None:
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
