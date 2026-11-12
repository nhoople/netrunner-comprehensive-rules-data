## Summary

<!-- What changed and why (1–3 bullets). -->

## Source and numbering

- [ ] Rule numbering and wording match the published Comprehensive Rules at [rules.nullsignal.games](https://rules.nullsignal.games/); where the YAML and the published document disagree, the published one wins
- [ ] `source/pin.json` names the ingested commit (if the source moved)

## Tests

- [ ] `python3 scripts/ingest.py && python3 scripts/transform.py`
- [ ] `python3 -m unittest discover -s tests` and `python3 scripts/validate.py` pass

## Release

- [ ] None: tooling, tests, or docs only
- [ ] New CR tag `<vYY.MM>`; consumers bump with the engine's [CR pin checklist](https://github.com/nhoople/netrunner-engine/blob/master/docs/cr-pin-bump-checklist.md), and the [pin table](https://github.com/nhoople/netrunner#readme) follows
