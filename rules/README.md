# Rules

Two files every agent in the repository obeys, and the design that delivers them to every agent that touches the code.

| File | What it is |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | The engineering rules: communication, source control, PRs and issues, compatibility, code style, testing, investigation, tool use, deployment safety, customer data. Copy it to your repository root and fill in its Repository Reference. |
| [`WRITING_FOR_AI_AGENTS.md`](WRITING_FOR_AI_AGENTS.md) | How to write text a model reads as instructions: rules, skills, prompts, tool descriptions. Every rule file and skill here was written and trimmed against it. Place it at `docs/handbook/` in your repository, where `AGENTS.md` and the skills point. |

## The opinions behind the rules

- **Coding labor costs about zero.** Refactors, migrations and one-time setup are never weighed by effort. What is weighed is correctness, reversibility, what external users see, and running cost.
- **The user keeps the decisions that are theirs**: merging, involving other people, product calls, production writes, new vendors. Agents take every other step themselves, including the reads and checks they could have handed back.
- **Claims are hypotheses until checked.** An issue's diagnosis, a doc's description of the system, a memory, a reviewer's finding and the agent's own inference are all verified against the code and the data before anything rests on them, and an unchecked claim says so.
- **Fail loudly, stay simple.** Guard clauses, no defensive fallbacks for values the caller guarantees, no interface surface for callers that do not exist yet, comments only for the why.
- **Prose advises, mechanism guarantees.** A rule that keeps breaking while it sits in context needs a check (a hook, a lint, a CI job, a test), not louder text.
- **Readers arrive cold.** Everything that persists, and every question to the user, is written for someone who was not in the conversation.

## How the rules reach every agent

