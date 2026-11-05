# Daily Eng Digest

Daily engineering digest of what merged in the last 24 hours (72 on Mondays), posted to the team chat.

| Field | Value |
| ----- | ----- |
| Platform / runner | Cloud agent automation |
| Schedule | Cron `0 8 * * 1-5`: Monday to Friday, start of the workday |
| Model tier | A frontier model, high effort |
| Repo / branch | The monorepo / `master` |
| Outputs | One team-chat message in the engineering channel (`#eng`) |
| Tools | GitHub read access, team-chat post |
| Source | [PROMPT.md](PROMPT.md) (the platform's agent instructions, verbatim) |

## What it does

Monday to Friday, it summarizes the window's merged changes into a single high-signal message: themed bullets of meaningful changes plus a short "Watchlist" of the risks those changes create. It skips days with no merges, prioritizes signal over completeness, and cites concrete PRs and commits rather than inventing detail.

## Why

With several developers and several agents merging every day, nobody reads every PR. The digest is the one place a developer catches up in a minute, and its Watchlist is the part that earns its keep: a merge that touched a risky area without tests, a rollout that needs watching. The prompt is short on purpose; most of its length is the two GitHub search pitfalls the routine actually hit (a `gh api` call that silently POSTs, and `updated:` matching old PRs), recorded so it does not hit them again.

A routine like this is also the natural place to surface any quality signal the team tracks over time (an eval pass rate, a latency percentile). If you add one, reconstruct its baseline from durable artifacts (workflow artifacts, a results table) on every run instead of relying on the platform's memory feature: a baseline kept in platform state cannot be reviewed, diffed or recovered.

## Installing it

Create a cloud agent automation on the monorepo's `master`, with the cron above, the team-chat integration, and [PROMPT.md](PROMPT.md) as its instructions. Replace `<org>/<repo>` in the prompt. The trigger lives in the platform, not the repository; the cron above is the versioned record.

## Notes

Platform-side state (run history) is not versioned here, only the definition (this README plus [PROMPT.md](PROMPT.md)).
