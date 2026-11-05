# yolo

**What.** Commit, push, `/create-pr`, mark ready, resolve open threads, squash-merge. No review, no CI wait.

**Why.** Some changes are trivial and fully understood (a typo in a doc, a one-line config the author just tested), and the full pipeline would spend review-bot rounds and minutes of waiting on nothing. Naming the shortcut honestly keeps it from being used by accident: whatever happens after the merge is the author's problem, and the invocation itself is the explicit per-PR approval.

**How it fits.** The merging shortcut with zero review; `/lgtm` is the reviewed one. See the [skills catalog](../README.md#the-delivery-pipeline).

**Wire up.** `gh` with merge rights. It merges without waiting only where the repository has no required status checks; with required checks, GitHub refuses and the skill reports it rather than using admin overrides.
