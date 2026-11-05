---
name: checkout
description: Start work on a new branch via the start script. Use when beginning new work from an issue, creating a feature branch, or setting up a new worktree.
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---
# Checkout (Start)

## When to Use
- Use when starting new work from an issue or keywords.
- Use to create a branch/worktree with the standard start script.

## Instructions
1. If the user did not provide branch keywords (2-3 words or issue_NUMBER), ask for them.
2. Run the repository's start script:
   ```bash
   <start-script> "<keywords>"
   ```
   The script forks from `origin/master` with `--no-track`, names the branch `<git-user>-<YYYYMMDD>-<keywords>`, and pushes it with its own upstream in one step. Use it rather than `git checkout -b`, which tracks whatever it forked from and skips the naming convention.
3. Verify the new branch:
   ```bash
   BRANCH_NAME=$(git branch --show-current)
   git config --get "branch.${BRANCH_NAME}.merge"
   ```
   - Expected output: `refs/heads/<branch-name>` (tracks its own remote).
   - **Forbidden** output: `refs/heads/master` (must never track master).

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `checkout`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
