---
name: prototype
description: >-
  Builds a disposable prototype the user can try and discard: one question round, then an
  autonomous build with a split decision ledger, local review only, and a draft PR. Use when
  the user invokes /prototype or asks for a build to try and maybe discard, including an
  overnight workflow run. Not for merge-ready work (/ship-it, /afk) or a design the user
  will decide (/design).
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---

# prototype

A running change the user can try and close. The agent takes the decisions during the build; the user ratifies the ones that matter when they come back. Merge stays with them.

## When to use

- The user invokes `/prototype`, or asks for a build they will try and maybe throw away, including an overnight multi-agent workflow run.
- Not when they want the reviewed pipeline (`/afk`, `/ship-it`, `/ship-it-lite`) or a design doc they will decide (`/design`). If the message is one of those, say so and stop.

## Rails

Autonomy widens who decides, not what the repo allows: `AGENTS.md` stays in force.

- Never merge, and never invoke `/lgtm` or `/yolo`.
- Never invoke `/autoreview`, `/contextual-review`, `/ship-it`, or `/ship-it-lite`, and never mark the PR ready. A draft is what keeps the review bots off.
- Never @mention, assign, or request review from anyone. Leave addressee slots blank.
- Do not invoke `/design` and do not write a design doc. That skill stops until the user decides. The closing message is where the user first sees a decision. Unratified choices stay in the ledger; they are not user decisions. If the user later keeps the work, `/design` records only what they ratified.

## Steps

The order is the requirement: want, one question round, build, local review, draft PR, then the ratification offer. Do not build, review, or offer ratification while an earlier step is open.

### 1. Want, not method

Take the want from the message: what they are after, the constraints, what done looks like when they try it. If that is thin — a sentence with no picture of done — ask them to dump what they have in their head and wait. Do not build yet.

When the want comes from a finished design doc, its user-made decisions are constraints; only the forks it leaves open go to the question round and the ledgers.

If they prescribe a method, park it as one option to evaluate, not as a constraint, unless they insist it is one. Separating the want from the method is the only part of `/problem-definition` that applies; do not run that skill's workshop.

### 2. One question round, then stop asking

Skip this round when the message already delegates the forks ("you decide", "I'm leaving", "don't hold back") or the want leaves no open decision. Otherwise ask once, and say that implementation is next so an answer now is the last one that binds.

Ask with the agent's structured question tool. If that tool is unavailable, ask in chat, one self-contained question at a time. A decision that is costly to reverse gets its own question; related small decisions may share one. When a decision can be delegated, include one choice, "You decide". Not sure and too early are that same choice: question tools commonly allow at most four options and add their own free-text Other, so the three wordings cannot each take a slot. A question a lookup can answer — how the code behaves, what the data holds — is yours to look up, not theirs. "You decide", not sure, or too early is an agent-owned decision: ledger it and do not ask it again.

In that same round, when the agent offers a multi-agent workflow mode and the session is not already running in one, ask them to turn it on at high or medium effort. The highest effort is not required. Do not ask it again after this round. If they have already left, or they do not switch, build in this session.

Open the artifact (step 4) before recording anything, including when this round is skipped. After this round, do not ask again until step 6.

### 3. Build

Start on a fresh branch from `origin/master`. Do not build on the session's current branch, and do not invoke `/checkout`: it asks for branch keywords, and this round is over. Take two or three keywords from the want.

When `git status --porcelain` is empty, run the repository's branch start script (the one `/checkout` runs) with those keywords. When it is not, leave this worktree on its branch. Uncommitted files follow a checkout, and step 5 would commit them into the draft whose closing discards them. Fork beside it: the branch name is the one the start script builds (`<git-user>-<YYYYMMDD>-<keywords>`), at `$WORKTREES_PATH/<branch>`. `git worktree add --no-track -b <branch> "$WORKTREES_PATH/<branch>" origin/master`, then `git push -u origin <branch>`. From inside that worktree, run the repository's worktree setup script so the exercise step has a `.venv` and `node_modules`. Then continue from that worktree: switch the session into it with the agent's worktree tool where it has one, else run every later command from that path. `git -C` is not enough: `/create-pr` and the local review use the current directory's branch.

