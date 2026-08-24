from fastapi.testclient import TestClient

from src.waffle.api.app import app


client = TestClient(app)


def test_state_endpoint():
    response = client.get("/state")

    assert response.status_code == 200

    data = response.json()

    assert "supply" in data
    assert "fee_balance" in data
    assert data["supply"] >= 0
    assert data["fee_balance"] >= 0
