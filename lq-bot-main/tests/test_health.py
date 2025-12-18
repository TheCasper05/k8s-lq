from fastapi.testclient import TestClient

from src.interfaces.api.main import create_app

NOT_FOUND_CODE = 404
STATUS_OK_CODE = 200


def test_health_ok():
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == STATUS_OK_CODE
    assert resp.json() == {"status": "ok"}


def test_health_not_found():
    client = TestClient(create_app())
    resp = client.get("/not-found")
    assert resp.status_code == NOT_FOUND_CODE
    assert resp.json() == {"detail": "Not Found"}
