---
name: fork
description: >-
  Create a new worktree of this repository from intent, with dependencies and environment
  set up, and open it in a new agent session. Use when starting isolated work from
  the main checkout or another worktree.
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---
# fork

## When to Use

- User wants to start work that should run in an isolated worktree.
- User asks for a new branch with deps + env preconfigured.
- Use **instead of** the editor's built-in worktree command or toggle — those create a bare worktree and skip the repository's worktree setup script (dependencies, env files, the virtualenv), so the agent there starts on a checkout that cannot run tests.

## Pre-flight

- The repository's worktree setup script must exist and be executable. If not, you're not in a checkout of this repository; ask the user to switch.
- If the user didn't provide intent (description of the work), ask them in one short question.

## Workflow

1. Pick 1–3 keywords from the intent. Lowercase, `[a-z0-9]`, 3–8 chars each, no stopwords. Join with `-`.

2. Run the worktree script with the assembled name, and stream its output:

   ```bash
   USER_SLUG=$(git config user.name | tr '[:upper:]' '[:lower:]' \
     | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g')
   <worktree-setup-script> -y --attach "${USER_SLUG}-$(date +%Y%m%d)-<keywords>"
   ```

3. The script opens the worktree where the user starts agent sessions (their editor or agent app). Tell the user — concisely:

   > Worktree ready on branch `<BRANCH>`. Open it from the project list and re-paste your intent into a fresh chat there.

   Do not continue acting on the user's request in this window — the work belongs in the new worktree.

## Branch name format

`<user-slug>-<YYYYMMDD>-<keywords>`, matching the `/checkout` start script and the interactive flow of the worktree script. Examples:

- `jdoe-20260418-fix-login-button`
- `jdoe-20260418-detail-pane`
- `jdoe-20260418-cli-perf`

If the assembled name collides with an existing branch, the script reuses it. Confirm with the user before re-running with different keywords.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `fork`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
