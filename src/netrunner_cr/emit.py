from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from . import DATA_DIR, NODES_DIR
from .build import node_filename


def emit_all(document: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    nodes = document["nodes"]
    metadata = document["metadata"]
    changelog = document["changelog"]
    by_id = {node["id"]: node for node in nodes}

    tree = [_with_children(node, by_id) for node in nodes if node["parent_id"] is None]
    latest = {"metadata": metadata, "changelog": changelog, "tree": tree}
    _write_json(DATA_DIR / "latest.json", latest)
    _write_json(DATA_DIR / "nodes.json", nodes)
    (DATA_DIR / "nodes.jsonl").write_text(
        "".join(json.dumps(node, ensure_ascii=False) + "\n" for node in nodes),
        encoding="utf-8",
    )
    _write_json(DATA_DIR / "index.json", _index(document, nodes))
    _write_json(DATA_DIR / "refs.json", _refs(nodes))
    _write_json(DATA_DIR / "cards.json", _cards(nodes))
    _write_json(DATA_DIR / "terms.json", _terms(nodes))
    _write_json(DATA_DIR / "changelog.json", {"metadata": metadata, "entries": changelog})
    _write_json(
        DATA_DIR / "timing-structures.json",
        [node for node in nodes if node["kind"] == "timing_structure"],
    )
    _emit_node_files(nodes)


def _with_children(node: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    copy = dict(node)
    copy["children"] = [_with_children(by_id[child_id], by_id) for child_id in node["child_ids"] if child_id in by_id]
    return copy


def _index(document: dict[str, Any], nodes: list[dict[str, Any]]) -> dict[str, Any]:
    toc = [
        {"id": node["id"], "number": node["number"], "title": node["title"] or node["text_plain"], "kind": node["kind"]}
        for node in nodes
        if node["toc"]
    ]
    return {
        "metadata": document["metadata"],
        "toc": toc,
        "ids": {node["id"]: node["number"] for node in nodes},
        "numbers": {node["number"]: node["id"] for node in nodes},
    }


def _refs(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    outgoing: dict[str, list[str]] = {}
    incoming: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        targets: list[str] = []
        for span in node["spans"]:
            if span.get("type") == "ref":
                targets.extend(span.get("ids") or [])
        if targets:
            unique = list(dict.fromkeys(targets))
            outgoing[node["id"]] = unique
            for target in unique:
                incoming[target].append(node["id"])
    return {"outgoing": outgoing, "incoming": dict(incoming)}


def _cards(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mentions: dict[str, dict[str, Any]] = {}
    for node in nodes:
        for span in node["spans"]:
            if span.get("type") != "card":
                continue
            name = span.get("target") or ""
            record = mentions.setdefault(
                name,
                {"name": name, "card_code": span.get("card_code"), "node_ids": []},
            )
            if span.get("card_code") and not record["card_code"]:
                record["card_code"] = span["card_code"]
            if node["id"] not in record["node_ids"]:
                record["node_ids"].append(node["id"])
    return sorted(mentions.values(), key=lambda item: item["name"].lower())


def _terms(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mentions: dict[str, dict[str, Any]] = {}
    for node in nodes:
        for span in node["spans"]:
            if span.get("type") not in {"term", "subtype"}:
                continue
            key = f"{span['type']}:{span.get('target')}"
            record = mentions.setdefault(
                key,
                {"type": span["type"], "text": span.get("target"), "node_ids": []},
            )
            if node["id"] not in record["node_ids"]:
                record["node_ids"].append(node["id"])
    return sorted(mentions.values(), key=lambda item: (item["type"], item["text"] or ""))


def _emit_node_files(nodes: list[dict[str, Any]]) -> None:
    if NODES_DIR.exists():
        for path in NODES_DIR.glob("*.json"):
            path.unlink()
    else:
        NODES_DIR.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    for node in nodes:
        name = node_filename(node["number"])
        if name in used:
            name = f"{node['number']}__{node['id']}.json"
        used.add(name)
        _write_json(NODES_DIR / name, node)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
