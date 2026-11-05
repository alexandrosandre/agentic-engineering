# ship-it

**What.** One command that takes finished work to a fully reviewed, merge-ready PR: a local code review, commit and push, `/create-pr`, `/autoreview` until CI and the review bots are settled, then `/contextual-review` against the session transcripts, whose fixes go through the review loop again. It never merges.

**Why.** The delivery pipeline has five steps that all need to run, in order, every time, and each one is easy to skip when a session ends. The opinions it encodes:

- **Review locally before the bots see it.** The fixes then land in the commit the bots review, so a bot round is not spent finding what a local pass would have found. The local review runs at the bots' own effort level and in a fresh-context subagent: run inline at the end of a long session, a reviewer skips most of its passes.
- **A fix bar, not a wish list.** Confirmed bugs, regressions, unmet intent and rule violations get fixed, along with every other place the change repeats the same mistake (the bots would flag each copy on a later round). Nits, refactors and opportunistic improvements go to the summary.
- **The name encodes merge authority.** `ship-it*` never merges; merging is the author's `/lgtm` or `/yolo`. Unaddressed Blockers from the contextual review open the summary instead of hiding behind "merge-ready".

**How it fits.** It is the full shortcut of the pipeline (see the [skills catalog](../README.md#the-delivery-pipeline)). `/ship-it-lite` is the same without the contextual review; `/afk` ends with it; the unattended issue agent runs it with extra risk-review and verification steps (see [alice-issue-agent](https://github.com/alexandrosandre/alice-issue-agent)).

**Wire up.** `gh` authenticated; the sibling skills `create-pr`, `autoreview`, `contextual-review`; a built-in or installed code-review command for the local pass (or the agent reviews the diff itself).
