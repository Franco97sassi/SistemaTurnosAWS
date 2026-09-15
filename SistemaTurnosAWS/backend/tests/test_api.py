import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app, get_db


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    def override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        login = test_client.post(
            "/auth/login",
            json={"email": "admin@turnos.local", "password": "TurnosDemo2026!"},
        )
        test_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield test_client
    app.dependency_overrides.clear()


def payload(fecha="2035-05-10T14:30:00Z"):
    return {"cliente": "  Ada Lovelace  ", "servicio": "Consultoría", "fecha": fecha}


def test_health_and_request_id(client):
    response = client.get("/health", headers={"X-Request-ID": "portfolio-check"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "portfolio-check"


def test_authentication_is_required_and_identity_is_available(client):
    anonymous = TestClient(app)
    assert anonymous.get("/turnos").status_code == 401
    assert anonymous.post(
        "/auth/login", json={"email": "admin@turnos.local", "password": "incorrecta"}
    ).status_code == 401
    identity = client.get("/auth/me")
    assert identity.status_code == 200
    assert identity.json()["role"] == "admin"


def test_readiness_checks_database(client):
    assert client.get("/ready").json() == {"status": "ready"}


def test_turno_http_lifecycle(client):
    created = client.post("/turnos", json=payload())
    assert created.status_code == 201
    assert created.json()["cliente"] == "Ada Lovelace"

    listed = client.get("/turnos", params={"estado": "pendiente", "search": "Ada"})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    turno_id = listed.json()["items"][0]["id"]

    updated = client.patch(f"/turnos/{turno_id}", json={"fecha": "2035-06-12T09:00:00Z"})
    assert updated.status_code == 200
    assert updated.json()["fecha"].startswith("2035-06-12")

    cancelled = client.delete(f"/turnos/{turno_id}")
    assert cancelled.status_code == 200
    assert client.get("/turnos", params={"estado": "cancelado"}).json()["total"] == 1


def test_slot_conflict_returns_409(client):
    assert client.post("/turnos", json=payload()).status_code == 201
    conflict = client.post("/turnos", json=payload())
    assert conflict.status_code == 409
    assert "fecha" in conflict.json()["detail"]


@pytest.mark.parametrize(
    "invalid",
    [
        {"cliente": " ", "servicio": "A", "fecha": "not-a-date"},
        payload("2020-01-01T10:00:00Z"),
    ],
)
def test_invalid_turno_returns_422(client, invalid):
    assert client.post("/turnos", json=invalid).status_code == 422


def test_not_found_and_cancelled_cannot_be_rescheduled(client):
    assert client.delete("/turnos/9999").status_code == 404
    turno_id = client.post("/turnos", json=payload()).json()["id"]
    client.delete(f"/turnos/{turno_id}")
    response = client.patch(f"/turnos/{turno_id}", json={"fecha": "2036-01-01T10:00:00Z"})
    assert response.status_code == 409


def test_pagination(client):
    client.post("/turnos", json=payload("2035-01-01T10:00:00Z"))
    client.post("/turnos", json=payload("2035-01-02T10:00:00Z"))
    response = client.get("/turnos", params={"page": 2, "page_size": 1})
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 1
