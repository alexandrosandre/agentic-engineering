---
name: afk-teleport
description: >-
  Move the session to a cloud agent session and continue there fully autonomously, because
  the user is leaving and this machine may sleep (also invoked as /siesta-teleport). Use when the
  user invokes /afk-teleport or /siesta-teleport, or asks to keep working unattended in the cloud.
  Not for unattended work that stays on this machine (afk).
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---

# afk-teleport

`/afk` run from the cloud: this session teleports to a cloud agent session — the agent host's "continue in cloud" handoff, exposed to the agent as a move-to-cloud tool — and the cloud session runs [`afk`](../afk/SKILL.md), so the work survives this machine closing. `afk` owns the unattended run; this skill owns only the handoff. Keep this turn to that handoff and move as early as it allows: the user is waiting for the move before they can leave.

## Hand off

The move carries two things: the branch, which the host pushes, and a summary of this conversation. It then archives this session, so whatever lives only here is lost unless you carry it:

- Commit the pending work: the move refuses uncommitted changes.
- Stop in-flight background work (subagents, long commands) instead of waiting for it — it dies with this session anyway — and note in the summary what it was for, so the cloud session reruns it.

Then call the move-to-cloud tool with a summary (a few thousand characters at most) that:

- Opens with the instruction the cloud session acts on: the user is away, so invoke the `afk` skill first and follow it end to end; then the run's remaining steps.
- Carries what the remaining work needs from this machine: scratchpad notes, findings, query or benchmark results, decisions already taken.
- Restates the user's personal instructions that bear on the remaining work, such as commit-trailer or PR conventions: the cloud session loads the repository's `AGENTS.md`, not the user's global instructions or memory, which live on this machine.
- Names the machine-only access the remaining work leans on — local cloud-credential profiles, local dev servers, the editor's browser pane — so the cloud session checks for it and ledgers what it cannot reach instead of stalling on it.

A fixable refusal (a push rejected, an unknown environment) names its fix: apply it and call again. When the session cannot move at all — the host offers no such move, or the session is already remote — run `afk` here instead, and open its final report with why the move did not happen.

## Closing

After a successful move, reply with one line carrying the cloud session's link, then a blockquote line: **Skills used:** then each skill name in backticks (this skill: `afk-teleport`). The cloud session's own report comes from `afk`.

If this skill's instructions failed or needed a workaround, update this file.
