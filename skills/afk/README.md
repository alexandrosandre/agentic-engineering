# afk

**What.** Tells the agent the user is leaving for an extended period: keep the session moving without them, from wherever it is — design to plan to code to the non-merging pipeline — and come back with a report and a ledger of the decisions taken in their absence.

**Why.** An agent that stops to ask at every fork turns an hour away into an hour lost. One that decides silently leaves the user unable to tell what was chosen for them. The skill makes the agent work like a principal engineer left in charge:

- **Rails do not move.** All rules stay in force; autonomy widens which decisions the agent takes, not what it may touch. It never merges, never invokes the merging skills, and never mentions, assigns or requests review from anyone — a mention notifies a real person, in the user's name, about work the user has not approved.
- **A ledger instead of questions.** At each fork the agent records the decision point, weighs the options (running a local experiment when one can settle it), takes the winner, and prefers the reversible option when evidence is thin. The ledger lives outside the worktree and heads with the remaining steps, so it also survives context compaction.
- **Decisions stay provisional.** A ledgered call is never written into a design doc as if the user had made it; the final report is where the user ratifies each one, written to be read cold in the product's vocabulary.
- **Don't hand work back.** A "what remains" list is usually work the run should have done. Stop only when everything is done, ledgered, or genuinely blocked on the user.

**How it fits.** Ends with `/ship-it` or `/ship-it-lite`. `/afk-teleport` runs it from a cloud session; `/siesta` is an alias; `/prototype` is the variant for a build to try and maybe discard.

**Wire up.** Nothing beyond the pipeline skills.
