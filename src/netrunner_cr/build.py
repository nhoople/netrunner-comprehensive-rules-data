from __future__ import annotations

import json
from typing import Any

from . import PIN_PATH, PUBLISHED_BASE, YAML_DIR
from .markup import parse_markup
from .numbering import number_document
from .parse_yaml import (
    Chapter,
    Example,
    Rule,
    Section,
    SubSection,
    TimingElement,
    TimingStructure,
    load_yaml_file,
    parse_changelog,
    parse_chapter,
)


def load_pin() -> dict[str, Any]:
    return json.loads(PIN_PATH.read_text(encoding="utf-8"))


def load_chapters() -> list[Chapter]:
    pin = load_pin()
    chapters = []
    for name in pin["chapter_files"]:
        path = YAML_DIR / "input" / f"{name}.yaml"
        chapters.append(parse_chapter(load_yaml_file(path)))
    return chapters


def load_changelog_entries() -> list[str]:
    pin = load_pin()
    path = YAML_DIR / "changelogs" / f"{pin['version']}.yaml"
    return parse_changelog(load_yaml_file(path))


def load_nrdb() -> dict[str, str]:
    path = YAML_DIR / "nrdb.yaml"
    if not path.exists():
        return {}
    data = load_yaml_file(path) or {}
    return {str(k): str(v) for k, v in data.items()}


def build_document() -> dict[str, Any]:
    pin = load_pin()
    chapters = load_chapters()
    id_map = number_document(chapters)
    nrdb = load_nrdb()
    nodes: list[dict[str, Any]] = []
    tree: list[dict[str, Any]] = []
    for chapter in chapters:
        node = _chapter_node(chapter, id_map, nrdb, nodes)
        tree.append(_tree_copy(node))
    changelog = []
    for text in load_changelog_entries():
        rendered = parse_markup(text, id_map=id_map)
        _attach_card_codes(rendered.spans, nrdb)
        changelog.append(
            {
                "text_markup": text,
                "text_plain": rendered.plain,
                "spans": [span.to_dict() for span in rendered.spans],
            }
        )
    metadata = {
        "version": pin["version"],
        "effective_date": pin["effective_date"],
        "effective_date_display": pin["effective_date_display"],
        "source_repo": pin["source_repo"],
        "source_sha": pin["source_sha"],
        "published_url": pin["published_url"],
        "published_hub": pin["published_hub"],
        "node_count": len(nodes),
    }
    return {
        "metadata": metadata,
        "changelog": changelog,
        "tree": tree,
        "nodes": nodes,
        "id_map": id_map,
        "nrdb": nrdb,
    }


def _chapter_node(chapter: Chapter, id_map, nrdb, nodes) -> dict[str, Any]:
    child_ids = [section.id for section in chapter.sections]
    node = _base_node(
        ident=chapter.id,
        kind="chapter",
        id_map=id_map,
        parent_id=None,
        child_ids=child_ids,
        text_markup=chapter.text,
        title=chapter.text,
        is_new=chapter.new,
        toc=True,
        nrdb=nrdb,
        resolve_markup=False,
    )
    nodes.append(node)
    for section in chapter.sections:
        _section_node(section, chapter.id, id_map, nrdb, nodes)
    return node


def _section_node(section: Section, parent_id: str, id_map, nrdb, nodes) -> dict[str, Any]:
    child_ids: list[str] = []
    for element in section.elements:
        if isinstance(element, TimingStructure):
            child_ids.extend(el.id for el in element.elements if el.id)
        else:
            child_ids.append(element.id)
    node = _base_node(
        ident=section.id,
        kind="section",
        id_map=id_map,
        parent_id=parent_id,
        child_ids=child_ids,
        text_markup=section.text,
        title=_plain_title(section.toc_entry or section.text, id_map),
        is_new=section.new,
        toc=True,
        steps=section.steps,
        snippet_markup=section.snippet,
        nrdb=nrdb,
    )
    nodes.append(node)
    for element in section.elements:
        if isinstance(element, TimingStructure):
            for child in element.elements:
                _timing_node(child, section.id, id_map, nrdb, nodes)
        elif isinstance(element, SubSection):
            _subsection_node(element, section.id, id_map, nrdb, nodes)
        elif isinstance(element, Rule):
            _rule_node(element, section.id, "rule", id_map, nrdb, nodes)
    return node


def _subsection_node(subsection: SubSection, parent_id: str, id_map, nrdb, nodes) -> None:
    example_nodes = _example_child_ids(subsection.id, subsection.examples)
    child_ids = [rule.id for rule in subsection.rules] + [ex_id for ex_id, _ in example_nodes]
    node = _base_node(
        ident=subsection.id,
        kind="subsection",
        id_map=id_map,
        parent_id=parent_id,
        child_ids=child_ids,
        text_markup=subsection.text,
        title=_plain_title(subsection.text, id_map) if subsection.toc else None,
        is_new=subsection.new,
        toc=subsection.toc,
        steps=subsection.steps,
        snippet_markup=subsection.snippet,
        examples=_example_summaries(subsection.id, subsection.examples, id_map, nrdb),
        nrdb=nrdb,
    )
    nodes.append(node)
    for rule in subsection.rules:
        _rule_node(rule, subsection.id, "rule", id_map, nrdb, nodes)
    for ex_id, example in example_nodes:
        _example_node(ex_id, subsection.id, example, id_map, nrdb, nodes)


