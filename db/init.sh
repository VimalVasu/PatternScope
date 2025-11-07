#!/bin/bash
set -e

echo "Running database migrations..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \i /docker-entrypoint-initdb.d/migrations/001_init.sql
    \i /docker-entrypoint-initdb.d/migrations/002_anomalies.sql
    \i /docker-entrypoint-initdb.d/migrations/003_trend_suggestions.sql
EOSQL

echo "Database migrations completed successfully!"
