#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from netrunner_cr.ingest import ingest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch pinned official CR YAML.")
    parser.add_argument("--force", action="store_true", help="Re-download even if SOURCE_SHA matches.")
    args = parser.parse_args()
    dest = ingest(force=args.force)
    print(f"Ingested YAML into {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
