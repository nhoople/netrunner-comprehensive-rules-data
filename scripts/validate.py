#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from netrunner_cr.validate import ValidationError, validate_artifacts  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated CR artifacts.")
    parser.add_argument("--live", action="store_true", help="Also check published HTML.")
    args = parser.parse_args()
    try:
        validate_artifacts(live=args.live)
    except ValidationError as exc:
        print(exc, file=sys.stderr)
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
