#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../backend"
python -m alembic upgrade head
python -m app.db.init_db
