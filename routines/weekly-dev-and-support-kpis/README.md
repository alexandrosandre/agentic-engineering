# Weekly Dev & Support KPIs

Biweekly KPI report: pulls the dev team's and support's issue metrics from the GitHub API over the trailing two weeks and posts a formatted summary to the team chat.

| Field | Value |
| ----- | ----- |
| Platform / runner | Cloud agent automation |
| Schedule | Biweekly, Friday midday (weekly trigger, the prompt skips off-weeks) |
| Model tier | A fast model |
| Repo / branch | The monorepo / `master` |
| Outputs | One team-chat message in the engineering channel (`#eng`) |
| Tools | GitHub API (`GH_TOKEN`), team-chat post |
| Source | [PROMPT.md](PROMPT.md) (the platform's agent instructions, verbatim) |

## What it does

Every two weeks it queries the GitHub API for a Friday-to-Friday two-week window and reports:

- **Dev Team**: new P0 bugs (with a one-line pain, impact and status for each), fixed bugs, and total open bugs.
- **Support**: total open support issues and fixed support issues.

It formats these into a two-section report, includes the date range, omits how the numbers were obtained, and adds a qualitative conclusion only when one is relevant.

## Why it looks like this

The numbers are GitHub search queries, written out verbatim in the prompt, so the KPI definitions are versioned and reviewable rather than living in someone's head or in a dashboard nobody can diff. They lean on the labels the [issue-triage](../../ci-agents/issue-triage/) agent applies (`P0`, `Bug`, `Chore`, `Support`) and the `Stale` label of the [stale](../../ci-agents/stale/) workflow, and they count an issue closed as not planned as not fixed: the report is only as good as the triage. The model is a fast one because the work is counting and formatting; the one judgment call, summarizing each P0, is a sentence per issue.

## Schedule

The platform's trigger fires **weekly** on Friday, and the prompt **self-gates to biweekly**: a shell one-liner computes the day offset from an anchor Friday and the run stops unless it is a multiple of 14, so the model never does date arithmetic. A run on any other weekday computes a non-zero offset and stops, which matters because the report window is Friday to Friday.

## Installing it

Create a cloud agent automation with a weekly Friday trigger, `GH_TOKEN` in its environment, the team-chat integration, and [PROMPT.md](PROMPT.md) as its instructions. Set the anchor date placeholders to any Friday on the cadence you want, and adjust the label names to your own.

## Notes

Self-contained: it queries the GitHub API at runtime and references no committed repository files. Platform-side state is not versioned here.
