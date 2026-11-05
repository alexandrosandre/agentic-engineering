---
name: yolo
description: >-
  Use when the user wants an immediate self-merge with zero review and zero
  waiting — commit, PR, then squash-merge without watching CI/CD or review
  comments. Only for low-risk changes the user already understands well.
compatibility: Requires gh CLI authenticated to GitHub.
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---
# yolo

Skip code review entirely: no local code review, /autoreview, or /contextual-review, and don't address findings from the review-bot checks listed in /autoreview's "Review Bot Checks" section. Don't wait for CI/CD either — no polling, no fixing failures; whatever happens on the branch after the merge is the user's problem.

## Steps

1. Commit and push all pending changes on this branch (not only this conversation's).
2. /create-pr — it opens the PR, or refreshes the title/description in place if one is already open (so a stale, early-opened description is corrected here). Mark the PR ready if it is a draft.
3. Merge immediately: resolve any open review threads without addressing them (branch protection requires it, and the /yolo invocation is the authority to dismiss them), then `gh pr merge <PR> --squash` (the only allowed merge method; when no required status checks exist, it lands without waiting). No `--admin` — if the merge is still rejected, stop and report.

Report the PR number and the merge result.

## Notes

- The /yolo invocation itself is the explicit per-PR merge approval.
- To wait for green CI and triage review findings before merging, use /lgtm; for review without merging, /ship-it or /ship-it-lite.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `yolo`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
