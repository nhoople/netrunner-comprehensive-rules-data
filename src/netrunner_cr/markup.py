from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Span:
    type: str
    start: int
    end: int
    target: str | None = None
    ids: list[str] = field(default_factory=list)
    card_code: str | None = None
    href: str | None = None
    combiner: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "type": self.type,
            "start": self.start,
            "end": self.end,
        }
        if self.target is not None:
            data["target"] = self.target
        if self.ids:
            data["ids"] = self.ids
        if self.card_code is not None:
            data["card_code"] = self.card_code
        if self.href is not None:
            data["href"] = self.href
        if self.combiner is not None:
            data["combiner"] = self.combiner
        return data


@dataclass
class RenderedText:
    plain: str
    spans: list[Span]


def parse_markup(text: str, *, id_map: dict[str, dict[str, str]] | None = None) -> RenderedText:
    """Render YAML formatted text to plaintext plus spans.

    Symbol tokens such as ``[c]`` become ``{c}``. Cross-references are expanded
    using ``id_map`` entries ``{id: {number, type}}`` when available.
    """
    prepared = _replace_symbols(text)
    parts = _split_curly(prepared)
    plain_parts: list[str]
    spans: list[Span]
    plain_parts = []
    spans = []
    cursor = 0
    new_start: int | None = None

    for kind, payload in parts:
        if kind == "text":
            plain_parts.append(payload)
            cursor += len(payload)
            continue
        if payload == "n":
            new_start = cursor
            continue
        if payload == "/n":
            if new_start is not None:
                spans.append(Span(type="new", start=new_start, end=cursor))
                new_start = None
            continue

        rendered, span = _render_token(payload, cursor, id_map)
        plain_parts.append(rendered)
        if span is not None:
            span.end = cursor + len(rendered)
            spans.append(span)
        cursor += len(rendered)

    return RenderedText("".join(plain_parts), spans)


def _replace_symbols(text: str) -> str:
    from . import SYMBOL_FROM_BRACKET

    out = text
    for token, name in SYMBOL_FROM_BRACKET.items():
        out = out.replace(token, f"{{img:{name}}}")
    return out


def _split_curly(text: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    buf: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "{":
            if buf:
                parts.append(("text", "".join(buf)))
                buf = []
            end = text.find("}", i + 1)
            if end == -1:
                buf.append(text[i:])
                break
            parts.append(("token", text[i + 1 : end]))
            i = end + 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        parts.append(("text", "".join(buf)))
    return parts


def _render_token(
    payload: str,
    start: int,
    id_map: dict[str, dict[str, str]] | None,
) -> tuple[str, Span | None]:
    from . import SYMBOL_PLAIN

    if payload.startswith("img:"):
        name = payload[4:]
        plain = SYMBOL_PLAIN.get(name, f"{{{name}}}")
        return plain, Span(type="symbol", start=start, end=start, target=name)
    if payload.startswith("curly:"):
        inner = payload[6:]
        plain = f"{{{inner}}}"
        return plain, Span(type="symbol", start=start, end=start, target=inner)
    if payload.startswith("term:"):
        value = payload[5:]
        return value, Span(type="term", start=start, end=start, target=value)
    if payload.startswith("subtype:"):
        value = payload[8:]
        return value, Span(type="subtype", start=start, end=start, target=value)
    if payload.startswith("card:"):
        value = payload[5:]
        return value, Span(type="card", start=start, end=start, target=value)
    if payload.startswith("product:"):
        value = payload[8:]
        return value, Span(type="product", start=start, end=start, target=value)
    if payload.startswith("link:"):
        rest = payload[5:]
        if "|" in rest:
            label, href = rest.split("|", 1)
        else:
            label, href = rest, rest
        return label, Span(type="link", start=start, end=start, target=label, href=href)
    if payload.startswith("ref:") or payload.startswith("ref/"):
        return _render_ref(payload, start, id_map)
    return payload, None


def _render_ref(
    payload: str,
    start: int,
    id_map: dict[str, dict[str, str]] | None,
) -> tuple[str, Span | None]:
    combiner = "and"
    if payload.startswith("ref/"):
        rest = payload[4:]
        combiner, ids_blob = rest.split(":", 1)
    else:
        ids_blob = payload[4:]
    capitalize = bool(ids_blob) and ids_blob[0].isupper()
    ids = [part.strip().lower() for part in ids_blob.split(",") if part.strip()]
    label = _ref_label(ids, capitalize, combiner, id_map)
    return label, Span(type="ref", start=start, end=start, ids=ids, combiner=combiner)


def _ref_label(
    ids: list[str],
    capitalize: bool,
    combiner: str,
    id_map: dict[str, dict[str, str]] | None,
) -> str:
    if not ids:
        return "rule"
    first = (id_map or {}).get(ids[0], {})
    kind = first.get("type", "rule")
    word = kind
    if capitalize:
        word = word[:1].upper() + word[1:]
    numbers = []
    for rid in ids:
        info = (id_map or {}).get(rid)
        numbers.append(info["number"] if info else rid)
    if len(numbers) == 1:
        return f"{word} {numbers[0]}"
    if len(numbers) == 2:
        return f"{word}s {numbers[0]} {combiner} {numbers[1]}"
    joined = ", ".join(numbers[:-1]) + f" {combiner} {numbers[-1]}"
    return f"{word}s {joined}"
