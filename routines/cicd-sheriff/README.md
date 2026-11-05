# Scheduled CI/CD Sheriff

Scheduled watchdog for the GitHub Actions status badges displayed at the top of the repository README.

| Field | Value |
| --- | --- |
| Platform / runner | GitHub Actions (cron) |
| Schedule | Cron `0 7,11,15 * * 1-5`: three times each weekday (morning, midday, afternoon in the team's time zone) |
| Model tier | The strongest available model, highest effort |
| Repo / branch | The monorepo / `master` |
| Outputs | A fix PR, and one team-chat handoff only after intervention or a human-only blocker |
| Tools | GitHub token, Claude Code's GitHub Action, the team-chat API (deterministic step only) |
| Source | [`ci-agents/cicd-sheriff/workflow.yml`](../../ci-agents/cicd-sheriff/workflow.yml) |

## What it does

Each run reads the monitored workflow inventory from `README.md` through [`check_readme_workflows.py`](../../ci-agents/cicd-sheriff/check_readme_workflows.py). An all-green run is silent. A red run invokes the [`cicd-sheriff`](../../ci-agents/cicd-sheriff/skills/cicd-sheriff/SKILL.md) skill through Claude Code's GitHub Action: it tells repository regressions from GitHub or runner failures, reuses existing work for the same root cause, prepares a focused fix, runs [`autoreview`](../../skills/autoreview/), requests the designated human reviewer, and leaves merge authority with a human.

This routine is the scheduled half of the [CI/CD Sheriff CI agent](../../ci-agents/cicd-sheriff/); that README carries the design, the alternatives and the dragons.

## Trigger and self-test

The workflow runs three times each weekday and supports manual dispatch. Manual runs default to detection only; `repair: true` enables repair only when dispatched from `master`. Pull requests touching the workflow, checker, skill, prompt or README run the detector and its contract tests without repair or notification permissions.

## Prompt

See [`PROMPT.md`](PROMPT.md), loaded verbatim by the workflow's repair job. The prompt is committed rather than inlined in the YAML so the routine registry and the workflow share one source.

## Notes

The repair job authenticates the agent with a repository secret (`CLAUDE_CODE_OAUTH_TOKEN`). After the repair agent exits, a deterministic step reads the team-chat token and posts the handoff; no chat credential reaches the repair agent. Because the watchdog shares GitHub Actions' failure domain, it cannot report during an Actions outage; the next successful scheduled run diagnoses any badge left red after recovery.
