#!/usr/bin/env bash
# One-time backend setup: virtual environment, packages, simulated seed data, database.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m simulation.generate
python -m simulation.seed_db
echo
echo "Setup done. Start the API with:"
echo "  source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
