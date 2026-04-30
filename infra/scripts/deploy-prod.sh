#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/infra/env/.env.prod}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  echo "Create it from infra/env/.env.prod.example before deploying."
  exit 1
fi

health_url="$(grep -E '^HEALTHCHECK_URL=' "$ENV_FILE" | tail -n 1 | cut -d '=' -f 2- || true)"
health_url="${health_url:-http://127.0.0.1:18000/api/health}"

cd "$ROOT_DIR"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config >/dev/null
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build --remove-orphans
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T backend alembic upgrade head
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T backend python -m app.db.init_db

for _ in $(seq 1 30); do
  if curl -fsS "$health_url" >/dev/null; then
    echo "Deploy success: $health_url"
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
    exit 0
  fi
  sleep 2
done

echo "Deploy finished, but health check failed: $health_url"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=120 backend nginx
exit 1
