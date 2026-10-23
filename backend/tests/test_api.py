from datetime import datetime

from fastapi.testclient import TestClient

from app import models
from app.db import Base, SessionLocal, engine
from app.main import app


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_latest_observation_returns_newest_row():
    with SessionLocal() as session:
        city = models.City(name="Toronto", latitude=43.65, longitude=-79.38)
        session.add(city)
        session.flush()
        session.add_all(
            [
                models.Observation(
                    city_id=city.id,
                    observed_at=datetime(2026, 10, 23, 12, 0),
                    temperature_c=10.0,
                    condition="Cloudy",
                ),
                models.Observation(
                    city_id=city.id,
                    observed_at=datetime(2026, 10, 23, 13, 0),
                    temperature_c=12.5,
                    condition="Sunny",
                ),
            ]
        )
        session.commit()
        city_id = city.id

    with TestClient(app) as client:
        data = client.get(f"/cities/{city_id}/latest").json()

    assert data["temperature_c"] == 12.5
    assert data["condition"] == "Sunny"


def test_unknown_city_returns_404():
    with TestClient(app) as client:
        assert client.get("/cities/999/latest").status_code == 404
