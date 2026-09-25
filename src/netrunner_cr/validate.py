from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry
from referencing.jsonschema import DRAFT202012

from . import DATA_DIR, FIXTURES_DIR, SCHEMAS_DIR
from .build import load_pin


class ValidationError(Exception):
    pass


def validate_artifacts(*, live: bool = False) -> list[str]:
    errors: list[str] = []
    latest = _read(DATA_DIR / "latest.json")
    nodes = _read(DATA_DIR / "nodes.json")
    index = _read(DATA_DIR / "index.json")
    errors.extend(_schema_errors(latest, SCHEMAS_DIR / "document.schema.json"))
    for node in nodes:
        errors.extend(
            _schema_errors(node, SCHEMAS_DIR / "node.schema.json", prefix=node.get("id", "?"))
        )
    errors.extend(_uniqueness(nodes))
    errors.extend(_index_consistency(nodes, index))
    errors.extend(_heading_fixture(nodes))
    errors.extend(_required_exports())
    if live:
        errors.extend(_live_html(nodes))
    if errors:
        raise ValidationError("\n".join(errors))
    return []


def _read(path: Path) -> Any:
    if not path.exists():
        raise ValidationError(f"missing artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_errors(instance: Any, schema_path: Path, prefix: str = "") -> list[str]:
    store = {}
    for path in SCHEMAS_DIR.glob("*.schema.json"):
        contents = json.loads(path.read_text(encoding="utf-8"))
        store[contents["$id"]] = contents
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = Registry()
    for url, contents in store.items():
        registry = registry.with_resource(url, DRAFT202012.create_resource(contents))
    validator = Draft202012Validator(schema, registry=registry)
    messages = []
    for error in validator.iter_errors(instance):
        loc = ".".join(str(part) for part in error.path)
        label = f"{prefix} {loc}".strip()
        messages.append(f"schema {schema_path.name}: {label}: {error.message}")
    return messages


def _uniqueness(nodes: list[dict[str, Any]]) -> list[str]:
    errors = []
    seen_ids: dict[str, str] = {}
    seen_numbers: dict[str, str] = {}
    for node in nodes:
        ident = node["id"]
        number = node["number"]
        if ident in seen_ids:
            errors.append(f"duplicate id {ident}")
        seen_ids[ident] = number
        if number in seen_numbers:
            errors.append(
                f"duplicate number {number} ({seen_numbers[number]} and {ident})"
            )
        seen_numbers[number] = ident
    return errors


def _index_consistency(nodes: list[dict[str, Any]], index: dict[str, Any]) -> list[str]:
    errors = []
    expected_ids = {node["id"]: node["number"] for node in nodes}
    if index.get("ids") != expected_ids:
        errors.append("index.json ids map does not match nodes.json")
    return errors


def _required_exports() -> list[str]:
    required = [
        DATA_DIR / "nodes.jsonl",
        DATA_DIR / "refs.json",
        DATA_DIR / "cards.json",
        DATA_DIR / "terms.json",
        DATA_DIR / "changelog.json",
        DATA_DIR / "timing-structures.json",
    ]
    return [f"missing artifact: {path}" for path in required if not path.exists()]


def _heading_fixture(nodes: list[dict[str, Any]]) -> list[str]:
    fixture_path = FIXTURES_DIR / "published_headings.json"
    if not fixture_path.exists():
        return ["missing tests/fixtures/published_headings.json"]
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    by_number = {node["number"]: node for node in nodes if node["kind"] == "section"}
    errors = []
    for heading in fixture:
        number = heading["number"]
        title = heading["title"]
        node = by_number.get(number)
        if node is None:
            errors.append(f"published heading {number} missing from dataset")
            continue
        actual = node.get("title") or node["text_plain"]
        expected_prefix = title.lower().split("(")[0].strip()
        if not actual.lower().startswith(expected_prefix):
            errors.append(
                f"published heading {number} title mismatch: {actual!r} vs {title!r}"
            )
    return errors


def _live_html(nodes: list[dict[str, Any]]) -> list[str]:
    pin = load_pin()
    url = pin["published_url"]
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8", errors="replace")
    errors = []
    if pin["version"] not in html and f"v{pin['version']}" not in html:
        errors.append(f"live HTML does not mention CR version {pin['version']}")
    sample = [node for node in nodes if node["kind"] in {"section", "rule"}][:40]
    for node in sample:
        if node["id"] not in html:
            errors.append(f"live HTML missing id {node['id']}")
    return errors
