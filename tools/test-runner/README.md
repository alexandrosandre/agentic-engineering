# test-runner

`test.sh`: run the checks CI would run, for only what this branch changed against `origin/master`, and stop at the first failure. It is what the [`test`](../../skills/test/) skill runs and re-runs while it fixes failures, and what [`contextual-review`](../../skills/contextual-review/) assumes already gated the diff (lint, type check, infrastructure lint, the suites).

## What it checks

| Changed | Check |
| --- | --- |
| A `.py` file in a Python package | `pylint` on the changed files only, then `pytest` on the whole package |
| An infrastructure-as-code template | The infrastructure linter on that template |
| A `.ts`/`.tsx` file in the web app | `pnpm lint`, `pnpm typecheck`, `pnpm test --run --maxWorkers=2` |

Nothing changed in those areas means nothing runs, and it says so.

## Why

An agent told to "run the tests" in a monorepo either runs everything (minutes of CPU on a laptop shared by several agent sessions, for a one-file change) or guesses which suite matters (and guesses wrong on the shared package everyone imports). A script that maps the diff to the checks CI would run removes both failure modes and gives the agent one command whose exit code is the answer. The opinions inside it:

- **Lint what changed, test what it belongs to.** Pylint on a whole package is slow and reports other people's debt; a test suite has to run whole, because a change in one module breaks a test of another.
- **Same checks as CI, earlier.** Each block mirrors a CI job, so a green run here predicts a green PR, and an agent does not learn about a type error from a review bot twenty minutes later.
- **Tests never reach a real account.** Fake cloud credentials and region are set for every Python check, so a module that builds a cloud client at import time imports cleanly and a test can never write anywhere.
- **Two workers for the web suite.** Several agent sessions often share one laptop; a test runner that forks a worker per core starves the others.
- **Fail fast.** It exits at the first failure; the `test` skill knows to re-run the whole script after its fixes, since later checks never ran and a fix can break an earlier one.

## Wiring it up

Set `PYTHON_PACKAGES`, `INFRA_TEMPLATES` and `INFRA_LINT` at the top to your layout and linter, and the web app's path and package scripts in the last block. It expects a root `.venv` and a `.pylintrc` at the repository root.
