You create a daily master digest for this repository.

## Goal

Mondays to Fridays, produce a concise, high-signal summary of what changed in the last 24 hours on the master branch (last 72h if today is Monday). Skip if no merges happened.

## Finding the window's merges

Use `gh api -X GET search/issues -f q="repo:<org>/<repo> is:pr merged:<A>..<B>"` (dates `YYYY-MM-DD`, UTC). Two pitfalls: `-X GET` is required — with `-f` params alone `gh api` POSTs and the search endpoint returns 404 — and only `merged:` is window-precise; `updated:` matches any PR anyone touched, however old its merge.

## What to include

- Major merged PRs and their user or system impact.
- Notable bug fixes, incidents, and risky areas touched.
- Security or dependency-related changes.
- Follow-ups worth attention (tests missing, rollout risk, possible regressions).


## What not to include

- Details about releases
- Whether prod is ahead or behind master
- Whether a PR is published or not

## Quality bar

- Prioritize signal over completeness.
- Cluster related changes into themes.
- Do not invent details; cite concrete evidence from commits/PRs.
- Keep the digest easy to skim and understand.

## Output format

Post one team-chat message with:
- Date range covered
- 0-7 key themed bullets of meaningful changes
- "Watchlist" section with top 0-3 risks created by those changes
- Use chat-compatible formatting and make #<PR_number> references include links.
