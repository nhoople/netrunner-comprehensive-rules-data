from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netrunner_cr.numbering import number_document
from netrunner_cr.parse_yaml import parse_chapter


SAMPLE = """
chapter: chpt_game_concepts
text: Game Concepts
sections:
- section: sec_golden_rules
  text: Golden Rules
  rules:
  - rule: rule_card_precedence
    text: If the text of a card directly contradicts these rules, the text of the card takes precedence.
- section: sec_deck_construction
  text: Deck Construction
  rules:
  - subsection: rule_identity
    text: Each player's deck is associated with a single identity card.
    rules:
    - rule: rule_gateway_identities
      text: The identities {card:The Catalyst} and {card:The Syndicate} are starter-only.
"""


class NumberingTests(unittest.TestCase):
    def test_published_numbers_for_golden_rules(self) -> None:
        import yaml

        chapter = parse_chapter(yaml.safe_load(SAMPLE))
        id_map = number_document([chapter])
        self.assertEqual(id_map["chpt_game_concepts"]["number"], "1")
        self.assertEqual(id_map["sec_golden_rules"]["number"], "1.1")
        self.assertEqual(id_map["rule_card_precedence"]["number"], "1.1.1")
        self.assertEqual(id_map["rule_identity"]["number"], "1.2.1")
        self.assertEqual(id_map["rule_gateway_identities"]["number"], "1.2.1a")


if __name__ == "__main__":
    unittest.main()
