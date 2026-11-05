# rule-bench

`rule-bench.py`: replay real prompts through headless Claude Code under variants of the repository's agent rules, have a blind judge grade the answers, and report whether the variant changed anything.

```
rule-bench.py run    SPEC --out DIR [--arms A,B] [--cases id,...] [--repeats N] [--parallel K]
rule-bench.py grade  SPEC --out DIR [--parallel K]
rule-bench.py report SPEC --out DIR
```

## Why

Rules files grow by accretion: someone gets a bad answer, adds a sentence, and nobody ever checks whether the sentence changed anything. Most don't. Some make things worse, by diluting the rules that mattered or by teaching the agent to hedge. The [`dream`](../../skills/dream/) skill proposes new rules from real corrections, and before a rule about what the agent *says* lands, rule-bench answers the only question that matters: with this text in place, does the agent answer the real situation correctly more often than without it?

## How it works

- **Spec.** A JSON file names a git `ref`, the model and judge model, `repeats`, a list of **arms** (each a set of files laid over the ref, such as `AGENTS.md` with and without the proposed sentence), and **cases** (a real prompt plus a rubric: the true answer, what a correct answer must contain, and the plausible wrong one).
- **Run.** Every case runs `repeats` times per arm, each in a fresh headless session in its own clone, so nothing one run writes reaches another. Sessions are not persisted, so the benchmark's prompts never show up later as "user turns" for `dream` to mine.
- **Grade.** A judge sees one final answer at a time, with no arm label and no tool calls, and scores it 1, 0.5 or 0 against the rubric, plus whether it stated something unverified as fact. The tool therefore measures what an agent answers, not what it does.
- **Report.** Per arm: cases passed (a case passes when most graded repeats score 1), mean score, invented-fact count, cases whose repeats disagree, cost, and median duration. Then each arm against the first with an exact McNemar test on the paired case outcomes, because with a few dozen cases and noisy agents, eyeballing two pass rates is how people convince themselves of effects that are not there.

## Isolation and contamination

- Each clone shares objects with the repository but has its own refs and a push URL that cannot work, and the arm's overlay is folded into its commit, so every arm starts from a clean tree (an agent that sees uncommitted changes is told to read them, which would point it straight at the rule under test).
- The child environment drops the parent session's markers, cloud keys and GitHub tokens and carries only a read-only cloud identity; common git and GitHub write commands are denied by permission rule, including through `-C`, `-c` and flags before a `gh` subcommand. These are defaults, not a sandbox; Claude Code's auto mode is what stops a deliberate write.
- `off_limits` paths (the transcript of the session where the answer was found, for instance) are denied to the Read tool, and a run whose tool calls or outputs reach one is reported as contaminated and excluded. A bare transcript listing is exempt; a listing piped into a search is not.
- An output directory is bound to one spec and one commit: resumes reuse the recorded commit even after the ref moves, and a changed spec is refused. A run that hits the account's usage limit stops the whole batch, and a rerun retries only errored runs.

## Wiring it up

`claude_command` builds the `claude -p` command line, and `parse_stream` reads its `stream-json` events (assistant messages with tool calls, tool results, a final result with answer, cost and duration). `read_only_cloud_env` is a stub to wire to your cloud provider's CLI. Set `PROVISIONED` to the dependency folders worth linking into each clone.

## Tests

`tests/` covers stream parsing, error runs, the pass rule, exact McNemar values, the off-limits deny rules and contamination detection (on full text, past the stored clip), and the output-directory binding.
