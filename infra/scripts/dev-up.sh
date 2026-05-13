#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/infra/env/.env.local}"
COMPOSE_ARGS=(-f infra/docker-compose.local.yml --profile full)

cd "$ROOT_DIR"

if [[ -f "$ENV_FILE" ]]; then
  docker compose --env-file "$ENV_FILE" "${COMPOSE_ARGS[@]}" up --build
else
  echo "Local env file not found, running with default local config: $ENV_FILE"
  docker compose "${COMPOSE_ARGS[@]}" up --build
fi
