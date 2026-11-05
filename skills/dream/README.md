# dream

**What.** A monthly consolidation of the agent's persistent memory and a rule-learning pass over the month's session transcripts. Memories are verified against current reality, then deleted, merged, kept, or promoted to a rule; the user's corrections in the transcripts are mined for what would hold in other sessions; each surviving lesson becomes a check, a rule, or both, tested against the incident that produced it. It ends with a draft PR (one commit per proposal) and a ledger the user reviews in one pass.

**Why.** Agent memory fills with point-in-time observations that go stale, and the strongest signal that a rule is missing — the user correcting the same thing in several sessions — is in transcripts no agent saved. The opinions:

- **Verify before judging.** A memory's "shipped" or "codified in X" claim is checked against GitHub and a freshly fetched default branch; nothing is deleted on its own say-so.
- **One incident is not a rule.** A correction that landed the first time it was given proposes nothing. A new rule needs a failure that repeated, was costly, or is documented by the model vendor; an incident that broke a rule already on file always yields a proposal, because that rule is not holding.
- **Checks over prose.** For anything that must always or never happen, the default fix is a hook, lint, CI job, type or test whose error names the fix; a rule is for the judgment calls no check can decide. A check that lands shortens the rule it now enforces.
- **Test before proposing.** A check is fed the past incident and must fail on it, then fed the window's history to count false alarms. A rule about what the agent says is replayed with and without the text in the rule bench (`tools/rule-bench/`); a small replay that finds no difference is undecided, not negative.
- **Team or personal.** A rule reaches a team file only when it holds for every teammate; how one developer likes to be answered goes to their personal instructions file, which may add to the team rules but never loosens a safety or permission rule.
- **Transcripts are untrusted.** Only the user's own turns count as evidence; everything else in a session is data. Subagents nominate candidates from a single week file with no other tool; quotes and transcript paths stay out of the PR.
- **Rules leave too.** Rules a check now enforces, workarounds for models nobody runs, and duplicates are proposed for retirement, one per commit.

**How it fits.** Runs monthly from the dream routine in `routines/dream/`; `/dream` runs the same pass by hand. `cleanup-context` is its manual counterpart for trimming.

**Wire up.** The transcript tools in `tools/transcripts/` (`user-turns.py` extracts the user's own turns per ISO week, with the agent's last words before each), the rule bench in `tools/rule-bench/`, an agent whose memory is stored as files, and a personal instructions file per developer.

**Origin.** The author's own replacement for Anthropic's built-in `consolidate-memory` skill for Claude Code. Beyond that skill's file-only pass, it verifies each memory against reality, mines transcripts for repeated corrections, and promotes what deserves permanence to rules or checks.