Where the code goes is the `/prototype` exception in `AGENTS.md` Conventions.

For a fork with more than one viable option where the wrong one is costly to reverse, evaluate the live options in parallel when the host can: one effort per option, a challenger whose job is to show the leader fails, then you pick. A fork the code already answers does not get that. Each delegated agent warms a cache of its own, so delegating every step spends the session limit on warmup.

When evidence is thin, pick the reversible option and keep moving. Implement the want far enough that they can try it. Leave out scale work and infra-cost tuning; those pay off only if they keep it.

Before the review, exercise the path they will try. A change that was never run is not something to try. Exercise it, and run experiments, only where nothing is written. When the local stack reads and writes shared or production stores, a path that writes is exercised through its tests or a dry-run mode, or ledgered as untried for the user to run. Same bound as `/afk`.

### 4. The artifact

Keep one markdown file and rewrite it in place — a diary buries the current state. Outside the worktree, so a commit cannot take it. Its name must be one no other session would pick. On a cloud run whose host publishes files from a fixed artifacts folder, put it there as `prototype.md`. Otherwise use the session scratchpad the host gives you, or `prototype-<session-id>.md` beside the session transcript. Send the path when the question round closes, or at the start of the build when the round was skipped.

Head it with the remaining steps and the want from step 1. When the build starts from a design doc, also record that doc's branch, path, and its user-made decisions as constraints. Keep them current. After a compaction, that file is where the run had got to, including the constraints it must not reopen. Same reason as `/afk`.

Two decision ledgers, kept apart so a product call is not rubber-stamped along with a technical one:

- **Product** — what a user or the business gets, including a security or privacy choice about what is allowed or shown.
- **Technical** — architecture, infrastructure, and mechanism, including how performance or security is implemented.

And a **learning** ledger for questions settled by a subagent or an experiment. A decision that rests on one names it; it does not restate the writeup.

Each decision, written so it can be ratified cold: what changes versus before, in the product's vocabulary; the viable options; the evidence; the winner; reversibility (two-way: easy to undo, or one-way: costly to reverse). Also a short list of doubts still open for the user. Empty when there are none.

The file is the source. The closing message copies both decision ledgers and the learning ledger from it. The PR's Decisions to check copies the two decision ledgers only, labeled provisional and awaiting ratification.

### 5. Local review and a draft to try

Run `/ship-it`'s first step and its triage bar, then stop. Do not continue into the rest of `/ship-it`.

Commit and push all pending changes on the prototype branch, then `/create-pr`. The branch is already on origin; the build's commits are not, and `/create-pr` does not push them. Open the description with `To judge: whether to keep this prototype; closing the PR discards it`. The PR stays draft.

The closing message says how you exercised it and how they repeat that, and that closing the draft PR is the discard. Do not delete the branch. Do not publish a preview unless they asked.

### 6. Offer to ratify one ledger

The last act, after the draft exists, is one question with the same tool as step 2:

Which ledger should we go through, one decision at a time?

- Product decisions
- Architecture, infra, and technical decisions
- Neither

If they pick one, ask that ledger one decision per question. Each question stands alone: what changes versus before, the viable options, the evidence, the winner, the reversibility. Choices are Keep, plus one choice per rejected viable option, and at most four choices. When more options were rejected than fit, ask the remaining ones in the next question rather than dropping them. Keep leaves the decision as ledgered. Any other choice switches the implementation to that option, updates the ledger, re-exercises the path, and reruns step 5 before the next decision. When that ledger is done, ask this same offer for the other ledger. Stop on Neither.

Do not walk the learning ledger — it is evidence, not a decision. After a walk that ratified or switched anything, `/create-pr` again so Decisions to check no longer labels those decisions provisional. If they are not back, the unanswered offer is the handback, not a reason to keep building.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `prototype`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
