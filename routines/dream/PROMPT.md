---
name: dream
description: Monthly memory consolidation and rule learning (/dream) — first Monday of the month, 12:00
---

Monthly dream run (scheduled). The task fires every Monday; it works on the first Monday of the month only.

1. Check whether today is the first Monday of the month: `python3 -c "import datetime; print(datetime.date.today().day <= 7)"`. If it prints False, reply "Not the first Monday of the month, nothing to do" and stop.
2. If True, invoke the `dream` skill (Skill tool, skill: dream) from the main checkout of the monorepo; if the Skill tool is unavailable, read `skills/dream/SKILL.md` there and follow it. It operates on this machine's auto-memory directory for the main checkout (`~/.claude/projects/<slug>/memory/`, the slug being the checkout path with `/` replaced by `-`) and on this machine's session transcripts since the previous run.

How to run it:
- Act on every memory bucket and proposal, deciding yourself per the skill's Deciding and landing step; verify stale and codified claims with `gh` and a fresh `git fetch origin master` first.
- Land the proposals as the draft PR (one commit per proposal, implementing its recommended option) and end with the skill's ledger, which the user reviews and amends.
- Repo edits go in a provisioned worktree on a fresh branch off `origin/master`: run the repository's worktree script (or `git worktree add -b dream-<YYYYMMDD> <worktrees-dir>/dream-<YYYYMMDD> origin/master`) from the main checkout, commit there, and open the PR as a draft against master. Never commit to master, never merge, no reviewer or assignee.
- Sweep this project's memory directory only. Then list `~/.claude/projects/*/memory` and report which other project directories hold memories, without touching them.
- Stay read-only toward production data stores (verification queries only, per AGENTS.md).
- An empty pass is a valid outcome; say so briefly.
