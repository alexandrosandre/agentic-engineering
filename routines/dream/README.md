# Dream routine

Monthly Claude Code run, one per developer, that consolidates the agent's auto-memory on that developer's machine and mines the month's session transcripts for corrections that deserve a rule, or a check that makes the mistake fail. It lands the tested proposals as one draft PR with one commit per proposal, and opens no PR when there is none. Procedure: the [`dream`](../../skills/dream/) skill.

| | |
| --- | --- |
| Owner | Each developer runs their own instance |
| Platform | Claude Code (local): scheduled task `dream` on the developer's machine (`~/.claude/scheduled-tasks/`) |
| Schedule | The task fires every Monday at midday local time; the prompt works on the first Monday of the month only. Midday so the developer can review the run's ledger and send corrections the same day. |
| Model tier | The strongest available model, high effort |
| Repo | The main checkout; a fresh worktree off `origin/master` when rules or checks change |
| Generates | Memory and `~/.claude/CLAUDE.md` edits on the machine, backed up first to a new `~/.claude/dream-backups/<date-time>/`; a draft PR `Dream — <date>` when there are proposals; a ledger in the run's session |
| Source | [PROMPT.md](PROMPT.md) (task prompt, verbatim) |

## What it is for

An agent's memory drifts: notes go stale when the code moves, duplicates pile up, and the corrections a developer types in the middle of a session ("never do X here") stay in that one session. The dream run is the monthly pass that turns that residue into something durable. It verifies each memory against the current repository, prunes and merges, and, from the transcripts, finds corrections that generalize. Those become rules in `AGENTS.md`, skill edits, or better, checks that make the mistake fail, each one tested before it is proposed (with [rule-bench](../../tools/rule-bench/) when the rule is about what the agent answers).

The opinion behind it: a correction the user had to give twice is a missing rule, and a rule that can be a check should be a check.

## Installing it

Create the scheduled task in Claude Code with the `schedule` skill: name `dream`, cron `0 12 * * 1`, [PROMPT.md](PROMPT.md) as the prompt, the main checkout as the working directory. Memories and transcripts are per machine, so each developer who wants their own sessions mined installs their own task; the rules it proposes are the team's.

It needs the [transcript tools](../../tools/transcripts/) to read the sessions, and a worktree script (or plain `git worktree add`) to keep its edits off the main checkout.

## Why it runs locally

Reason 2 of the local-routine policy in [`routines/README.md`](../README.md): its inputs, the auto-memory directory and the session transcripts under `~/.claude/projects` (and the IDE agent's own folder), exist only on the developer's machine, and they stay there (transcripts can carry customer data). No hosted runner can have them, so there is no move to plan.
