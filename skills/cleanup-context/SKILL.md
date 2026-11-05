---
name: cleanup-context
description: >-
  Optimize the coding-agent context — AGENTS.md files, the skill listing, and
  frequently-loaded skill bodies — so agents follow it instead of drowning in it. Use when
  asked to clean up, slim, optimize, or review the agent context or rules, or when agents
  keep ignoring a documented rule. Not for a product agent's runtime prompt, which is gated
  by its own evals.
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---

# Clean Up the Agent Context

Read `docs/handbook/WRITING_FOR_AI_AGENTS.md` first — it owns the criteria (fewest high-signal tokens, one home per fact, current truth only, right altitude, emphasis, progressive disclosure). This skill adds only the workflow.

## 1. Measure the surface

- **Always-on every session:** root `AGENTS.md` + the root shim (with its routing table) + the skill listing (every skill's frontmatter `description`). Estimate tokens as bytes/4.
- **Always-on per service:** each per-service `AGENTS.md` — agents that read `AGENTS.md` natively attach it when editing under its directory; the others attach it through the directory's shim when a file there is read inside the session's working directory, and the root routing table covers the rest. Weight by how often that service is worked on.
- **Practically always-on:** skill bodies loaded in a large share of sessions. Mine real usage:

  ```bash
  python3 skills/cleanup-context/scripts/skill_usage.py [session_limit] [repo_name]
  ```

  It scans the newest local session transcripts and prints, per skill, invocation and session counts, plus how often each `AGENTS.md`/handbook file was opened with the Read tool or attached by the harness itself (the usual route for per-service rules); shell reads are not counted. Treat the counts as a low-confidence signal: they cover only this machine's local sessions — cloud/background runs and teammates' usage are invisible to it. A skill loading in a third of sessions is always-on in practice — its body is a first-class trim target; one never loading is a description problem or a deletion candidate (deletion is the user's call).

## 2. Classify candidates

Sweep every file on the surface for the handbook's failure classes, weighted by load frequency — a byte in the root file is worth ~10 in a cold per-service file:

- **Duplicated** rules (across AGENTS.md files, or skill body vs AGENTS.md): pick the one home — where the reader is when the rule fires — and leave a pointer or nothing. Skills never restate AGENTS.md (it is loaded alongside them), except text a skill puts into a brief for a subagent type that starts without it (`docs/handbook/WRITING_FOR_AI_AGENTS.md`, delegation briefs).
- **Obvious** rules a frontier model follows untold: delete.
- **Rarely-firing** always-on content: move behind a trigger that actually fires — a per-directory `AGENTS.md` (plus its shims and a routing-table row in the root shim), a skill with a trigger-rich description, or the file the agent already opens for the task (e.g. rendering rules inside the people registry).
- **Stale/history** framing ("predates the rule", "that happened once", dates, migrations): rewrite as current truth; the why lives on, the era narration dies.
- **Bloated skill descriptions**: keep the trigger clause and disambiguating "Not for …" clauses; procedure summaries belong in the body.
- **Wrong-audience files** named `AGENTS.md` (system prompts, vendored docs): rename them out of the auto-loaded namespace.
- **Rules broken while loaded** (the user corrected a rule that was in context): moving, trimming or emphasizing it does not make it hold; route it to a check (`dream` step 7).
- **Emphasis inflation** (CAPS/MUST chains): flag, but de-inflate battle-tested rails only as its own separate, deliberate edit — never bundled with moves.

## 3. Apply

- Minimal diff: only what moves the needle. Move content verbatim first; rewriting is a separate edit within the pass, never combined with the move in one unreviewable diff.
- A moved rule is only moved when its new home is loaded at the moment the rule fires. If no such home exists, condense in place instead.
- Ask the user before deleting a skill, and before rewriting any rule whose meaning or extent you are unsure of — if it confuses you it confuses the agent, and only the author knows the intent.
- A rule block deliberately duplicated across sibling directories takes the same edit in every copy, same PR (`AGENTS.md`, rule-writing conventions).
- One commit per coherent group (root trim, per-file dedupe, descriptions, …) so moves stay reviewable.

## 4. Verify

- Re-read every edited file end-to-end: no rule may end up homeless — each deleted block was moved somewhere loaded-when-relevant or deliberately erased.
- Grep for dangling references: routing-table rows ↔ files, shims present for any new `AGENTS.md`, skill cross-references resolve, no pointer to a section that no longer exists.
- Report before/after bytes (and ~tokens) per file.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `cleanup-context`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
