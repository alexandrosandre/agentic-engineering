# ship-it-lite

**What.** `/ship-it` without the session-transcript review: local code review, commit and push, `/create-pr`, `/autoreview`. It never merges.

**Why.** The contextual review earns its cost on substantial, intent-heavy sessions. A low-risk change (a config value, a copy fix, a small refactor you understand fully) still deserves the local review and the bot loop, but not a reviewer reading the whole conversation.

**How it fits.** Pick it over `/ship-it` for low-risk work you will merge yourself; pick `/lgtm` when you already approve the result and want the merge too. See the [skills catalog](../README.md#the-delivery-pipeline).

**Wire up.** Same as `ship-it`, minus `contextual-review`.
