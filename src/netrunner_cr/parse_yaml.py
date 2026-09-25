from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union

import yaml


@dataclass
class Example:
    text: str
    new: bool = False


@dataclass
class TimingElement:
    text: str
    new: bool = False
    elements: list["TimingElement"] = field(default_factory=list)
    id: str | None = None
    number: str | None = None


@dataclass
class TimingStructure:
    bold: bool
    elements: list[TimingElement]


@dataclass
class Rule:
    id: str
    text: str
    new: bool = False
    examples: list[Example] = field(default_factory=list)
    kind: str = "rule"


@dataclass
class SubSection:
    id: str
    text: str
    new: bool = False
    toc: bool = False
    steps: bool = False
    snippet: str | None = None
    examples: list[Example] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)


@dataclass
class Section:
    id: str
    text: str
    new: bool = False
    toc_entry: str | None = None
    steps: bool = False
    snippet: str | None = None
    elements: list[Union[Rule, SubSection, TimingStructure]] = field(default_factory=list)


@dataclass
class Chapter:
    id: str
    text: str
    new: bool = False
    sections: list[Section] = field(default_factory=list)


def load_yaml_file(path) -> Any:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_chapter(data: dict[str, Any]) -> Chapter:
    return Chapter(
        id=_require_id(data, "chapter"),
        text=_str_field(data, "text"),
        new=_flag(data, "new"),
        sections=[parse_section(item) for item in data.get("sections") or []],
    )


def parse_section(data: dict[str, Any]) -> Section:
    return Section(
        id=_require_id(data, "section"),
        text=_str_field(data, "text"),
        new=_flag(data, "new"),
        toc_entry=data.get("toc_entry"),
        steps=_flag(data, "steps"),
        snippet=_optional_str(data, "snippet"),
        elements=[parse_section_element(item) for item in data.get("rules") or []],
    )


def parse_section_element(data: dict[str, Any]) -> Rule | SubSection | TimingStructure:
    if "timing_structure" in data:
        payload = data["timing_structure"]
        if isinstance(payload, dict) and ("elements" in payload or "bold" in payload):
            return parse_timing_structure(payload)
        return parse_timing_structure(data)
    if "subsection" in data:
        return parse_subsection(data)
    if "rule" in data:
        return parse_rule(data)
    raise ValueError(f"Expected rule, subsection, or timing_structure, got {list(data)}")


def parse_subsection(data: dict[str, Any]) -> SubSection:
    return SubSection(
        id=_require_id(data, "subsection"),
        text=_str_field(data, "text"),
        new=_flag(data, "new"),
        toc=_flag(data, "toc"),
        steps=_flag(data, "steps"),
        snippet=_optional_str(data, "snippet"),
        examples=[parse_example(item) for item in data.get("examples") or []],
        rules=[parse_rule(item, kind="rule") for item in data.get("rules") or []],
    )


def parse_rule(data: dict[str, Any], kind: str = "rule") -> Rule:
    return Rule(
        id=_require_id(data, "rule"),
        text=_str_field(data, "text"),
        new=_flag(data, "new"),
        examples=[parse_example(item) for item in data.get("examples") or []],
        kind=kind,
    )


def parse_example(data: dict[str, Any]) -> Example:
    return Example(text=_str_field(data, "text"), new=_flag(data, "new"))


def parse_timing_structure(data: dict[str, Any]) -> TimingStructure:
    if "timing_structure" in data and isinstance(data["timing_structure"], dict):
        data = {**data, **data["timing_structure"]}
    return TimingStructure(
        bold=_flag(data, "bold"),
        elements=[parse_timing_element(item) for item in data.get("elements") or []],
    )


def parse_timing_element(data: dict[str, Any]) -> TimingElement:
    return TimingElement(
        text=_str_field(data, "text"),
        new=_flag(data, "new"),
        elements=[parse_timing_element(item) for item in data.get("elements") or []],
    )


def parse_changelog(data: dict[str, Any]) -> list[str]:
    entries = []
    for item in data.get("changelog") or []:
        entries.append(_str_field(item, "text"))
    return entries


def _require_id(obj: dict[str, Any], key: str) -> str:
    if key not in obj or obj[key] is None or str(obj[key]).strip() == "":
        raise ValueError(f"Missing id field {key} in {list(obj)}")
    return str(obj[key])


def _str_field(obj: dict[str, Any], key: str) -> str:
    if key not in obj or not isinstance(obj[key], str):
        raise ValueError(f"Expected string field {key} in {list(obj)}")
    return obj[key].rstrip()


def _optional_str(obj: dict[str, Any], key: str) -> str | None:
    if key not in obj:
        return None
    value = obj[key]
    if not isinstance(value, str):
        raise ValueError(f"Expected string field {key}")
    return value.rstrip()


def _flag(obj: dict[str, Any], key: str) -> bool:
    return key in obj
