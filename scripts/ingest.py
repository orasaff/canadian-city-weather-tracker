"""Load a JSON file fetched from the ECCC GeoMet API into the database.

Usage:
    python scripts/ingest.py data/latest.json
"""
import argparse
import json
from datetime import datetime

from sqlalchemy import select

from app import models
from app.db import Base, SessionLocal, engine


def parse_items(payload: dict) -> list[dict]:
    """Turn the raw GeoMet response into a list of plain dicts.

    Each dict must have these keys:
        name (str), latitude (float), longitude (float),
        observed_at (datetime), temperature_c (float | None), condition (str | None)

    TODO: fill this in yourself.
      1. Run: curl -s "https://api.weather.gc.ca/collections/citypageweather-realtime/items?f=json&limit=5" | python -m json.tool | less
      2. Find where the city name, coordinates, timestamp, temperature and
         condition live in the response (the collection is marked experimental,
         so check the structure before relying on it).
      3. Return one dict per city.
    """
    raise NotImplementedError("Map the GeoMet response fields in parse_items()")


def save(items: list[dict]) -> int:
    """Insert cities (if new) and one observation per item. Returns rows added."""
    Base.metadata.create_all(bind=engine)
    added = 0
    with SessionLocal() as session:
        for item in items:
            city = session.scalars(
                select(models.City).where(models.City.name == item["name"])
            ).first()
            if city is None:
                city = models.City(
                    name=item["name"],
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                )
                session.add(city)
                session.flush()

            observed_at: datetime = item["observed_at"]
            exists = session.scalars(
                select(models.Observation).where(
                    models.Observation.city_id == city.id,
                    models.Observation.observed_at == observed_at,
                )
            ).first()
            if exists is None:
                session.add(
                    models.Observation(
                        city_id=city.id,
                        observed_at=observed_at,
                        temperature_c=item["temperature_c"],
                        condition=item["condition"],
                    )
                )
                added += 1
        session.commit()
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", help="Path to a JSON file saved from the GeoMet API")
    args = parser.parse_args()

    with open(args.json_file, encoding="utf-8") as f:
        payload = json.load(f)

    added = save(parse_items(payload))
    print(f"Added {added} new observations")


if __name__ == "__main__":
    main()
