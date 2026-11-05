# Clean up stale feature flags

Weekly automation that removes graduated frontend feature flags whose gated path is now permanent, and opens a PR with the cleanup.

| Field | Value |
| ----- | ----- |
| Platform / runner | Cloud agent automation |
| Schedule | Weekly, Tuesday morning |
| Model tier | A coding-tuned frontier model, high effort |
| Repo / branch | The monorepo / `master` |
| Outputs | A PR for review by the frontend owner + a team-chat note, only when something changed |
| Tools | Open pull request, request reviewers |
| Source | [PROMPT.md](PROMPT.md) (the platform's agent instructions, verbatim) |

## What it does

Each week it scans the web app's custom in-repo feature-flag system for graduated flags (enabled in the global scope for at least a grace period after release, not in the "Do not cleanup" section, not disabled for any customer account) and removes them, so the enabled code path becomes unconditional. Its safety net is the TypeScript compiler plus a required repo-wide `rg '<flag>' web` sweep: the sweep catches the untyped hard-coded flag sets the compiler cannot see. It validates with `pnpm tsc --noEmit`, `pnpm lint` and `pnpm test --run`, and opens a focused PR through the [`create-pr`](../../skills/create-pr/) skill with the frontend owner as reviewer. It stays silent when nothing changed.

## Why

Feature flags are cheap to add and nobody's job to remove. Each one left behind doubles a code path, and after a few months the "disabled" branch is dead code that still has to compile, still confuses readers, and still gets edited by agents that cannot tell it is dead. Cleanup is exactly the kind of chore a routine does better than a person: mechanical, bounded, verifiable, and boring.

The prompt is long because it embeds the whole map of how flags work in this codebase (registry, defaults, evaluation order, every call-site pattern, the places the compiler cannot see). That map is the difference between an agent that removes a flag and an agent that removes a flag correctly: without it, an agent deletes the name from the typed registry, sees a green compile, and leaves it in the untyped sets, where it keeps a dead feature half-alive. The prompt therefore names every place the compiler cannot see and makes the text sweep a required gate, not a suggestion.

Opinions encoded in it:

- The enabled path must survive unchanged: the cleanup is a no-op for every user already seeing the feature.
- Low confidence means report, not edit: a candidate with blockers is a valid output.
- Operational toggles (reserved toggle prefixes, demo and freeze switches) are not rollouts and are never candidates, and the "Do not cleanup" list has one home, the defaults file, read fresh each run.

## Installing it

Create a cloud agent automation with a weekly trigger, permission to open PRs and request reviewers, the team-chat integration, and [PROMPT.md](PROMPT.md) as its instructions. Rewrite the "Background" section for your own flag system; that section is the part that does not transfer, and the part that matters most.

## Related files

The routine reads and edits the flag registry, the per-scope defaults and the evaluation helpers of the web app; the prompt names each one with a placeholder (`<flag-registry>`, `<flag-defaults>`, `<flag-helpers>`) to fill in for your codebase.
