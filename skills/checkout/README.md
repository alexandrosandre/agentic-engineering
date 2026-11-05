# checkout

**What.** Starts new work on a fresh branch through the repository's start script, then verifies the branch tracks itself and not the default branch.

**Why.** A branch created with a plain `git checkout -b` from `master` tracks `master`, and a later bare `git push` can land on the default branch. The start script forks from `origin/master` with `--no-track`, applies the naming convention (`<user>-<YYYYMMDD>-<keywords>`, with `-` never `/`, since deploy tooling derives resource names from it) and pushes with its own upstream in one step. The skill's verification makes "never track master" a check, not a hope.

**How it fits.** The usual first step of a session; `/fork` does the same in a separate worktree; `/prototype` reuses the start script without the question.

**Wire up.** A start script with that behavior; put its path in the skill.
