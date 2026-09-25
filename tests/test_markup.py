from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from netrunner_cr.markup import parse_markup


class MarkupTests(unittest.TestCase):
    def test_symbols_use_published_plaintext(self) -> None:
        rendered = parse_markup("Pay 1[c] and spend [click].")
        self.assertEqual(rendered.plain, "Pay 1{c} and spend {click}.")
        types = [span.type for span in rendered.spans]
        self.assertEqual(types, ["symbol", "symbol"])

    def test_ref_expands_with_id_map(self) -> None:
        id_map = {"sec_credits": {"number": "1.10", "type": "section"}}
        rendered = parse_markup("See {ref:sec_credits}.", id_map=id_map)
        self.assertEqual(rendered.plain, "See section 1.10.")
        self.assertEqual(rendered.spans[0].ids, ["sec_credits"])

    def test_capitalized_ref(self) -> None:
        id_map = {"sec_clicks": {"number": "1.11", "type": "section"}}
        rendered = parse_markup("{ref:Sec_clicks}", id_map=id_map)
        self.assertEqual(rendered.plain, "Section 1.11")

    def test_card_term_subtype_and_new(self) -> None:
        rendered = parse_markup(
            "{n}Play {card:Diesel} as a {subtype:event} to gain {term:credits}.{/n}"
        )
        self.assertEqual(rendered.plain, "Play Diesel as a event to gain credits.")
        kinds = {span.type for span in rendered.spans}
        self.assertEqual(kinds, {"new", "card", "subtype", "term"})


if __name__ == "__main__":
    unittest.main()
