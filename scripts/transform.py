#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from netrunner_cr.build import build_document  # noqa: E402
from netrunner_cr.emit import emit_all  # noqa: E402
from netrunner_cr.ingest import ingest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Transform CR YAML into JSON artifacts.")
    parser.add_argument("--ingest", action="store_true", help="Fetch YAML before transforming.")
    args = parser.parse_args()
    if args.ingest:
        ingest()
    document = build_document()
    emit_all(document)
    meta = document["metadata"]
    print(
        f"Wrote {meta['node_count']} nodes for CR v{meta['version']} "
        f"(source {meta['source_sha'][:12]})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
