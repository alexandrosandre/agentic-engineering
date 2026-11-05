# cicd-sheriff (skill)

**What.** The contract the CI/CD Sheriff's repair agent follows: read the README badge inventory with the detector, attribute each red `master` run before touching code, fix repository regressions in one focused PR (reusing an open one for the same root cause), re-run transient failures once instead of patching them, take the fix through `autoreview`, request the human reviewer, and hand off to the team chat through a file.

**Why.** A red pipeline invites speculative patches. The skill makes attribution the first step, keeps platform incidents and superseded runs out of the codebase, and leaves the merge with a person, so an agent repairing a broken pipeline cannot make it worse on its own judgment.

**How it fits.** Run by the repair job of the [CI/CD Sheriff workflow](../../README.md) on a schedule; usable by hand when a README-badge workflow is red. CI failures on your own PR belong to [`autoreview`](../../../../skills/autoreview/README.md) instead.

**Wire up.** Install it in your agent's skill folder as `cicd-sheriff`, with the detector at `ci/check_readme_workflows.py`, a `Sheriff` label, and the `CICD_SHERIFF_REVIEWER` and `CICD_SHERIFF_HANDOFF` variables the workflow sets.
