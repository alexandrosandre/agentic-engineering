# test

**What.** A test-fix loop: run the repository's test runner, fix each failure, re-run only what failed, then run the whole runner once more and stop.

**Why.** Two failure modes of agents running tests: re-running the whole suite after every one-line fix (slow, and on a shared laptop it starves other sessions), and looping forever on a failure the code cannot fix. The loop re-runs narrowly, does one final full pass because the runner exits at the first failure and a fix can break an earlier check, and reports environment problems, flaky tests and failures already on the base branch instead of looping on them. CI runs the full suites anyway.

**How it fits.** Used before `/create-pr`, inside `/autoreview` for branch-caused CI failures, and on request.

**Wire up.** A test runner script that runs, for each package the branch modified, what the CI gate runs (lint, types, tests); this repository ships one in `tools/test-runner/`. Point the skill at yours.
