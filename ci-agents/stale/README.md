# Close inactive issues and PRs

The stock `actions/stale` action, tuned for a repository where agents open a lot of issues and PRs. No model involved.

| | |
| --- | --- |
| Trigger | Daily cron |
| Permissions | `issues: write`, `pull-requests: write` |
| Source | [`workflow.yml`](workflow.yml) |

## What it does

- Issues: marked `Stale` after 90 days without activity, closed 7 days later unless someone comments.
- PRs: marked `Stale` after 45 days without activity, closed 7 days later. Branches are kept.

## Why it is here

Agents are prolific. An unattended issue agent, a CI sheriff, a cleanup routine and every developer's own sessions all open issues and PRs, and some of those are explorations nobody will come back to. Without a decay rule the backlog grows until nobody reads it, and the agents that sweep it (triage, the issue agent, the KPI report) work on noise. The thresholds encode an opinion: an issue nobody touched in a quarter is not a priority, and a PR nobody touched in six weeks needs a rebase more than a review. The `Stale` label is also the one the [KPI report](../../routines/weekly-dev-and-support-kpis/) excludes from "fixed" counts, so closing stale work never inflates the numbers.

## Wiring it up

Nothing beyond the default `GITHUB_TOKEN`. Adjust the thresholds and the messages to taste.
