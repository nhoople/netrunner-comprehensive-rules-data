from __future__ import annotations

from . import LETTERS, ROMAN
from .parse_yaml import Chapter, Rule, Section, SubSection, TimingStructure

# DocumentLike is chapters list; keep numbering independent of a Document class.


class DuplicateIdError(ValueError):
    pass


def number_document(chapters: list[Chapter]) -> dict[str, dict[str, str]]:
    """Assign printed numbers matching the official YAML document generator."""
    id_map: dict[str, dict[str, str]] = {}
    for chapter_index, chapter in enumerate(chapters, start=1):
        _add(id_map, chapter.id, str(chapter_index), "section", chapter.text, toc=True)
        for section_index, section in enumerate(chapter.sections, start=1):
            _number_section(id_map, section, chapter_index, section_index)
    return id_map


def _number_section(id_map, section: Section, chapter_index: int, section_index: int) -> None:
    number = f"{chapter_index}.{section_index}"
    title = section.toc_entry or section.text
    _add(id_map, section.id, number, "section", title, toc=True)
    sub_ref_type = "step" if section.steps else "rule"
    for i, element in enumerate(section.elements):
        if isinstance(element, TimingStructure):
            _assign_timing_ids(element, id_map, section.id, number)
            continue
        _number_section_element(id_map, element, chapter_index, section_index, i + 1, sub_ref_type)


def _number_section_element(id_map, element, chapter_index, section_index, subsection_index, ref_type) -> None:
    number = f"{chapter_index}.{section_index}.{subsection_index}"
    if isinstance(element, SubSection):
        kind = "step" if element.steps else "section"
        _add(id_map, element.id, number, kind, element.text if element.toc else "", toc=element.toc)
        child_type = "step" if element.steps else "rule"
        for i, rule in enumerate(element.rules):
            _number_subrule(id_map, rule, chapter_index, section_index, subsection_index, i, child_type)
        return
    if isinstance(element, Rule):
        _add(id_map, element.id, number, ref_type, "", toc=False)


def _number_subrule(id_map, rule: Rule, chapter_index, section_index, subsection_index, subrule_index, ref_type) -> None:
    if subrule_index >= len(LETTERS):
        raise ValueError(f"Too many lettered subrules under {chapter_index}.{section_index}.{subsection_index}")
    number = f"{chapter_index}.{section_index}.{subsection_index}{LETTERS[subrule_index]}"
    _add(id_map, rule.id, number, ref_type, "", toc=False)


def _assign_timing_ids(ts: TimingStructure, id_map, section_id: str, base_nr: str) -> None:
    for i, l1 in enumerate(ts.elements):
        l1_id = f"{section_id}_{i + 1}"
        l1_nr = f"{base_nr}_{i + 1}"
        l1.id = l1_id
        l1.number = l1_nr
        _add(id_map, l1_id, l1_nr, "appendix", "", toc=False)
        for j, l2 in enumerate(l1.elements):
            if j >= len(LETTERS):
                raise ValueError(f"Too many timing L2 elements under {l1_id}")
            letter = LETTERS[j]
            l2_id = f"{l1_id}_{letter}"
            l2_nr = f"{l1_nr}_{letter}"
            l2.id = l2_id
            l2.number = l2_nr
            _add(id_map, l2_id, l2_nr, "appendix", "", toc=False)
            for k, l3 in enumerate(l2.elements):
                if k >= len(ROMAN):
                    raise ValueError(f"Too many timing L3 elements under {l2_id}")
                roman = ROMAN[k]
                l3_id = f"{l2_id}_{roman}"
                l3_nr = f"{l2_nr}_{roman}"
                l3.id = l3_id
                l3.number = l3_nr
                _add(id_map, l3_id, l3_nr, "appendix", "", toc=False)


def _add(id_map, ident: str, number: str, ref_type: str, text: str, *, toc: bool) -> None:
    if ident in id_map:
        raise DuplicateIdError(f"id defined twice: {ident}")
    id_map[ident] = {
        "id": ident,
        "number": number,
        "type": ref_type,
        "text": text,
        "toc": "true" if toc else "false",
    }
