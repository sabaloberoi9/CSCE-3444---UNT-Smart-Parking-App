"""Create the SQLite database and load the seed data (TR-62, TR-63, TR-65).

Run from the backend folder (after `python -m simulation.generate`):
    python -m simulation.seed_db            # create + seed if empty
    python -m simulation.seed_db --reset    # wipe every table and seed again

The API also seeds an empty database automatically on startup.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402
from app.services.db import Database  # noqa: E402

REQUIRED = ("users.json", "schedules.json", "events.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true", help="delete all rows and seed again")
    args = parser.parse_args()

    missing = [f for f in REQUIRED if not (settings.data_dir / f).exists()]
    if missing:
        sys.exit(f"Missing {', '.join(missing)} in {settings.data_dir}. Run: python -m simulation.generate")

    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(settings.db_path)
    if args.reset:
        db.reset_and_seed(settings.data_dir)
    else:
        db.seed(settings.data_dir)

    print(f"Database: {settings.db_path}")
    for table, n in db.counts().items():
        print(f"  {table:<14} {n:>4} rows")


if __name__ == "__main__":
    main()
