#!/bin/sh
# Install application test dependencies into the repository's virtual environment.
set -eu
cd "$(CDPATH= cd "$(dirname "$0")/.." && pwd)"
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ is required"'
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements-dev.txt
.venv/bin/python scripts/test.py --check-tools
