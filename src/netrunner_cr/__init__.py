"""Shared constants for the CR conversion toolchain."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "source"
YAML_DIR = SOURCE_DIR / "yaml"
PIN_PATH = SOURCE_DIR / "pin.json"
DATA_DIR = ROOT / "data"
NODES_DIR = ROOT / "nodes"
SCHEMAS_DIR = ROOT / "schemas"
TESTS_DIR = ROOT / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"

PUBLISHED_BASE = "https://rules.nullsignal.games/"

SYMBOL_FROM_BRACKET = {
    "[c]": "credit",
    "[click]": "click",
    "[recurring]": "recurring",
    "[link]": "link",
    "[MU]": "mu",
    "[sub]": "sub",
    "[trash]": "trash",
    "[interrupt]": "interrupt",
    "[trashcost]": "trashcost",
}

SYMBOL_PLAIN = {
    "credit": "{c}",
    "click": "{click}",
    "recurring": "{recurring}",
    "link": "{link}",
    "mu": "{MU}",
    "sub": "{sub}",
    "trash": "{trash}",
    "interrupt": "{interrupt}",
    "trashcost": "{trashcost}",
}

LETTERS = "abcdefghijklmn"
ROMAN = [
    "i",
    "ii",
    "iii",
    "iv",
    "v",
    "vi",
    "vii",
    "viii",
    "ix",
    "x",
    "xi",
    "xii",
    "xiii",
    "xiv",
]
