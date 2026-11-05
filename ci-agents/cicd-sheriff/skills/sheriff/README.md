# sheriff (alias)

**What.** `/sheriff`, a user-invoked alias that hands over to the on-call engineer's production alarm-review skill (`review-alarms`), forwarding whatever the user passed.

**Why.** On call, people type the role, not the skill's name. The alias holds no behavior of its own, so the alarm-review workflow keeps one home, and it is user-invoked only so it never competes with that skill for the model's attention.

**How it fits.** The alarm-review skill it points at is specific to one company's infrastructure and is not shipped here; it stamps its issues and PRs with the same `Sheriff` label the [CI/CD Sheriff](../../README.md) uses, which is how the work report in [`snippets`](../../../../skills/snippets/README.md) recognizes sheriff duty.

**Wire up.** Point the alias at your own alarm-review skill, or drop it.
