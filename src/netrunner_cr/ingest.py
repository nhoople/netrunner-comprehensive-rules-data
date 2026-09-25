from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from . import PIN_PATH, YAML_DIR


CHAPTER_DIR = "data/input"
CHANGELOG_DIR = "data/changelogs"
NRDB_PATH = "generated/nrdb/nrdb.yaml"
CONFIG_PATH = "config.yaml"


def ingest(*, force: bool = False) -> Path:
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    sha = pin["source_sha"]
    dest = YAML_DIR
    if dest.exists() and not force:
        marker = dest / "SOURCE_SHA"
        if marker.exists() and marker.read_text(encoding="utf-8").strip() == sha:
            return dest
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "input").mkdir(exist_ok=True)
    (dest / "changelogs").mkdir(exist_ok=True)

    repo = pin["source_repo"].rstrip("/")
    if repo.endswith(".git"):
        repo = repo[:-4]
    slug = repo.replace("https://github.com/", "")
    base = f"https://raw.githubusercontent.com/{slug}/{sha}"

    for name in pin["chapter_files"]:
        _download(f"{base}/{CHAPTER_DIR}/{name}.yaml", dest / "input" / f"{name}.yaml")
    _download(f"{base}/{CHANGELOG_DIR}/{pin['version']}.yaml", dest / "changelogs" / f"{pin['version']}.yaml")
    _download(f"{base}/{NRDB_PATH}", dest / "nrdb.yaml")
    _download(f"{base}/{CONFIG_PATH}", dest / "config.yaml")
    (dest / "SOURCE_SHA").write_text(sha + "\n", encoding="utf-8")
    (dest / "README.md").write_text(
        (
            "Vendored YAML copied from the official Comprehensive Rules document "
            f"generator at `{pin['source_repo']}` @ `{sha}`.\n"
        ),
        encoding="utf-8",
    )
    return dest


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        dest.write_bytes(response.read())
