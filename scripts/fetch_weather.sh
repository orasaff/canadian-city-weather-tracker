#!/usr/bin/env bash
# Fetch city weather from the ECCC GeoMet API and load it into the database.
# Intended to be run from the repo root, manually or via cron.
set -euo pipefail

cd "$(dirname "$0")/.."

# Default endpoint (experimental collection). Override by exporting WEATHER_URL.
URL="${WEATHER_URL:-https://api.weather.gc.ca/collections/citypageweather-realtime/items?f=json&limit=50}"
OUT="data/latest.json"

mkdir -p data

echo "$(date -u +%FT%TZ) fetching $URL"
curl --fail --silent --show-error --retry 3 --retry-delay 5 "$URL" -o "$OUT"

echo "$(date -u +%FT%TZ) loading into database"
docker compose exec -T api python scripts/ingest.py "$OUT"
