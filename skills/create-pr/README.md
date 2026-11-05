# create-pr

**What.** Merges the default branch, then opens a draft PR with a scoped title, a structured description and the linked issues — or, on a branch that already has an open PR, regenerates its title and description in place.

**Why.** The PR description seeds the squash commit and is what a reviewer reads cold, so it is written for that reader:

- It opens with **one sentence naming what to judge** (`To judge: whether this is the right contract, not whether the wording is good`). The bots read every line of code anyway; a person's attention goes to the intent.
- Fixed sections: **What** (one sentence for the whole change first), **Why** (the problem as reported, and what checking that report against the code found), **Risk** (only when a risk review produced one), **Decisions to check** (the judgment calls the diff cannot show), **Out of scope**.
- Migration, infrastructure and deploy-order sections are regenerated from the current diff on every run, so a changed diff never leaves stale deploy steps behind; only free-form human prose is carried over.
- Agents never address the description to anyone or suggest reviewers. Involving people is the author's call.
- Generated text goes through files, never inline shell strings, where backticks and apostrophes break or execute.

Re-running it on an open PR is how a PR whose scope grew gets its description refreshed before merge.

**How it fits.** Step 3 of `/ship-it` and `/ship-it-lite`, used by `/lgtm`, `/yolo` and `/prototype`. See the [skills catalog](../README.md#the-delivery-pipeline).

**Wire up.** `gh` authenticated. Define your title scopes and the regex that checks them (one scope per top-level area of your repository).
