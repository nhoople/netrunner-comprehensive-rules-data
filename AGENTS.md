# Agent notes

This is the Comprehensive Rules dataset of the Netrunner project. Full instructions for coding agents are in the project repo's [`CLAUDE.md`](https://github.com/nhoople/netrunner/blob/main/CLAUDE.md), and the git and release process is in [`docs/git-hygiene.md`](https://github.com/nhoople/netrunner/blob/main/docs/git-hygiene.md).

- The four repositories stay separate: `netrunner-engine`, `netrunner-cards-data`, `netrunner-comprehensive-rules-data`, and `netrunner-game`. The game and the engine consume the others by release tag, not by `master` and not as workspace packages. Do not recommend merging them, an npm workspace, or Turborepo unless asked to change that release model.
- The published Comprehensive Rules win over the YAML source when they disagree. Consumers pin a release tag.
- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Before committing, add or update a test for the behavior and run `.venv/bin/python scripts/ingest.py && .venv/bin/python scripts/transform.py && .venv/bin/python -m unittest discover -s tests && .venv/bin/python scripts/validate.py` (the CI `transform-validate` job).
- Work on a `claude/<descriptive-name>` branch and merge by pull request; `master` takes no direct push.
