---
name: snippets
description: >-
  Generate the biweekly personal work report ("snippets"): plain-language one-liners, in the
  team's language, of the last 2-week cycle's work plus the upcoming To Do. Use when the user
  asks for snippets, the biweekly report, "what did I do these two weeks", or on a scheduled
  biweekly snippets run.
allowed-tools: >-
  Bash(gh api:*) Bash(gh pr list:*) Bash(gh pr view:*) Bash(gh issue list:*)
  Bash(gh issue view:*) Bash(gh project list:*) Bash(gh project item-list:*)
  Bash(python3 -c:*) Bash(python3 tools/transcripts/find-transcripts.py:*)
  Bash(date:*) Bash(mkdir -p:*)
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---

# Snippets — Biweekly Work Report

Builds the personal "snippets" report each dev shares with the team every two weeks: what the runner did (📚 Done) and what's coming (📅 To Do). The audience is the whole team — not only devs — so bullets are concise plain-language one-liners describing outcomes, never raw PR titles. The bullets are in the team's language (Spanish for the team this was written for, so the examples below are Spanish); section headers stay in English as templated.

## When to Use

- The user asks for their snippets, the biweekly report, or "what did I do these two weeks".
- A scheduled task invokes it. Scheduled runs are non-interactive: never ask questions mid-run; collect doubts in the trailing "❓ Revisar" list instead.

## Workflow

### Step 1 — Compute the period

Cycles are 14 days, Monday to Monday, anchored on a fixed Monday (set `anchor` to your team's first cycle). Compute with python3 (macOS `date -v` is fragile):

```bash
python3 -c "
from datetime import date, timedelta
anchor = date(<YYYY>, <M>, <D>)  # your first cycle's Monday
today = date.today()
days_into = (today - anchor).days % 14
boundary = today - timedelta(days=days_into)
if days_into >= 11: boundary += timedelta(days=14)  # Fri-Sun: report the closing cycle early
print('DONE:', boundary - timedelta(days=14), '..', boundary - timedelta(days=1))
print('TODO:', boundary, '..', boundary + timedelta(days=13))
"
```

Runs on the Friday–Sunday before a boundary report the closing cycle early; the missing weekend tail is accepted and never backfilled. Announce the windows to the user up front ("Done: 3–16 mar · To Do: 17–30 mar"). GitHub date qualifiers are UTC; the hours-level skew vs local time is accepted.

### Step 2 — Harvest GitHub

Resolve the runner once: `LOGIN=$(gh api user --jq .login)`. Then run the search facets from [references/gh-queries.md](references/gh-queries.md) over the DONE window: merged PRs, closed-unmerged PRs, still-open PRs created in the window (reported "(en curso)"), issues created, issues closed, issues commented, and PRs reviewed. Critical: `gh api search/issues` **must** use `-X GET` (with `-f` alone the request becomes a POST and the endpoint 404s). Always project `number`, `title`, and `labels` — labels drive categorization. Reviewed-PR candidates must be confirmed by review `submitted_at` date (no review-date qualifier exists in GitHub search; see the reference). Closed issues must pass the "Closed issue ≠ done" verification in the same reference before being reported as fixed — a closed issue may have been discarded, answered, or fixed in a later period.

### Step 3 — Harvest agent sessions

List the runner's coding-agent sessions over the DONE window: through the agent host's session index where it has one (list sessions including archived ones, keep those whose last activity falls inside the window), else through the transcript locator, from the repo root:

```bash
python3 tools/transcripts/find-transcripts.py --list \
  --since <DONE-start> --until <DONE-end> --workspace-substring <repo>
```

Its TSV columns are last-activity, source (the harness), project slug, path, title. Then:

- Sessions linked to a PR (or whose branch resolves via `gh pr list --head <branch> --state all --json number`) whose PR appears in Step 2's results are already covered — use their titles only to enrich the bullet. If the linked PR is NOT in Step 2's results (e.g. a still-open PR created before the window), the session is in-window work on it: report it "(en curso)" instead of dropping it.
- The rest is **chat-only work** — visible nowhere else, so it must be reported. Summarize from the session title; read the session's first events only when the title is too vague to write a one-liner. If transcript reads would require an approval prompt (scheduled runs), classify by title alone. Exclude the in-flight run itself and any session that is a snippets run — the report never reports its own generation.

### Step 4 — Harvest the calendar

Tool names vary by connector: discover them with the agent's tool search (e.g. `calendar list events`). Fetch events for both windows. Business events only:

- DONE window → meetings held, routed per [references/categorization.md](references/categorization.md).
- TODO window → upcoming meetings for 📅 To Do, one line each ("Reunión con X — 24 jul").
- Personal events are discarded. Check the runner's personal-filters file (`snippets/personal-filters.md` in the agent's per-user folder; create it if missing) for known-personal patterns; anything doubtful goes to "❓ Revisar", never into the report. In interactive runs, after the user resolves a doubt, append the confirmed-personal pattern to that file so the list shrinks over time.

### Step 5 — Harvest sent email

Business email the runner **sent** in the DONE window is work visible nowhere else — customer replies, vendor/partner coordination, internal decisions. Received-only threads are not the runner's own actions, so they are skipped; email feeds 📚 Done only, never 📅 To Do (that stays calendar + board).

