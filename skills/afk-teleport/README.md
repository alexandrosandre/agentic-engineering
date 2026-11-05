# afk-teleport

**What.** `/afk` from the cloud: commits the pending work, moves the session into a cloud agent session through the agent host's "continue in cloud" handoff, and hands the cloud session the instruction to run `/afk` plus everything that lives only on this machine. Its last local message is the link to the cloud session, where the report arrives.

**Why.** A laptop that sleeps kills an `/afk` run. The move itself carries only the branch and a conversation summary, so the skill's job is the handoff: stop background work (it dies anyway) and say what it was for, carry scratchpad notes and findings, restate the user's personal instructions (the cloud session loads the repository's rules, not the user's global ones or their memory), and name the machine-only access the remaining work leans on, so the cloud session ledgers what it cannot reach instead of stalling.

**How it fits.** A thin wrapper; `afk` owns the run. `/siesta-teleport` is an alias. When the host cannot move the session, it falls back to a plain `/afk`.

**Wire up.** An agent host that can move a local session to a cloud session and exposes that to the agent as a tool.
