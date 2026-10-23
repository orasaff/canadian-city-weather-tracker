# Architecture

## Data flow

```mermaid
flowchart LR
    A[ECCC GeoMet API] -->|curl, every 30 min via cron| B[fetch_weather.sh]
    B --> C[ingest.py]
    C --> D[(PostgreSQL)]
    D --> E[FastAPI service]
    E --> F[React + OpenLayers map - planned]
```

## Data model

```mermaid
classDiagram
    class City {
        +int id
        +str name
        +float latitude
        +float longitude
    }
    class Observation {
        +int id
        +int city_id
        +datetime observed_at
        +float temperature_c
        +str condition
    }
    City "1" --> "*" Observation : has
```

## Design notes

- `scripts/ingest.py` separates parsing (`parse_items`) from storage (`save`), so the API format can change without touching the database code.
- Observations are de-duplicated on `(city_id, observed_at)`, so re-running the fetch is safe.
- Tests run against SQLite so CI does not need a PostgreSQL service.
