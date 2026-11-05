# cleanup-context

**What.** Optimizes the coding-agent context — the `AGENTS.md` files, the skill listing, and the skill bodies that load in many sessions — so agents follow it instead of drowning in it.

**Why.** Every always-on line is re-sent on every step of every turn, and compliance falls with the number of rules that must hold at once. Rule files only grow unless someone prunes them on purpose. The skill measures before it cuts: it mines local session transcripts (`scripts/skill_usage.py`) for how often each skill loads and each rule file is attached, weights each byte by how often it loads, and classifies candidates by the failure classes of [`WRITING_FOR_AI_AGENTS.md`](../../rules/WRITING_FOR_AI_AGENTS.md): duplicated, obvious, rarely firing but always on, history framing, bloated descriptions, wrong-audience files, emphasis inflation. A rule that keeps breaking while loaded is routed to a check rather than reworded. Moves and rewrites go in separate commits so each stays reviewable, and nothing ends up homeless.

**How it fits.** The manual counterpart of `dream`'s rule-retirement pass; both apply the same handbook.

**Wire up.** `scripts/skill_usage.py` reads Claude Code's transcript store from its `PROJECTS_ROOT` constant (default `~/.claude/projects`, one folder per project holding one JSONL file per session); pass it your repository's name. The counts cover only the machine it runs on.
