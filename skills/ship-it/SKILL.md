---
name: ship-it
description: >-
  Use when finished work should be taken all the way to a fully reviewed,
  merge-ready PR in one pass. Does not merge; the author keeps merge authority
  (see /lgtm or /yolo to merge).
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---
# ship-it

Run through the steps below and finish them. Defer anything needing human confirmation to the final summary.

Fix review findings that are confirmed bugs, regressions, unfulfilled task intent, or AGENTS.md violations in the changed code, and the same mistake wherever else the change repeats it — the bots flag each copy on a later round. Leave nits, refactor preferences, and opportunistic improvements for the final summary; when in doubt, leave it.

At the end, summarize how far you got, the pending user decisions, and the findings you skipped. Surface unaddressed /contextual-review Blockers prominently at the top — never fold them into a generic "merge-ready" claim.

## Steps

1. Review the changes the review bots have not seen yet with the coding agent's built-in code review at its highest effort level (for example a `/code-review` command set to its top effort); skip this when there are none. With no target it reviews unpushed commits plus uncommitted edits; while the branch has no PR or the PR is a draft the bots have seen nothing, so fetch `origin/master` and pass it as the target to review the whole branch (local `master` is usually stale here). No auto-fix; its findings get triaged against the bar above. Match the effort level the CI reviewer bot runs at, so this pass reasons as deeply. Run it from a foreground general-purpose subagent that invokes the review command with this step's arguments and returns every finding; why is in /autoreview Step 5. Where the agent has no subagents, invoke the command directly; where it has no such command, review the diff yourself at that depth.
2. Commit and push all pending changes on this branch (not only this conversation's). Before pushing, fetch and merge the base branch (the open PR's base, else `origin/master`), so this push carries it and no merge-only push follows it from /create-pr or /autoreview's Startup. If it conflicts, `git merge --abort` and push without it; /create-pr in step 3 then stops on the conflict and reports it.
3. /create-pr — it opens the PR, or refreshes the title/description in place if one is already open.
4. /autoreview
5. /contextual-review, its findings triaged against the bar above instead of its confirmation gate. When it calls for fixes, make them, then repeat steps 1, 2 and 4 for them.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `ship-it`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
