#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS}" = "true" ]; then
  tries=0
  max_tries="${MIGRATION_MAX_TRIES:-10}"
  upgraded="false"
  while [ "${tries}" -lt "${max_tries}" ]; do
    if flask --app run.py db upgrade; then
      upgraded="true"
      break
    fi
    tries=$((tries + 1))
    sleep 2
  done

  if [ "${upgraded}" != "true" ]; then
    if [ "${RUN_BOOTSTRAP_DB}" = "true" ]; then
      python - <<'PY'
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
PY
      flask --app run.py db stamp head
    else
      exit 1
    fi
  fi
fi

exec "$@"
