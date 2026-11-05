# lgtm

**What.** The author's merge approval as a command. Typing `/lgtm` (or replying a plain "LGTM" as the PR's author) takes the branch from wherever it is — uncommitted, unpushed, no PR, PR in review — through the local review, `/create-pr`, `/autoreview`, a pass that settles the remaining findings with the authority the approval grants, and a squash merge.

**Why.** Merging is shipping, so an agent never merges on its own judgment. But once the author has looked at the result and approves it the way a tech lead would, waiting at the merge button for CI and a few bot nits is wasted attention. The approval is conditional, and the skill checks the condition mechanically:

- It records the head SHA the author approved, and before merging compares a fingerprint of the PR's own changes at that SHA and at the final head. A rebase or merge from the base that touched nothing of the PR's leaves the fingerprint equal, so the approval stands.
- Anything that changed is classified: **Trivial** (tests, comments, lint) and **Fix within intent** (a bug the review found in code the PR adds, fixed so the PR does what its description already says) keep the approval; anything **Substantial** makes it stale, and the skill stops and asks for a fresh `/lgtm`.
- A head someone else pushed stops the merge, and the merge is pinned to the checked SHA so a push in between is refused by GitHub.

**How it fits.** The merging end of the pipeline; `/yolo` is the no-review variant. In the unattended issue agent's merge round, the approval is her issue reviewer's GitHub approval. See the [skills catalog](../README.md#the-delivery-pipeline).

**Wire up.** `gh` authenticated with merge rights; squash merge allowed on the repository; the sibling pipeline skills. If your agent host runs its own PR auto-fix monitor, the skill pauses it for the duration, as `autoreview` describes.
