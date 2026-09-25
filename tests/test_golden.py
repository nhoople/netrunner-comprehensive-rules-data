from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netrunner_cr import YAML_DIR
from netrunner_cr.build import build_document
from netrunner_cr.parse_yaml import load_yaml_file, parse_chapter
from netrunner_cr.numbering import number_document


class GoldenChapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = YAML_DIR / "input" / "01_game_concepts.yaml"
        if not path.exists():
            raise unittest.SkipTest("YAML not ingested; run scripts/ingest.py")
        cls.chapter = parse_chapter(load_yaml_file(path))
        cls.id_map = number_document([cls.chapter])

    def test_card_precedence_is_1_2_1(self) -> None:
        self.assertEqual(self.id_map["rule_card_precedence"]["number"], "1.2.1")

    def test_gateway_identities_is_lettered_subrule(self) -> None:
        self.assertEqual(self.id_map["rule_gateway_identities"]["number"], "1.4.1a")

    def test_chapter_and_section_numbers(self) -> None:
        self.assertEqual(self.id_map["chpt_game_concepts"]["number"], "1")
        self.assertEqual(self.id_map["sec_golden_rules"]["number"], "1.2")
        self.assertEqual(self.id_map["sec_deck_construction"]["number"], "1.4")


class BuiltDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not (YAML_DIR / "input" / "01_game_concepts.yaml").exists():
            raise unittest.SkipTest("YAML not ingested; run scripts/ingest.py")
        cls.document = build_document()
        cls.by_id = {node["id"]: node for node in cls.document["nodes"]}

    def test_plaintext_resolves_refs_and_symbols(self) -> None:
        node = self.by_id["rule_symbol_credits"]
        self.assertIn("{c}", node["text_plain"])
        self.assertIn("section 1.10", node["text_plain"])

    def test_url_uses_published_deep_link(self) -> None:
        node = self.by_id["rule_card_precedence"]
        self.assertEqual(
            node["url"],
            "https://rules.nullsignal.games/?r=rule_card_precedence",
        )

    def test_appendix_timing_ids(self) -> None:
        self.assertIn("11.2_1", {node["number"] for node in self.document["nodes"]})


if __name__ == "__main__":
    unittest.main()
