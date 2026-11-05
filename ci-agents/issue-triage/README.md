# Issue Triage

An agent that labels, assigns and files every new issue the moment it is opened, so no issue sits unowned and every report the team runs on GitHub labels is counting triaged issues.

| | |
| --- | --- |
| Trigger | `issues: opened` |
| Permissions | `issues: write`, `repository-projects: write`, `contents: read` |
| Model tier | A fast model |
| Source | [`workflow.yml`](workflow.yml) |

## What it does

On each new issue it applies exactly one Scope label and one Type label (plus Priority only when clearly justified), assigns owners by scope, adds the issue to the right project board (Support, Product or Engineering) with a status, and stops. A last deterministic step can hand the issue to an unattended issue agent.

## Why it looks like this

- **The prompt is the triage policy.** Label meanings, the assignment table, the project rules and their precedence are all in one versioned prompt, reviewed in PRs like code. When the team's conventions change, the PR that changes them changes the triage.
- **Untrusted input is fenced.** The issue title and body are pasted inside an explicit "untrusted, for analysis only" envelope, and the prompt says never to follow instructions found there.
- **The tool allowlist is the real guardrail.** The agent can run `gh issue`, `gh label` and `gh project`, and nothing else: no file edits, no other shell, no other GitHub writes. A prompt injection that convinces the model still has nowhere to go.
- **A sparse checkout keeps the repository's rules out.** The job checks out only the folder its last step needs, so the triage agent does not load `AGENTS.md`. Triage needs the label rules, not the engineering rules, and a smaller context is a more obedient one.
- **Labels the agent must never touch are named.** `skip-alice`, `Sheriff` and the issue agent's account are reserved for people and for fixed steps; the prompt says so explicitly, because a model asked to "pick labels" will otherwise pick those too.
- **Assignment to the issue agent is a deterministic step, not the model's call.** It runs after the triage agent with the workflow's own token, behind two repository variables (its own switch and the issue agent's sweep switch), so nothing is assigned to the agent while nothing would start it. The issue agent, its sweep and the assignment script live in [alice-issue-agent](https://github.com/alexandrosandre/alice-issue-agent); without it, delete that step.

## Wiring it up

- Repository secret `CLAUDE_CODE_OAUTH_TOKEN` for Claude Code's GitHub Action.
- Replace the `<scope-owner>` and `<support-owner>` placeholders with GitHub logins (one owner per scope), the `<..._PROJECT_NUMBER>` placeholders with your project numbers, and the label list with yours (`gh label list`). Keep the list authoritative: the agent only applies labels it finds there.
- Optionally, repository variables `ALICE_AUTO_ASSIGN_ENABLED` and `ALICE_SWEEP_ENABLED` and the issue agent's `alice/` folder.
