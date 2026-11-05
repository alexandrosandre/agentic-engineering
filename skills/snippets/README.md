# snippets

**What.** Generates a developer's biweekly work report for the whole team: plain-language one-liners of what they did in the last two-week cycle (📚 Done) and what is coming (📅 To Do), harvested from GitHub, the developer's agent sessions, their calendar and their sent email, deduplicated and categorized deterministically.

**Why.** A lot of a developer's work with agents never becomes a PR: investigations, chat-only sessions, customer emails, design discussions. Reconstructing two weeks by hand misses most of it, and a list of PR titles means nothing to Sales or Marketing. The skill's opinions:

- **Bullets are tasks, never PRs**, written as outcomes for the team in the product's user-facing vocabulary, one line each, grouped, not exhaustive.
- **Every source is verified, not trusted.** GitHub search over-matches (an `updated:` window, a bulk co-assignment, a closed-but-discarded issue), so each facet has a confirmation query; a closed issue is not "done" until a merged PR or a real resolution shows it.
- **Deterministic routing, first match wins**, with a self-check that keeps someone else's issue out of the runner's Coding section.
- **Never fail the run.** A missing connector degrades to a note; doubts go to a review list, never into the report; scheduled runs never ask questions.
- **Learn the personal filters.** Confirmed-personal calendar and email patterns are appended to a per-user file so the doubt list shrinks.

**How it fits.** Writes Spanish for the team it was built for, using [`spanish-copy`](../spanish-copy/README.md); swap the language and the example bullets for yours. Reads sessions through the transcript locator in `tools/transcripts/`. Can run as a scheduled routine.

**Wire up.** `gh` with `read:project` for the board; calendar and email connectors in the agent (both optional); the cycle anchor date; your board's name and status columns in `references/gh-queries.md`.
