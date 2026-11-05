# github-rest

`rest.py`: the pull-request operations the delivery skills need ([`create-pr`](../../skills/create-pr/), [`autoreview`](../../skills/autoreview/), [`ship-it`](../../skills/ship-it/), `lgtm`), over GitHub's REST API, printing the same JSON shapes `gh pr view --json`, `gh pr checks` and `gh run list --json` print.

```
python3 tools/github-rest/rest.py pr-for-branch [branch]
python3 tools/github-rest/rest.py pr-view [number]
python3 tools/github-rest/rest.py pr-create --title-file T --body-file B [--base master]
python3 tools/github-rest/rest.py pr-edit N --title-file T --body-file B
python3 tools/github-rest/rest.py pr-ready|checks|runs|threads|comments|reviews [number]
python3 tools/github-rest/rest.py resolve-thread N ROOT_COMMENT_ID
python3 tools/github-rest/rest.py request-reviewers N login...
python3 tools/github-rest/rest.py pr-merge N HEAD_SHA
```

## Why

The same skills run in two places: a developer's laptop, where `gh` talks to GitHub directly, and Claude Code cloud sessions, which reach GitHub through Anthropic's git proxy. That proxy refuses GraphQL, so `gh pr ...` and `gh api graphql` fail there while plain REST works; it adds REST routes for the three operations GitHub only offers in GraphQL (review-thread state, resolving a thread, marking ready for review). Rather than teach every skill two code paths, this script picks the route and normalizes the output, so a skill reads `state: MERGED`, `mergeable: UNKNOWN` or a thread's `isResolved` the same way wherever it runs.

## Details worth keeping

- **Linked issues.** `linked_issue_numbers` is the one parser of the PR description convention (one `Fixes #N` or `Part of #N` line per issue). A line counts only when it declares the link, after an optional list marker, bold or colon; the same words inside a sentence, a quote or a parenthesis ("this does not fix #N") do not. The [issues-in-progress](../../ci-agents/issues-in-progress/) workflow reuses it.
- **Merges are pinned.** `pr-merge` sends the head SHA the caller checked, so GitHub refuses the merge if anything was pushed after the review. Only the `lgtm` skill runs it, on the developer's explicit go.
- **Thread IDs are never cached.** Resolving a thread looks up its GraphQL node at resolve time, since node IDs change as threads move.
- **The proxy's thread shape was probed, not documented.** The root comment is the listed comment that replies to nothing, because the order of `comment_ids` was never observed with replies; the tests cover a reply listed before its root.

## Wiring it up

`is_cloud_session` reads `CLAUDE_CODE_REMOTE`, which Claude Code sets in its cloud sessions, and `PROXY_ROUTE` is `ccr`, the path segment its proxy serves the extra routes under. If your cloud sessions reach GitHub directly, you only need the normalization, and every call can take the local path.

## Tests

`tests/` covers the normalization on synthetic payloads: merged state and mergeability, the linked-issue rule, check and run states, proxy and GraphQL threads giving identical output, root-comment detection, and remote URL parsing.
