# Canadian Weather Tracker

A small data pipeline and API built on top of Environment and Climate Change Canada's (ECCC) open weather data.

A scheduled shell job fetches city weather from the public MSC GeoMet API, a Python script parses and stores it in PostgreSQL, and a FastAPI service exposes it over REST. A React + OpenLayers map frontend is planned.

> **Disclaimer:** This is an independent learning project. It is not affiliated with or endorsed by ECCC or the Government of Canada.
>
> **Data source:** Contains information from the Meteorological Service of Canada (MSC), Environment and Climate Change Canada, via [MSC GeoMet](https://api.weather.gc.ca/). Use of the data is subject to the MSC Datamart end-user license.

## Architecture

```
ECCC GeoMet API  ->  fetch_weather.sh (curl + cron)  ->  ingest.py  ->  PostgreSQL  ->  FastAPI  ->  (React + OpenLayers map)
```

See [docs/architecture.md](docs/architecture.md) for diagrams.

## Tech stack

Python, FastAPI, SQLAlchemy, PostgreSQL, Docker Compose, Bash/cron, pytest, GitHub Actions. Planned: React, OpenLayers.

## Run locally

Requires Docker.

```bash
docker compose up --build        # starts PostgreSQL and the API on http://localhost:8000
bash scripts/fetch_weather.sh    # fetches data and loads it into the database
```

Then open http://localhost:8000/docs for the interactive API docs.

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/cities` | List stored cities |
| GET | `/cities/{city_id}/latest` | Most recent observation for a city |

### Schedule it (Linux/macOS)

```cron
*/30 * * * * cd /path/to/weather-tracker && bash scripts/fetch_weather.sh >> fetch.log 2>&1
```

## Tests

```bash
pip install -r backend/requirements.txt
PYTHONPATH=backend DATABASE_URL=sqlite:///./test.db pytest backend/tests
```

CI runs the same tests on every push (see `.github/workflows/ci.yml`).

## Roadmap

- [ ] Fill in the API field mapping in `scripts/ingest.py`
- [ ] Add a React + OpenLayers map showing city markers and current temperature
- [ ] Parse CAP weather alerts (XML) from the MSC Datamart
- [ ] Add retry and caching around the fetch step
