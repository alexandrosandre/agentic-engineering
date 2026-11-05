# Public API Doc Sync

An agent that keeps the public API's OpenAPI (Swagger) document in step with the code, inside the PR that changes the API.

| | |
| --- | --- |
| Trigger | `pull_request` (opened, synchronize, ready for review, reopened) on `master` or `release/*`, only when the public API handlers, the spec or the public API test change; skipped for drafts |
| Permissions | `contents: write`, `pull-requests: write` |
| Model tier | A mid-tier model |
| Source | [`workflow.yml`](workflow.yml) |

## What it does

When a ready PR touches the public API surface, the agent reads the diff and decides whether the interface changed (endpoints, parameters, auth, request or response schema, status codes, examples, versioned behavior). If it did, it updates the spec to match, bumps `info.version` by semantic versioning (major for breaking, minor for additive, patch for fixes), commits the spec to the PR branch, and leaves one sticky comment listing the changed endpoints and any manual publishing step. If it did not, it does nothing and says nothing.

## Why

Public API docs drift because the person changing a handler is not thinking about the spec, and the reviewer is reading the handler. Putting the sync inside the PR means the spec change is reviewed together with the code change that caused it, by the same reviewer, before merge. Silence on no-change PRs keeps the agent from becoming a comment every PR has to scroll past.

## Guardrails

- Path filters, plus a draft skip, keep it from running on PRs that cannot change the public API, or that are not ready for review.
- The tool allowlist allows file edits, the `git` subcommands that read the diff and commit and push the spec (`status`, `diff`, `log`, `add`, `commit`, `push`), and three read-or-comment `gh pr` subcommands, nothing else.
- Project MCP servers are not started: the action restores the repository's MCP config from the base branch, but the servers it names run commands from repository paths, which on a PR job means the PR's own files with the job's tokens.
- The prompt states its success criteria, including the negative ones ("no unnecessary changes or commits", "if no API change, no comment is posted").

## Wiring it up

Repository secret `CLAUDE_CODE_OAUTH_TOKEN`, and the three paths in the prompt and the `paths:` filter pointed at your handlers, spec and public API test.
