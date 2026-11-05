# contextual-review

**What.** A review of the branch diff against the literal session transcripts. One reviewer subagent reads the conversations that produced the change and the diff together, and returns findings tagged Blocker / Important / Nit in three categories: bug, intent, design.

**Why.** Every other reviewer sees only the diff. None of them knows what the user actually asked for, which alternatives were rejected, what constraint was added halfway through, or which edge case was discussed and then never tested. That is where the expensive mistakes hide: a change that is clean, passes CI, and does the wrong thing. This skill covers that one gap and explicitly nothing else — style, lint, security, duplication and performance belong to the other reviewers, and the skill's prompt lists them as out of scope so it does not drift into a generic review.

The reviewer cites the user's words verbatim for every finding that turns on session context, so the person triaging can check the call. Invoked alone, it never fixes anything without confirmation; inside `/ship-it`, `/ship-it` triages its findings against its own bar and sends the fixes back through review.

**How it fits.** The last step of `/ship-it`; runnable alone before `/autoreview` for risky or intent-heavy changes. It pairs with `/simplify`: the contextual pass owns "did we ship what we meant", the fresh-eyes pass owns "is the code tidy".

**Wire up.** The transcript locator in `tools/transcripts/` (it finds the session files of the current checkout across agent harnesses, filters trivial sessions and caps the total). A subagent facility. Keep the name: calling it `code-review` collides with built-in review commands.
