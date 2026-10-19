#!/bin/sh
set -eu
cd "$(CDPATH= cd "$(dirname "$0")/.." && pwd)"
: "${VIRTUAL_ENV:=/workspace/.venv}"
if [ ! -x "$VIRTUAL_ENV/bin/python" ]; then
  python3 -m venv "$VIRTUAL_ENV"
fi
"$VIRTUAL_ENV/bin/python" -m pip install --only-binary=:all: -r requirements-dev.txt
exec "$VIRTUAL_ENV/bin/python" -u scripts/dev_server.py