Tool names vary by connector: discover them with the agent's tool search (e.g. `email search threads`). Search **sent** mail over the DONE window. Many mail search syntaxes treat `before:` as exclusive, so pass the day **after** the DONE end (the hours-level timezone skew is accepted, as with GitHub):

```
in:sent after:<DONE-start Y/M/D> before:<DONE-end + 1 day, Y/M/D>
```

Ask for the minimal thread view (subject + snippet — enough to route and write a one-liner) and paginate until the window is exhausted. Read a full thread only when a subject is too vague to summarize; on scheduled (non-interactive) runs, classify by subject alone rather than read bodies. Read-only: never draft, send, or label.

Filter aggressively, then route per [references/categorization.md](references/categorization.md):

- The search returns whole **threads** that contain a match, so results include messages outside the window and replies from other people. Key each item on a message whose sender **is the runner** and whose date falls **inside** the DONE window; drop a thread that has none (same date-confirm discipline as the GitHub facets).
- Drop noise per the email rules in the personal-filters file (create the section if missing): auto-replies, calendar RSVPs, one-line logistics, personal recipients. Anything doubtful goes to "❓ Revisar", never the report. In interactive runs, append a newly confirmed-noise pattern to that file so the list shrinks over time.
- A thread about work already reported (a PR/issue, a meeting) **enriches** that bullet — it never gets a second bullet. Email-only work gets a bullet with no link (never fabricate a `(#...)`).
- Collapse a back-and-forth thread into one item, not one per sent message.

### Step 6 — Merge and categorize

Dedupe first, then route every item per [references/categorization.md](references/categorization.md):

- **Bullets are tasks/scopes, never PRs.** The report is a narrative for the team, not a changelog: one bullet per task or scope of work, with however many links belong to it. Exhaustiveness is not a goal — fold minor items into a grouped line or leave them out; drop only insignificant work, never a whole task.
- Canonical key is the PR number: the GitHub result wins, sessions only enrich. N sessions + N PRs on one task → one bullet.
- Chat-only items get bullets without links — never fabricate a `(#...)` reference.
- Group recurring/sibling topics with `(xN)` (e.g. two weekly cost reviews → one line, both PRs). Target ≤ ~4-6 bullets per subsection.
- Never guess a customer name; unclassifiable-but-significant → 🎲 Others.

### Step 7 — Write the one-liners

For Spanish, load the `spanish-copy` skill first (Spain-Spanish register rules). Follow [references/style-examples.md](references/style-examples.md): past-participle openings, outcome for the team (not the mechanism), the product's user-facing vocabulary per the User-Facing Copy rules in `AGENTS.md`, proper nouns untranslated. Links render as `([#12](https://github.com/<org>/<repo>/pull/12))` (issues use `/issues/`).

### Step 8 — Render and deliver

Render the template below. Top-level sections always appear, even empty; Coding subsections only when non-empty. Project subsections come from bracket prefixes found in the work, not from a hardcoded list. "Bugs/Cleanups" becomes "Bugs/Cleanups (⭐ Sheriff!)" only when `Sheriff`-labeled issues/PRs assigned to the runner exist in the window (the on-call sheriffing skills always label **and self-assign** what they create).

Use real markdown structure, not a flat text block: `##` for the two top-level sections, `###` for their subsections (Coding, Support, Product, ...), `**bold**` for the Coding sub-subsections (project names, Enhancements, Bugs/Cleanups, DevOps, AgentOps), and a blank line between every bullet so the report is scannable, not dense.

```
## 📚 Done

### 👨‍💻 Coding

**<Project>**

<one-liner>

<one-liner>

**Enhancements**

<one-liner>

**Bugs/Cleanups**[ (⭐ Sheriff!)]

<one-liner>

**DevOps**

<one-liner>

**AgentOps**

<one-liner>

### 🆘 Support

### 🧙‍♂️ Product

### ✔️ Reviewing & Collaborating

### 🤖 Dev Team Stuff

### 🎲 Others

## 📅 To Do

<upcoming business meetings and tasks; critical unfinished work, one per line, blank line between>
```

📅 To Do contains, **one line per item**: upcoming business calendar events and the runner's active board items — the team's GitHub Project board statuses are the source of truth for work in progress (open/draft PRs are not: they can sit stale). Flag `P0`-labeled items with a `P0:` prefix. P1+ issues outside the board are deliberately excluded: they are already tracked on GitHub.

Deliver twice: print the full report in chat (copy-paste ready) and archive it verbatim to `snippets/<DONE-end YYYY-MM-DD>.md` in the agent's per-user folder (`mkdir -p` the directory). After the template, append the "❓ Revisar" list and any source-degradation notes.

## Degradation (never fail the run)

- Calendar tools absent (connector not loaded in this session): continue without meetings and append `⚠️ Calendario no disponible (reinicia la sesión con el conector de calendario conectado)`.
- Email connector absent (not loaded in this session): skip the sent-mail harvest and append `⚠️ Correo no disponible (reinicia la sesión con el conector de correo conectado)`.
- No session index in this host: use the transcript locator's listing above instead; if that also yields nothing, report GitHub-only and say so.
- `read:project` scope missing (board query fails): skip it and append `⚠️ Tablero no disponible (ejecuta gh auth refresh -s read:project)`.

## Closing

> **Skills used:** `snippets`
>
> If this skill's instructions failed or needed a workaround, update this file.
