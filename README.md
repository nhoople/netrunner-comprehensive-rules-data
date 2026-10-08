# Netrunner Comprehensive Rules data

Unofficial, machine-readable Comprehensive Rules (CR) for Netrunner, converted from the published Null Signal Games document.

This is a **consumer dataset**, in the same spirit as [netrunner-cards-json](https://github.com/Null-Signal-Games/netrunner-cards-json). It is not a rules website and not a PDF generator.

**Semantic authority:** the published CR at [rules.nullsignal.games](https://rules.nullsignal.games/) (currently v26.03, effective 2 March 2026).

**Machine pipeline:** YAML in [rubenpieters/netrunner-comprehensive-rules](https://github.com/rubenpieters/netrunner-comprehensive-rules), the public document generator used to produce that PDF/HTML. Ingest is pinned to a git SHA in [`source/pin.json`](source/pin.json). If YAML and the published document disagree, the published numbering and wording win and validation fails.

See [`NOTICE`](NOTICE) for affiliation and trademark notes. Toolchain code is MIT; rules text remains Null Signal Games reference material.

## Consume the data

Files under [`data/`](data/) are the API. Clone the repo or fetch raw GitHub URLs.

| File | Use |
| --- | --- |
| [`data/latest.json`](data/latest.json) | Full nested document plus changelog and metadata |
| [`data/nodes.json`](data/nodes.json) | Flat array of every node |
| [`data/nodes.jsonl`](data/nodes.jsonl) | One node per line (search, RAG, streaming) |
| [`data/index.json`](data/index.json) | TOC, `id → number`, `number → id` |
| [`data/refs.json`](data/refs.json) | Outgoing and incoming cross-references |
| [`data/cards.json`](data/cards.json) | Card-name mentions with NetrunnerDB codes |
| [`data/terms.json`](data/terms.json) | `{term:}` and `{subtype:}` mentions |
| [`data/changelog.json`](data/changelog.json) | v26.03 summary of changes |
| [`data/timing-structures.json`](data/timing-structures.json) | Appendix timing-structure steps |
| [`nodes/<number>.json`](nodes/) | One file per node for reviewable diffs |
| [`schemas/`](schemas/) | JSON Schema for nodes and the document |

Each node has a stable YAML `id` (the `?r=` deep link), a printed `number`, `text_markup`, resolved `text_plain`, and `spans`.

Example deep link: `https://rules.nullsignal.games/?r=rule_card_precedence` is node `1.2.1`.

Lettered subrules use the published citation form (`1.4.1a`), matching “rule 1.5.2b” in the CR changelog.

Symbols in `text_plain` follow the published plaintext replacements: `{c}`, `{click}`, `{MU}`, `{sub}`, `{trash}`, `{interrupt}`, `{link}`, `{recurring}`.

Version the dataset with git tags such as `v26.03`.

## Use in code

Python — load a rule by printed number:

```python
import json
from pathlib import Path

index = json.loads(Path("data/index.json").read_text())
nodes = {n["id"]: n for n in json.loads(Path("data/nodes.json").read_text())}

rule_id = index["numbers"]["1.2.1"]
print(nodes[rule_id]["text_plain"])
# If the text of a card directly contradicts these rules, the text of the card takes precedence.
```

JavaScript — fetch the flat node list from a tagged release:

```js
const base =
  "https://raw.githubusercontent.com/nhoople/netrunner-comprehensive-rules-data/v26.03/data";
const index = await fetch(`${base}/index.json`).then((r) => r.json());
const nodes = await fetch(`${base}/nodes.json`).then((r) => r.json());
const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
console.log(byId[index.numbers["1.2.1"]].text_plain);
```

Pin consumers to a tag (`v26.03`), not `master`, so a later CR update does not break you silently.

## Rebuild

Python 3.14+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/ingest.py          # fetch pinned YAML into source/yaml/
python3 scripts/transform.py       # emit data/ and nodes/
python3 scripts/validate.py        # schema, uniqueness, published headings
python3 -m unittest discover -s tests -v
```

`python3 scripts/validate.py --live` also checks that current HTML at rules.nullsignal.games still contains sampled rule ids.

This project is not associated with, produced by, or endorsed by Null Signal Games, Fantasy Flight Games, R. Talsorian Games, or Wizards of the Coast.
