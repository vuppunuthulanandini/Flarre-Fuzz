#!/usr/bin/env bash
# One-command launcher for macOS / Linux
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
echo "Starting Flarre-Fuzz at http://127.0.0.1:8000 ..."
python -m flarre_fuzz
