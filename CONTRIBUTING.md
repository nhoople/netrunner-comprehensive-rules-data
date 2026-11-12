# Contributing

This repository converts the published Null Signal Games Comprehensive Rules into JSON. It is part of [nhoople/netrunner](https://github.com/nhoople/netrunner); the git and release process is in that repo's [`docs/git-hygiene.md`](https://github.com/nhoople/netrunner/blob/main/docs/git-hygiene.md).

- **Authority:** the published document at [rules.nullsignal.games](https://rules.nullsignal.games/). The YAML source is pinned in [`source/pin.json`](source/pin.json); when it disagrees with the published numbering or wording, validation fails and the published version wins.
- **Setup:** `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- **Before a pull request:** `python3 scripts/ingest.py && python3 scripts/transform.py`, then `python3 -m unittest discover -s tests` and `python3 scripts/validate.py`. CI runs the same steps as `transform-validate`.
- **Releases:** tag a new CR version (`vYY.MM`) only when Null Signal Games publishes one. Consumers move with the engine's [CR pin checklist](https://github.com/nhoople/netrunner-engine/blob/master/docs/cr-pin-bump-checklist.md).
