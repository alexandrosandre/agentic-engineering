# benchmark-models

**What.** The method for comparing models, reasoning-effort levels, providers, serving tiers or agent harnesses on quality, latency and cost for one LLM call site, and for recording the result so it is never measured twice.

**Why.** A benchmark buys one decision at the price of hours, shared quota and real money, and most wasted rounds come from harness traps rather than the models. The skill encodes the traps:

- **Read the ledger first.** Every past benchmark (setup, result, cost, raw data) lives in a ledger read before any new comparison; public benchmarks are pulled live to form a hypothesis and never persisted, since leaderboards move.
- **Test the hypothesis, not the space.** Pin every lever but the one the decision turns on. Measured on one agentic suite, effort levels moved net pass counts little while disagreeing on many individual cases — so tests are paired, and effort is rarely the arm worth paying for.
- **Estimate, then ask.** Dollars (with cache reads priced as such, from the pricing page read that day), external services' own meters, wall time, quota, where the data goes, and a stop rule declared before peeking.
- **A fair instrument.** The harness is an arm; the judge and grader are fixed across arms; the grader must not measure its own error; the noise floor is measured before any gap is read; knobs are pinned where a run cannot lose them and verified to reach the model; latency is measured per workload shape, unbuffered.
- **Caching decides the bill and the order** of cases.
- **Persist the result, not the code**, and write the decision where the call site's pick lives. A latency gap is accepted or blocking, never "unexplained".

**How it fits.** Writes to the model-benchmark ledger convention in `rules/AGENTS.md`. Reads `read-user-sessions` when real usage decides the workload shape.

**Wire up.** A ledger folder (`docs/benchmarks/` with a README defining the entry shape, the standing facts and the instruments table), a separate internal lane of model capacity for benchmarks, and read-only access to the provider's catalog.
