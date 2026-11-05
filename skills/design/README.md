# design

**What.** Brainstorms the design of a feature or a major change with the user and records the result as a design doc: the options per decision, their trade-offs and dragons, the user's decisions, and a doc that keeps only what the code cannot show.

**Why.** A design process exists to find **dragons** — the failure modes, constraints and unknowns that stay invisible until implementation — and it is done only when every dragon is addressed, consciously accepted, or open with a concrete way to resolve it. The opinions:

- **The category sets what to optimize.** An experiment optimizes for speed of learning and cheap disposal, an MVP for time to honest user feedback, a platform change for long-term correctness, lock-in and running cost. Same process, different risks to surface.
- **Decisions are the user's.** The agent analyzes; the user decides, one decision per question, in dependency order (a one-way door first). Facts are the agent's to look up, never questions for the user. A doc is never where the user first learns a decision was made.
- **Inherited decisions are decisions.** Keeping the current database or service boundary is surfaced with what was considered, not silently assumed.
- **No effort estimates.** Coding labor costs about zero, so days and story points are not decision factors.
- **Docs are maps, not evidence.** A claim a doc makes about the system — even one the same agent wrote last week — is verified against the code before a decision rests on it.
- **The doc complements the code.** Every sentence passes a code test (does the code already show it? cut it), an ownership test (does a sibling doc own it? cite it), a breakage test (could someone break the design without it? keep it) and a resume test (does a fresh session need it to continue? keep it until launch). Decided decisions collapse to one entry with their load-bearing why; the analysis stays in the conversation.

**How it fits.** `/design-review` reviews the doc; `/prototype` can build a disposable version with the doc's decisions as constraints; `state-of-the-art-research` feeds it ranked proposals. Doc locations follow the conventions in `rules/AGENTS.md`.

**Wire up.** A design-docs folder (`docs/design/`) and an experiments folder for prototype docs. A structured question tool in the agent helps but is optional.
