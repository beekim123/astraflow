#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/infra/env/.env.prod}"
BACKUP_DIR="${BACKUP_DIR:-/opt/astraflow/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

postgres_user="$(grep -E '^POSTGRES_USER=' "$ENV_FILE" | tail -n 1 | cut -d '=' -f 2- || true)"
postgres_db="$(grep -E '^POSTGRES_DB=' "$ENV_FILE" | tail -n 1 | cut -d '=' -f 2- || true)"
postgres_user="${postgres_user:-astraflow}"
postgres_db="${postgres_db:-astraflow}"

mkdir -p "$BACKUP_DIR"

backup_file="$BACKUP_DIR/astraflow-$(date +%Y%m%d-%H%M%S).sql"

cd "$ROOT_DIR"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  pg_dump -U "$postgres_user" "$postgres_db" > "$backup_file"

find "$BACKUP_DIR" -type f -name "astraflow-*.sql" -mtime +"$RETENTION_DAYS" -delete

echo "Backup created: $backup_file"
