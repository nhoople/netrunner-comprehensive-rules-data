"""The README's Layout section names every folder in the repo, and only those.

Folders come from git: tracked files plus untracked files that .gitignore does
not ignore, so `.venv/`, `__pycache__/` and other local clutter never count,
but a new folder fails before it is committed.
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

# A table row whose first cell is a backticked folder, e.g. "| `data/` | ... |".
ROW = re.compile(r"^\|\s*`([^`]+)/`\s*\|")
# Script files use one naming style: snake_case, like Python module names.
SCRIPT_NAME = re.compile(r"^[a-z][a-z0-9_]*\.[a-z0-9]+$")


def layout_map_folders(readme_text: str) -> set[str]:
    """Folders listed in the README's "## Layout" table."""
    match = re.search(r"^## Layout\n(.*?)(?=^## |\Z)", readme_text, re.M | re.S)
    if match is None:
        raise AssertionError('README.md has no "## Layout" section')
    return {m.group(1) for line in match.group(1).splitlines() if (m := ROW.match(line))}


def repo_files() -> list[str]:
    if not (ROOT / ".git").exists():
        raise unittest.SkipTest("layout check needs a git checkout")
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [path for path in out.split("\0") if path and (ROOT / path).exists()]


def repo_folders(files: list[str]) -> set[str]:
    """Every folder that holds a file, and each folder above it."""
    folders: set[str] = set()
    for path in files:
        for parent in PurePosixPath(path).parents:
            if str(parent) != ".":
                folders.add(str(parent))
    return folders


class LayoutMapTests(unittest.TestCase):
    def test_every_folder_is_in_the_readme_layout_map(self) -> None:
        listed = layout_map_folders(README.read_text(encoding="utf-8"))
        actual = repo_folders(repo_files())
        missing = sorted(actual - listed)
        stale = sorted(listed - actual)
        problems = []
        if missing:
            problems.append(
                "Folders not in the README's Layout section: "
                + ", ".join(f"{f}/" for f in missing)
                + ". Add a row for each, saying what it holds."
            )
        if stale:
            problems.append(
                "The README's Layout section lists folders that do not exist: "
                + ", ".join(f"{f}/" for f in stale)
                + ". Remove or rename those rows."
            )
        if problems:
            self.fail("\n".join(problems))

    def test_script_files_use_snake_case(self) -> None:
        bad = sorted(
            path
            for path in repo_files()
            if path.startswith("scripts/")
            if not SCRIPT_NAME.match(PurePosixPath(path).name)
        )
        self.assertEqual(bad, [], "Name script files in snake_case, like ingest.py: " + str(bad))

    def test_layout_map_parser_reads_only_the_layout_table(self) -> None:
        text = (
            "# T\n\n## Consume\n\n| `nodes/` | x |\n\n"
            "## Layout\n\n| Folder | Holds |\n| --- | --- |\n| `data/` | a |\n| `src/x/` | b |\n\n"
            "## Next\n\n| `other/` | c |\n"
        )
        self.assertEqual(layout_map_folders(text), {"data", "src/x"})


if __name__ == "__main__":
    unittest.main()
