from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.db import Base, engine, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup. Replace with Alembic migrations if the schema grows.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Canadian Weather Tracker", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/cities")
def list_cities(session: Session = Depends(get_session)):
    cities = session.scalars(select(models.City).order_by(models.City.name)).all()
    return [
        {"id": c.id, "name": c.name, "latitude": c.latitude, "longitude": c.longitude}
        for c in cities
    ]


@app.get("/cities/{city_id}/latest")
def latest_observation(city_id: int, session: Session = Depends(get_session)):
    city = session.get(models.City, city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")

    obs = session.scalars(
        select(models.Observation)
        .where(models.Observation.city_id == city_id)
        .order_by(models.Observation.observed_at.desc())
        .limit(1)
    ).first()
    if obs is None:
        raise HTTPException(status_code=404, detail="No observations yet")

    return {
        "city": city.name,
        "observed_at": obs.observed_at.isoformat(),
        "temperature_c": obs.temperature_c,
        "condition": obs.condition,
    }