Rules live in plain Markdown `AGENTS.md` files, the open, vendor-neutral format most coding agents read natively. The design had four requirements: one canonical source for every shared rule (no mirrored copies to drift), the same rules reaching every agent environment, hierarchical scoping (global rules everywhere, a directory's rules only when working in it), and no lock-in to one vendor's rules dialect.

### Hierarchy

The root `AGENTS.md` holds what applies everywhere: communication, coding values, PR and issue conventions, the branch workflow. Each service directory gets its own `AGENTS.md` with its language style guide, its build/lint/test commands and its service-specific rules (a monitoring convention, an error-handling decorator, a data-contract convention). Agents read the nearest `AGENTS.md` to the code being edited and merge it with its ancestors, more specific rules taking precedence, the way `.gitignore` resolves. Each rule lives in the smallest scope where it applies; the root holds only what applies across every service.

Directory scoping replaced file-type scoping (rules for `*.py` only) on purpose: the service directories were language-focused enough that the directory said what the glob would have said, and `AGENTS.md` has no glob syntax that every tool understands.

### Shims for agents that do not read AGENTS.md

Not every agent reads `AGENTS.md`. Some read their own file name, and some review bots read only their own config file. Rather than a second rule set per tool, every directory with an `AGENTS.md` also gets a one-line shim in each tool's format that points at the co-located file:

- an import shim for agents that read their own instruction file and support an `@path` import: the file holds exactly `@AGENTS.md`;
- a link shim for review bots that read their own Markdown config and follow relative links in it: the file holds exactly `[Project Rules](../AGENTS.md)`.

The shims are identical in every directory, never change when a rule changes (both resolve to the co-located file at read time), and exist only until each tool reads `AGENTS.md` natively. Since every shim sits beside its `AGENTS.md`, the hierarchy carries over: an agent reviewing a nested file accumulates every shim on the path, and each expands to its own `AGENTS.md`.

The root shim is the one exception. Besides the import, it carries a small routing table listing each per-service `AGENTS.md` with a one-line instruction to read it before editing files there. The harness attaches a directory's shim only when a file there is read inside the session's working directory, and about a fifth of first edits in a service still happened without its rules (new files written into a directory nothing was read from, edits outside the working directory, resumed sessions). The table is the fallback for those; it changes only when a service directory is added or removed.

### The environments

The same rule set reaches four kinds of consumer: the developer's interactive coding agent in the editor or terminal, cloud and background agent sessions working unattended, the review bots that comment on every PR, and the CI agents in GitHub Actions. Interactive and cloud agents read the rules and the skills; review bots read the rules through their shim and judge the diff against them; CI agents check out the repository and get both. That is why `AGENTS.md` holds rules a reviewer can apply ("never mirror a literal in a test"), not only rules an author follows.

### Rule-writing conventions

- **The first word shows the tier.** Hard prohibitions use `Never`; everything else is a positive imperative (`Use X`, `Prefer X`, `Skip X`). `Don't` is not used: it primes the forbidden token without the force of `Never`. `Avoid` appears only in a `Prefer X (avoid Y)` pair.
- **Condense, but keep the why and the example.** Rule files load on every turn, so redundant prose goes. A rule that loses its rationale gets re-litigated by the next contributor, so the reason stays.
- **Linter-enforced style stays in the linter.** `AGENTS.md` names the lint command and never restates a rule the linter checks.
- **Contradictions are product decisions.** When two rules conflict, the agent asks which one is authoritative before editing either. Deliberate copies (one language style guide repeated in sibling services the hierarchy cannot share) carry a sync obligation: an edit to one copy goes to every copy in the same change.

### Alternatives rejected

- **A vendor-specific rules format as the source of truth**, imported by the others: it keeps glob scoping but ties the shared rule set to one vendor's dialect and leaves drift between dialects unsolved.
- **One native rules folder per tool**: each tool gets its preferred format, at the price of two or three independently maintained rule sets.
- **A hybrid** with `AGENTS.md` for general rules and a vendor format kept only for globbed style guides: the glob scoping bought nothing once the directories were language-focused.

## The developer workflow

These are the commands a developer types into the coding agent. The pipeline is:

```
code → /create-pr → /autoreview → merge
```

Each step can run alone, or a shortcut runs the chain. The shortcuts differ in review coverage and in whether they merge, and their names encode merge authority: `ship-it*` prepares a merge-ready PR and never merges; `/lgtm` and `/yolo` are merge approvals, typing one is the explicit per-PR go for the agent to squash-merge. A plain `LGTM` reply counts as `/lgtm` only from the PR author; from anyone else it is a review comment.

| Skill | What runs | Merges? |
| --- | --- | --- |
| `/ship-it` | local code review → commit/push → `/create-pr` → `/autoreview` → `/contextual-review` (its fixes reviewed again) | No |
| `/ship-it-lite` | local code review → commit/push → `/create-pr` → `/autoreview` | No |
| `/lgtm` | resumes from wherever the branch is → `/autoreview` → fixes clear, consequential findings, dismisses nits and theoretical edge cases | Yes, unless a fix or a conflict resolution changed production behavior beyond what the PR already says, or someone else pushed; then it asks for a fresh `/lgtm` |
| `/yolo` | commit/push → `/create-pr` → immediate squash-merge, no review, no CI wait | Yes |

The shortcuts that review do it locally first, before the review bots see the change, so the fixes land in the commit the bots review and a bot round is not spent finding them. The local pass runs at the bots' own effort level, from a subagent so it reviews in a fresh context (run inline in a long session it skips most of its passes), and triages on the same bar `/autoreview` uses: real bugs and rule violations get fixed, nits come back to the developer. Pick by trust: `/ship-it` for substantial sessions, `/ship-it-lite` for low-risk work you will merge yourself, `/lgtm` when you looked at the result and approve it as a tech lead would, `/yolo` only for trivial changes you fully understand.

The unattended issue agent runs the same pipeline with extra steps (an independent risk review, functional verification, a live-questions link); see [alice-issue-agent](https://github.com/alexandrosandre/alice-issue-agent).

### Leaving the agent alone

- **`/afk`** (alias `/siesta`): the agent keeps the session moving while you are away, design to plan to code to the non-merging pipeline, resolving the forks it would have asked about through an evidence-grounded decision ledger you ratify when you return. It never merges.
- **`/afk-teleport`** (alias `/siesta-teleport`): the same, moved first into a cloud session so the run survives your laptop closing.
- **`/prototype`**: something to try rather than something to merge. One round of questions while you are there, then the agent decides, builds and stops at a draft PR (the review bots stay off) with separate product and technical decision ledgers to walk through together.

### Opening the PR

`/create-pr` merges the default branch and opens a draft PR with a scoped title, a description and the linked issues, or refreshes an open PR's title and description in place. The description opens with one sentence naming what the reviewer should judge (`To judge: whether this is the right contract, not whether the wording is good`) and is structured as **What**, **Why**, **Risk**, **Decisions to check**, **Out of scope**. Whom to notify is the author's call: agents never address the description to anyone.

For intent mismatches the diff-only bots cannot catch, `/contextual-review` reviews the diff against the session transcripts; `/ship-it` includes it.

### Babysitting the PR

`/autoreview` polls CI, fixes failures caused by the branch, and triages every review comment, human and bot, into fix, skip or leave open, until checks are green and every item has a disposition. It batches fixes per head commit so the bots are not restarted per comment, reviews each batch locally before pushing it, and merges the default branch only when it must (at start, on a conflict, or once for a failure the newer base may have fixed), since every push restarts every bot. On the unattended agent's PRs it stops after five fix rounds and hands over what remains.

### Rules and memories

Nothing runs at the end of a session. Code tidying happens before each commit (`/simplify`). Rule learning is a monthly routine: `/dream` consolidates the agent's memories and mines the month's transcripts for corrections that would hold in other sessions, weighs a rule against a check for each, tests both against the past incident, and lands its proposals as a draft PR, one commit each, with a ledger to review. See `routines/` for the schedule.
