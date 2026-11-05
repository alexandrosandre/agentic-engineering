# transcripts

Two scripts that read the coding agents' own session transcripts, so skills can learn from what actually happened in a session instead of from what the diff shows.

| Script | What it does | Used by |
| --- | --- | --- |
| [`find-transcripts.py`](find-transcripts.py) | Locates the session transcripts of a workspace: one path per line, oldest first, trivial sessions dropped, capped at 10 sessions or 1 MB. With `--list`, one TSV row per session across every project (last activity, source, project, path, title), bounded by `--since`/`--until`. | [`contextual-review`](../../skills/contextual-review/) (the sessions behind the branch being reviewed), [`snippets`](../../skills/snippets/) (list mode, for a two-week work report) |
| [`user-turns.py`](user-turns.py) | Extracts only what the user typed over a date window, as Markdown: a heading per session, a bullet per turn, each turn followed by an excerpt of the agent's last words before it (the thing the correction answers). With `--out-dir`, one file per ISO week. | [`dream`](../../skills/dream/)'s rule-learning pass |

## Why

The transcripts are the richest record of how the team works with agents, and the least used. Two of the skills here are built on them:

- **Review with intent.** A diff-only reviewer sees what changed, not what was asked. `contextual-review` reads the sessions that produced a branch and checks the code against the user's stated intent, the design decisions made along the way, and the corrections the user gave, which is where intent drift and context-dependent bugs hide.
- **Learning rules from corrections.** Every time a developer types "no, never do X here", that is a candidate rule. `dream` reads a month of user turns and promotes the corrections that generalize into rules or checks.

## What "the user's own words" means

Most of what sits under the user role in a transcript is not the user: tool results, system reminders, attached skill bodies, task notifications, slash-command envelopes, compaction summaries, the output of shell commands the user ran, and pasted text. `user-turns.py` drops all of those, matched by their envelopes and prefixes. Pasted blocks matter most: they can carry instructions the user did not write (an issue body, a log), so they are stripped with an id-matched envelope that a paste cannot close early. A bare slash command is an invocation, not something the user said.

`find-transcripts.py` treats a session as trivial when its first substantive user entries are only meta-commands (`/help`, `/copy`, `/compact`); blank entries do not count toward that inspection window, so ten empty turns cannot hide real work behind them.

## Layouts

The scripts handle two transcript layouts: Claude Code's (`~/.claude/projects/<slug>/<session>.jsonl`, role nested under `message`) and an IDE agent's (one folder deeper under each project, role at the top of each entry, typed input inside an envelope). The IDE agent's directories and markers sit in one block marked `TODO` at the top of `find-transcripts.py`, filled with neutral sample values; map it to your IDE agent's format, and the selection, filtering and rendering logic does not change.

## Privacy

Transcripts can carry customer data. These scripts only read local files and print to stdout or a local directory; the skills that use them keep the output on the developer's machine, which is why the [dream routine](../../routines/dream/) runs locally.

## Tests

`tests/` covers role detection across both layouts, envelope unwrapping, the triviality budget, session titles, which entries count as user turns, and rendering. Run with `pytest tools/transcripts`.
