# agents-tests

The CI gate for the agent tooling itself: the scripts in [`tools/`](../../tools/), the CI sheriff's detector, and the scripts that skills carry. No model involved; this is what keeps the agents' own plumbing honest.

| | |
| --- | --- |
| Trigger | `pull_request` to `master`, only when the tooling, its tests or its dependencies change |
| Permissions | `contents: read` |
| Source | [`workflow.yml`](workflow.yml) |

## Why

Agent tooling is code that runs unattended, often with credentials, and is mostly edited by agents. It deserves the same gate as product code, and usually gets none, because it lives in a folder nobody thinks of as "the product". A transcript parser that silently drops user turns, or a web reader that stops refusing private addresses, fails quietly for weeks.

## Design choices

- **One job for every suite.** Setting up a job (checkout, Python, dependencies) costs about ten times the tests themselves, so splitting per tool would buy parallelism nobody needs at the price of minutes everybody waits.
- **Path-filtered and sparse.** It runs only on PRs that touch the tested code, its tests, or the lockfile, and checks out only those folders, so it finishes in well under its five-minute timeout.
- **PRs only.** A push to `master` would re-test code its PR already tested.
- **Pinned actions.** Third-party actions are pinned to a commit, like every workflow here.

## Wiring it up

A `pyproject.toml` whose dev dependency group carries the tools' third-party imports (`pytest`, `lxml`, `pypdf`), and the folder layout in the `paths:` and `sparse-checkout:` lists matched to yours. The issue agent's own suites run in its own repository, [alice-issue-agent](https://github.com/alexandrosandre/alice-issue-agent).
