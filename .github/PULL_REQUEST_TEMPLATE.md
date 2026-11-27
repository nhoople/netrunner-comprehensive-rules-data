## Summary

<!-- What changed and why (1–3 bullets). -->

## Proof

<!-- How the maintainer can see this working without reading code: a played match or the part of one this changes, a before-and-after screenshot or recording, or a test whose name states the behavior in plain words. Docs, tooling, or dependency-only PRs: `n/a — <reason>`. -->

## Review

<!-- For a code change: the `/code-review` level, what it found, and what was fixed or why not. Otherwise: `none — <reason>`. -->

## Found, not fixed

<!-- Each thing noticed that this PR does not change: what it is, where it went (issue, plan, or a fix-now session), and why. See "Findings" in https://github.com/nhoople/netrunner/blob/main/docs/how-we-work.md. Write `none` if nothing. -->

## Source and numbering

- [ ] Rule numbering and wording match the published Comprehensive Rules at [rules.nullsignal.games](https://rules.nullsignal.games/); where the YAML and the published document disagree, the published one wins
- [ ] `upstream/pin.json` names the ingested commit (if the source moved)

## Tests

- [ ] `python3 scripts/ingest.py && python3 scripts/transform.py`
- [ ] `python3 -m unittest discover -s tests` and `python3 scripts/validate.py` pass

## Release

- [ ] None: tooling, tests, or docs only
- [ ] New CR tag `<vYY.MM>`; consumers bump with the engine's [CR pin checklist](https://github.com/nhoople/netrunner-engine/blob/master/docs/cr-pin-bump-checklist.md), and the [pin table](https://github.com/nhoople/netrunner#readme) follows
