#!/bin/sh
# Aplica as migrations (Alembic é o dono do schema) e sobe a API.
set -e

echo "[entrypoint] alembic upgrade head..."
alembic upgrade head

echo "[entrypoint] iniciando uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