def _rule_node(rule: Rule, parent_id: str, kind: str, id_map, nrdb, nodes) -> None:
    example_nodes = _example_child_ids(rule.id, rule.examples)
    node = _base_node(
        ident=rule.id,
        kind=kind,
        id_map=id_map,
        parent_id=parent_id,
        child_ids=[ex_id for ex_id, _ in example_nodes],
        text_markup=rule.text,
        title=None,
        is_new=rule.new,
        toc=False,
        examples=_example_summaries(rule.id, rule.examples, id_map, nrdb),
        nrdb=nrdb,
    )
    nodes.append(node)
    for ex_id, example in example_nodes:
        _example_node(ex_id, rule.id, example, id_map, nrdb, nodes)


def _timing_node(element: TimingElement, parent_id: str, id_map, nrdb, nodes) -> None:
    assert element.id and element.number
    child_ids = [child.id for child in element.elements if child.id]
    node = _base_node(
        ident=element.id,
        kind="timing_structure",
        id_map=id_map,
        parent_id=parent_id,
        child_ids=child_ids,
        text_markup=element.text,
        title=None,
        is_new=element.new,
        toc=False,
        nrdb=nrdb,
    )
    nodes.append(node)
    for child in element.elements:
        _timing_node(child, element.id, id_map, nrdb, nodes)


def _example_node(ident: str, parent_id: str, example: Example, id_map, nrdb, nodes) -> None:
    parent_number = id_map[parent_id]["number"]
    index = ident.rsplit("_", 1)[-1]
    number = f"{parent_number}.ex{index}"
    id_map[ident] = {
        "id": ident,
        "number": number,
        "type": "example",
        "text": "",
        "toc": "false",
    }
    node = _base_node(
        ident=ident,
        kind="example",
        id_map=id_map,
        parent_id=parent_id,
        child_ids=[],
        text_markup=example.text,
        title=None,
        is_new=example.new,
        toc=False,
        nrdb=nrdb,
    )
    nodes.append(node)


def _example_child_ids(parent_id: str, examples: list[Example]) -> list[tuple[str, Example]]:
    return [(f"{parent_id}__example_{i}", example) for i, example in enumerate(examples, start=1)]


def _example_summaries(parent_id: str, examples: list[Example], id_map, nrdb) -> list[dict[str, Any]]:
    summaries = []
    for ident, example in _example_child_ids(parent_id, examples):
        rendered = parse_markup(example.text, id_map=id_map)
        _attach_card_codes(rendered.spans, nrdb)
        summaries.append(
            {
                "id": ident,
                "text_markup": example.text,
                "text_plain": rendered.plain,
                "is_new": example.new,
            }
        )
    return summaries


def _base_node(
    *,
    ident: str,
    kind: str,
    id_map,
    parent_id: str | None,
    child_ids: list[str],
    text_markup: str,
    title: str | None,
    is_new: bool,
    toc: bool,
    nrdb,
    steps: bool = False,
    snippet_markup: str | None = None,
    examples: list[dict[str, Any]] | None = None,
    resolve_markup: bool = True,
) -> dict[str, Any]:
    info = id_map[ident]
    if resolve_markup:
        rendered = parse_markup(text_markup, id_map=id_map)
        _attach_card_codes(rendered.spans, nrdb)
        plain = rendered.plain
        spans = [span.to_dict() for span in rendered.spans]
    else:
        plain = text_markup
        spans = []
    snippet_plain = None
    if snippet_markup is not None:
        snippet_rendered = parse_markup(snippet_markup, id_map=id_map)
        _attach_card_codes(snippet_rendered.spans, nrdb)
        snippet_plain = snippet_rendered.plain
    url = None
    if kind != "example":
        url = f"{PUBLISHED_BASE}?r={ident}"
    return {
        "id": ident,
        "kind": kind,
        "number": info["number"],
        "ref_type": info["type"],
        "title": title,
        "parent_id": parent_id,
        "child_ids": child_ids,
        "text_markup": text_markup,
        "text_plain": plain,
        "spans": spans,
        "examples": examples or [],
        "is_new": is_new,
        "toc": toc,
        "steps": steps,
        "snippet_markup": snippet_markup,
        "snippet_plain": snippet_plain,
        "url": url,
    }


def _plain_title(markup: str, id_map) -> str:
    return parse_markup(markup, id_map=id_map).plain


def _attach_card_codes(spans, nrdb: dict[str, str]) -> None:
    for span in spans:
        if span.type == "card" and span.target in nrdb:
            span.card_code = nrdb[span.target]


def _tree_copy(node: dict[str, Any]) -> dict[str, Any]:
    return dict(node)


def node_filename(number: str) -> str:
    safe = number.replace("/", "_")
    return f"{safe}.json"
