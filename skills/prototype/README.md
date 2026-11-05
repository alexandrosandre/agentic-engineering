# prototype

**What.** Builds a disposable prototype the user can try and throw away. One round of questions while the user is there, then the agent takes every remaining decision, builds on a fresh branch, exercises the path the user will try, runs only the local review, and stops at a draft PR. Closing the PR is the discard.

**Why.** Some questions are answered faster by something running than by a design doc, and a prototype loses its value if every fork waits for the user. The skill makes the trade explicit:

- **Want, not method.** The build starts from what the user is after and what done looks like; a prescribed method is parked as one option to evaluate.
- **One question round, then stop asking.** "You decide", "not sure" and "too early" are complete answers, and each becomes an agent-owned decision.
- **Two decision ledgers kept apart** — product (what a user or the business gets) and technical (architecture, infrastructure, mechanism) — so a product call is not rubber-stamped along with a technical one; plus a learning ledger for what experiments settled. Each decision is written to be ratified cold, with its reversibility.
- **The draft keeps the bots off.** No `/autoreview`, no ready-for-review, no merge, no mentions, no design doc (a design doc would record decisions the user never made).
- **Ratification at the end.** The last act offers to walk one ledger, one decision per question; choosing another option switches the implementation, re-exercises it and reruns the local review.
- **Nothing is written where it should not be.** Paths that write to shared stores are exercised through tests or dry runs, or ledgered as untried.

**How it fits.** Sits between `/design` (decisions the user makes) and `/afk` or `/ship-it` (merge-ready work). `state-of-the-art-research` and `/design` both offer it as a next step.

**Wire up.** The branch start and worktree setup scripts `/checkout` and `/fork` use; `/create-pr`; the local review step of `/ship-it`. A multi-agent workflow mode in the agent is optional.
