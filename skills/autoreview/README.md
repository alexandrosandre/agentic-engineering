# autoreview

**What.** Babysits an open PR, hands-free, until it is merge-ready: merges the base when it must, waits for CI, fixes failures the branch caused, and triages every review item — human threads, bot threads, review summaries, general comments — into **Fix it**, **Silently resolve / skip** or **Leave open and report**. It ends with only the items that need the author, plus a drift report of what it changed.

**Why.** After a PR opens, most of the remaining work is mechanical but attention-hungry: polling checks, reading bot output in three different shapes, deciding which findings are real. The skill takes that over under a strict contract:

- **Leave open by default.** Only confirmed bugs in PR-touched code, unmet PR intent, rule violations the PR introduced, branch-caused CI failures, and explicit requests from the PR author get fixed. Nits, refactors and "consider" suggestions from others stay the author's call; scope is anchored on the PR's stated intent, not on the moving diff.
- **Batch per head SHA, push once.** Every push restarts every review bot, so all fixes for one head go out together, after a local review of just that batch (review fixes introduced about a quarter of the real bugs the bots later found on sampled PRs). Replies and thread resolutions wait until GitHub shows the pushed head.
- **Merge the base only when it pays.** At start (so checks test the PR against current base), on a conflict, or once for a failure the newer base may have fixed. A merge-only push minutes later would restart every bot to re-test little.
- **Corroboration counts.** Two bots flagging the same line are verified against the code before any "false positive" dismissal.
- **Loop safety.** Caps on wait time, base merges, repeated CI failures, and — on the unattended agent's PRs — five fix rounds, after which the PR is handed over with the open findings listed.
- **Resolve only what is settled.** Replying does not justify resolving; questions and disagreements stay open for the author to close.

[`references/HEURISTICS.md`](references/HEURISTICS.md) holds the CI classification (branch-related vs flaky/infra vs stale base), the per-author bar and the scope check.

**How it fits.** Step 4 of `/ship-it` and `/ship-it-lite`, the core of `/lgtm`, and usable on its own after `/create-pr`. See the [skills catalog](../README.md#the-delivery-pipeline).

**Wire up.**

- `gh` authenticated. Where a cloud sandbox blocks GitHub's GraphQL API, route the PR calls through a small REST helper; the steps stay the same.
- Fill in the **Review Bot Checks** section with the exact check and workflow names of your review bots, split into security and non-security reviewers.
- If your agent host runs its own PR auto-fix monitor, map the Startup's pause/restore paragraph to its switch.
- Set the unattended agent's login (`alice-bot`) for the round cap, or drop that section.
