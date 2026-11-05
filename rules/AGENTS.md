# Agent Guide

Single source of truth for AI coding agents working in this repository. Per-directory additions live in `<directory>/AGENTS.md` and merge with this file through the standard hierarchical `AGENTS.md` model. Agents that do not read `AGENTS.md` natively reach it through one-line shims (see `README.md` beside this file for the design).

---

## Engineering Rules

### Communication
- Use AmE in anything that persists — code, comments, docs, commit messages, PRs, issues — since its readers were not in the conversation. In chat, match the user's language.
- Answer on point, without dense prose or internal shorthand: the reader arrives cold, mid-switch between tasks and sessions, so every gap costs a round-trip. Give what they need to resume: their intent, how far you got, how, the evidence behind each claim, and what is next to decide and do. Use the space and formatting readability needs. Spell out acronyms and define internal terms that are not widely known; never coin one.
- A claim you did not check this session says so in the same sentence (inferred, unverified, or a guess): the reader acts on what reads as fact without re-checking it, so an unmarked inference becomes their wrong premise.
- Hand the user only the steps your own access cannot take or that are theirs to take (a sign-in, a production write per Deployment & Infrastructure Safety, their console), and run every read, check and debug step yourself first. A command you do hand over has been run first or says it has not, and a shell command runs from any directory (absolute paths or a `cd` first; when it leaves this machine, as in a PR body, paths from the repository root under a line saying to run it there) with every value filled in, secrets as a lookup (an env var, a secrets-manager call) and never a literal: the user pastes it into whichever terminal is open, and each one that fails costs a round-trip.
- Name the idea before explaining it, in words the reader already has. Identifiers, function names and internal vocabulary have nothing to attach to until the idea has a name, so an explanation built from them leaves the reader assembling the meaning instead of receiving it. Approximate is fine at that altitude: precision comes next, and the mechanism only when the question needs it. Left alone, an explanation comes out in the order it was discovered, which suits whoever did the discovering and nobody else.
- A question to the user is answered cold and in isolation, so it carries everything the answer depends on — what is being decided, the options, what each one changes, and the findings that led there — and assumes nothing from earlier text: no "as described above", and no term, label, or figure that only makes sense to someone who read it. A choice put to them while a question of their own is unanswered is not ready to be asked: answer theirs first, then ask, since the answer is usually what decides the choice.
- Explain changes in chat; never narrate them in comments or docs — describe current behavior only.
- Always use the GitHub CLI to access github.com URLs.

### User-Facing Copy
- Use the term the UI uses, never the backend's internal synonym, in all user-facing text: when the UI labels a concept one way and the code another, users only know the UI's word.
- Never write an internal codename (a service, an assistant, a project) in user-facing text: users do not know it.
- Apply this to any customer-visible text, including UI copy, in-app explanations, user-visible warning text, API error payloads shown verbatim in the UI, and email copy.
- Keep raw per-event signals and the aggregated, user-facing concept they feed apart in naming: a word the product reserves for what a user sees is not used for an internal intermediate.
- Write for the product's real audience and prefer the vocabulary of the tools they already use over internal engineering terms.
- Do not expose internal operational details (schedules, infrastructure timing, regions) in user-facing text. Keep copy functional and outcome-oriented.

### People & mentions
- Teammate references: match and render them per the people registry kept in the repository (handles, display names, how each is written) — open it whenever writing a person into a PR, issue, chat message, code comment, or reply.

### Source Control
- Never commit or push directly to the default branch; always work on a feature branch and create a PR.
- Merging is the user's call: never merge a PR without their explicit go in the current conversation — `/lgtm`, `/yolo`, or plain words. No task wording implies merge authority: the default branch is always releasable, so merging is shipping — even a task whose verification needs the change deployed stops at a merge-ready PR and asks. On the unattended issue agent's PRs, the go is the approval of her issue's reviewer on GitHub. The go covers the changes the user had in front of them. A rebase or a merge from the default branch that leaves the PR's own changes as they were keeps it, and under `/lgtm` so do the changes its step 5 classes as Trivial or Fix within intent, a conflict resolution's included; any other change to them, or another session's push after it, means they approved something else — show them what changed and ask again.
- Never create branches that track the default branch; when branching from `origin/master`, always use `--no-track` and set upstream to the branch itself (`git push -u origin <branch>`).
- Name branches with `-`, never `/` (`fix-login-button`): deploy tooling that derives resource names from the branch rejects a slash, so the branch could not deploy to a feature-branch environment.
- Never amend a Git commit: the worktree and branch are shared with the user and other agents (below), who may already be building on that commit.
- Working-tree modifications you didn't make are intentional — another agent or the user is working on the same branch / worktree. Read the diff to understand what changed, then adapt your own work to coexist. Never undo or discard those changes. If the external change conflicts with yours, pause and ask before proceeding.
- Worktrees share one repository, so never let the shell's cwd decide which tree you act on. A `cd` leaked from an earlier command silently lands edits, `git checkout`, and test runs in the main checkout instead. Target the tree explicitly (`git -C <path>`, absolute paths) and check `git status` in the tree you meant before reporting a result.
- `git stash` is repo-global, and `git stash push` with nothing to save is a silent no-op — the next `pop` then restores an unrelated entry from another branch into your worktree. Never stash to shelve an edit for a before/after run — a red/green, or an A/B baseline against a candidate: check out the pre-change revision instead (`git checkout <sha> -- <path>`), or re-apply the edit by hand.

### Pull Requests & Issues
- If the PR relates to GitHub issue(s), the PR description must mention them using `Fixes #<issue_number>` (when merging leaves none of the work the issue asks for: a pending release does not keep it open, nor does a leftover that is a separate problem, already wrong on the default branch or filed as its own issue) or `Part of #<issue_number>` (when requested work remains, and on a `P0` issue, which stays open until its fix is released). Use one line per issue.
- Before merging, refresh the PR title and description if they have drifted significantly from the branch's diff and intent — the squash-merge commit is seeded from them. Re-run `/create-pr`, which updates an open PR in place.
- Bug issues: describe the symptom; optionally add root cause + debug steps. Fix goes in the PR.
- An issue states the result wanted whenever its writer knows it: the unattended issue agent, which works issues alone, asks on the issue instead of guessing when the code and data do not settle it.
- Tackling an issue: its report, diagnosis, and instructions are claims, not facts — the reporter wrote through their own hypothesis, and the code may have moved since. Start from the documented pain, complaint, or symptom, verify every claim against the code and the data, and rethink the fix from there; a claim or instruction becomes context only once it holds, and one that does not is reported back with what was found instead.
- Redefining a body you just posted is an in-place edit (`gh issue edit --body-file`, or `gh pr edit` for PRs), with the delta reported in chat — the body stays one current, self-contained statement, not a ledger of narrating comments. Once the body has an audience (you're acting on it, logging progress, revising it weeks later) or someone else posted it, comment instead: a silent edit rewrites what readers already saw.

### Migrations & Compatibility
- Coding labor cost is ~0: never weight refactors or migrations by author-time, lines of code, or "effort". Internal migrations are cheap for the same reason: a one-time script that rewrites callers or moves data costs nothing. One-time setup the user can perform (a repo secret, a credential, a config entry) is equally ~0 — never argue against a design option because it is not wired up yet.
- Backward compatibility is not a default requirement unless the surface is externally observable. For launched features or released SDK versions, support existing users, data, and dependencies. Product analytics events are externally observable too — dashboards count them — so a refactor keeps each event firing in exactly the situations it fired before, attributed the same way, and adds no capture to a path that produced none. Widening what an event counts is a product decision the user makes, not a side effect of sharing a helper.
- A change to the API the web app calls reaches browsers still running an older bundle — an open tab outlives any deploy window — so that API counts as externally observable, as does every other client that calls it. Changing it and its web caller in one PR does not make the pair atomic in production. Where compatibility is genuinely impossible, a forced reload from the web app's error boundary is the escape hatch, not the plan.
- Merged code outruns manual schema steps: a merge can deploy staging on its own, and a release can follow a merge within minutes. When merged code depends on a manually applied database DDL, apply the DDL before merging — deploy steps listed in a PR body describe the order; they do not enforce it.

### Code Style (applies to all languages)
- Prefer readability over performance/abstraction.
- Use full words in identifiers (`format_percentage`, not `_fmt_pct`).
- Extract helpers only for non-obvious logic used more than twice; keep trivial one-liners inline since the indirection costs more than the DRY benefit. This is KISS: a helper used once is harder to read than its inline form. Assume the reader knows the language well.
- Never add interface surface (extra params, option flags, abstraction layers, generic wrappers) for hypothetical future callers (YAGNI). Add it when the second real caller arrives; refactors are cheap (see Migrations & Compatibility).
- Name locally shared helper modules `utils.py` / `utils.ts`.
- Handle errors/edge cases early with guard clauses / if-return, not nested branches.
- Validate user-configurable inputs (UI, config) at the input boundary.
- Let contract violations fail loudly; skip defensive fallbacks (`.get(key, default)`, `or {}`, `x if x is not None`) for caller-guaranteed values. This is YAGNI for edge cases: handle inputs the caller can actually produce, not hypothetical ones.
- Prefer guard conditions (`if not x or x < min:`) over silent clamping (`max(x, 1)`) for input validation.
- A failure that will be retried logs at WARN; only the attempt that exhausts the retries logs at ERROR. Error-log alarms fire on ERROR, and some page, so an ERROR on a retried failure raises an alert for a request that went on to succeed. When the code cannot tell which attempt it is (the client retries), find out from the caller.
- Comment only non-obvious logic, and only to explain *why*; the code already shows *what* and *how*. Never restate what the next line does.
- Comments describe current behavior, not the change or prior implementation.
- When docs (README, etc.) conflict with the code, the code is the source of truth; update the docs.
- Max line length: 100 chars, source code only. Apply to lines you add; leave existing files unreflowed. Exceptions: URLs, long string literals, and generated files. Enforced by the linters (pylint, Prettier).
- Never hard-wrap prose — Markdown, docs, commit bodies, PR descriptions, issue and comment bodies. Let a paragraph run as one line and leave wrapping to the reader's editor. Wrapped text that is soft-wrapped again by a narrow window breaks in two places at once and turns ragged, and the only way out is switching soft-wrap off and scrolling sideways.

### Writing for AI agents

Before writing or editing text an AI reads as instructions — any `AGENTS.md`, the agent skills, system prompts in code — read `docs/handbook/WRITING_FOR_AI_AGENTS.md`; when reviewing a diff that writes or edits such text, check the diff against that handbook.

### Testing & Verification
- Tests validate behavior — a property a caller depends on, a branch with a distinct output, or a regression.
- Never write tests that only mirror a literal from production (e.g. asserting `metadata["k"] == v` next to a production line that writes `"k": v`, or asserting a query/config string equals the string the module just constructed). Add such a test only for a non-trivial transform/branch or to lock in a regression (red→green).
- For UI renderers, prefer one smoke test per user-facing outcome plus focused tests for non-obvious transforms/regressions. Do not add one test per JSX branch when the branches only restate static copy or object wiring.
- Skip tests for invalid/edge inputs callers cannot produce (YAGNI for tests).
- A test double never implements the property its test claims: a tenant filter, a lease or a uniqueness rule written into an in-memory fake proves only the fake, while the test reads as proof of the production guarantee. Keep the property out of the fake and test it where production enforces it; for a query or the database, per the SQL rule below.
- In TypeScript suites a test file's cost is its import graph, not its tests: each test file re-imports every module it reaches, which was most of the time the test runner reported for a large backend suite. Import the smallest module that holds the unit; when a pure helper lives in a heavy module (a service, a router, a tool registry), move the helper out rather than import the graph to reach it.
- Each test has a brief docstring stating its testing goal.
- Bugs found during testing or review: fix with a regression test (red → green).
- A red run that passes is not evidence. Before reporting red → green, confirm the red run failed on the assertion the fix targets, with the pre-fix code verifiably in place — check the code itself, not the mechanism that was supposed to revert it.
- Always verify new or changed code works: run existing tests, exercise the code through its entry point (`_main`, CLI, integration test), or add a test per the rules above.
- TypeScript checks are heavy and several agent sessions share one laptop: a vitest run forks a worker for every CPU core but one (about 150 MB each), and a type check loads the whole type graph. While iterating, run only the test files you touched with `--maxWorkers=2`; run the type check and lint once, before committing. Never leave vitest or `tsc` in watch mode, and wait for another running vitest or `tsc` rather than starting a second. CI runs the full suites.
- When using a browser, capture screenshots at each important step and share them in the conversation as you go so visible changes remain available for later comparison.
- New or changed SQL, and any guarantee a query or the database enforces (a tenant filter, row-level security, a lease, a uniqueness rule), must be validated at runtime against a real database of the production engine — mocks miss query errors, and a SQLite fixture passes a production-engine guarantee trivially. Where a CI job starts such a database, commit the test there; otherwise validate ad hoc (`_main`, CLI, or a direct query), never running destructive statements.
- Never commit tests that hit shared databases; committed tests must stay deterministic and free of external services. A throwaway database the CI job itself starts is neither.
- Keep hardcoded params in `_main`/CLI functions intact — they're intentional for local testing.

### Investigation & Debugging
- Before explaining, retuning or redesigning an existing control — an alarm, a threshold, a budget, a cap, a config value — find the intent behind its number. It lives in the code or doc that owns it, or in the PR or issue that introduced it, never in the resource itself: a redesign from the mechanics alone re-derives it wrong.
- Validate hypotheses empirically before presenting conclusions. Query observability sources (the database's query log, log queries, metrics) on full datasets rather than sampled or common-case slices, and include the extreme tail (worst-case durations, not just averages).
- Before any change or decision where how users really behave could favor one option over another — not only work aimed at user behavior — read their real sessions, following the `read-user-sessions` skill, even in the middle of other work. Assumed behavior, synthetic prompts and aggregate counts can each look plausible and still describe users who don't exist.
- Never rest a design or a production command on assumed database engine behavior (type changes, JSON/nullable semantics, mutation mechanics): reproduce the exact operation on a local scratch server first, with production-shaped data — dotted keys, sentinels, blanks — since a clean-data repro can pass where production fails.
- When correlating production behavior with code history, treat each GitHub tag as a production release boundary and compare the relevant deployed tag diffs around the observed inflection.
- When running production code locally for investigation, only call read-only / side-effect-free functions (e.g., data-layer SELECT queries). Never call handlers or orchestrators that write data or trigger external side-effects without enabling their dry-run modes first — e.g., a job that persists its results and notifies customers.

### Tool Use & Scripting
- Prefer one script over repeated tool calls (MCP, SDK, or API — same thing here). When a task fans out the same call across many items, or produces bulky intermediate data you would otherwise discard, write a single script that makes the calls and returns only the distilled result — keeping raw payloads out of the model's context, the main token driver. Stay with direct tool calls when you genuinely need the intermediate values in context.
- A background waiter that polls `pgrep -f <label>` matches its own command line and spins forever, reporting a finished job as still running. Wait on the job's output file or a pidfile instead, cap every wait loop so a hang surfaces as a failure rather than silence, and read two status checks in a row that say "running" with no new output as a stall, never as progress.
- Treat permission errors and denied tool calls as intentional restrictions, not obstacles — deploys, cloud writes, and repo settings are gated on purpose (see Deployment & Infrastructure Safety). Never reach the same effect through an alternate route (another CLI or SDK, a script, other credentials): use the documented path if one exists, otherwise hand the user the exact commands to run.

### Deployment & Infrastructure Safety
- **NEVER deploy directly to staging or production** with the cloud provider's CLI or SDK (updating a function's code, deploying an infrastructure template, or any other command that modifies staging or production resources). All staging/production deployments go through the automated CI/CD pipeline.
- Per-developer **feature-branch deployments** are allowed when explicitly instructed by the user. A teardown script that mass-deletes staging infrastructure is run by agents only in its default discovery mode, never with its apply flag.
- The agent may **read** cloud resources (describe, get, list) for investigation purposes, but must **never write/update** staging or production infrastructure or its deployed code directly.
- Production database DDL and mutations are run by the user. Hand each over as a complete runbook in one message: the statement, the watch query with how done/stuck/failed read, and the cancel command as the escape hatch with its verification. One mutation at a time on large tables.
- Production config/data writes (account settings in the operational database, a shared application database, anything through an admin CLI): by default hand the user the exact ready-to-run command with every value filled in (a write-capable profile in it is fine), then verify the result read-only after it runs. Run the write yourself only when you hold the permission and the user told you to, in the current conversation: for this one command, or generally ("run it yourself"), or through a skill they invoked that calls for the write. Run its `--dry-run` first where the command has one. A run nobody attends (a cloud routine, `/afk`) puts the command in the PR description, or in the run's report when there is no PR; a routine scheduled on the user's own machine holds its write permissions on purpose and runs the writes its skill calls for. A database the run created for itself (a throwaway local one) is not production: write to it freely. A local dev stack is not such a database when it reads and writes shared stores.
- When fixing a production issue with unproven fixes, one PR carries one change — the single most promising, with minimal diff surface — not a bundle: changes bundled into one PR can't be attributed or rolled back individually on a running system. Let it prove itself before the next PR.
- **Model-provider rate caps are a security limit, not a performance setting.** A rate cap on the production model gateway is the exposure ceiling for what a runaway agent, an abusive user or a leaked key can spend, so a rate-limit error there is the limit doing its job. Never change those capacities: report the rate-limit rate and point the user at the doc that owns the numbers and how they are derived. Evals, benchmarks, dev, staging and previews run on a separate internal lane, never on the production one.
- **Never modify GitHub repository settings** (branch protection rules, required status checks, etc).
- An alarm's OK notification goes to the paging tool its alarm notification pages and nowhere else: the page closes itself, and the team chat sees one message per failure. Most alarms count single failures that return to OK a minute later, so an OK in chat would double every failure message and say nothing; whether an alarm is still active is read in the paging tool or the monitoring service.
- An alarm's name is the only thing the team chat and the paging app show of it, cut short, so its first 60 characters, up to ` - `, carry the priority and team its topics page and what broke for whom: `[P1][Backend] Checkout failing - payment step errored 2 runs in a row (canary_checkout)`; its description opens with what was detected at which threshold and window, then who is affected and where to look. A CI check holds the exact rules and fails on a title whose label disagrees with the topics it notifies.

### Customer data and processors
- In production, customer data leaves our infrastructure only for the approved processors the company has declared to its customers, in the location declared for each. Adding a processor, or a new location for one, is the user's decision, and its declaration goes out early enough for customers to object before it ships: stop at a merge-ready PR that names the vendor, the data it receives, and where it processes it. Reviewers flag a diff that adds such a path without that description.
- Production means what our code sends once deployed: code first exercised in dev, staging or a preview included. It covers every outbound path, including telemetry, email relays, proxies and a vendor's own AI features. Judge the host the code actually calls, not the vendor's name: some SDKs send to a default region unless configured otherwise.
- Internal work (the team running its own tools on a customer's data to deliver the contracted service) may use the short list of internal tools the company approved for it; any other service receives customer data only with the user's go, while synthetic data needs none. Internal work comes back in scope once its output is shared outside the team.
- Issue and PR bodies and comments may carry the account detail the work needs (the account's ID, the event or record names, counts), and personal data only as its kind and count, such as "3 email addresses", never the values. Anything else from a customer (conversations, transcripts, notes) stays out of the repository. Every service that reads the repository, review bots included, must be one your customers' data may go to. Commits, PR titles and branch names carry none of it.

---

## Repository Reference

This part is specific to each repository; fill it in for yours. What belongs here:

- **Overview**: what the product does in two sentences, and one bullet per service directory with its stack, lint, test and dev-server commands.
- **Environment**: the single source of truth for each language version, the shared virtualenv or workspace, and where to run each tool from (`cd <service> && pytest`, never from the root, when tests use relative paths).
- **Credentials**: agents use read-only identities (`READ_ONLY_PROFILE`) for all cloud and database access, and never switch to a different profile, role, or credential source without explicit user permission in the current conversation. When a read-only identity is missing on a machine, the agent points the user at the doc that provisions it and never substitutes another.
- **Local development**: the one script that starts the local stack, what it reads and writes, and what it must never write.

### Conventions

**Experimental folder (`experiments/`)** contains experiment and prototype artifacts: code, scripts, design docs, benchmarks and one-off tools created by individual team members. It is the boundary that distinguishes experiments from MVPs, platform work, and production code: nothing in it is used by automated pipelines, CI/CD, shared manual processes, or deployed services.
- **Skip** lint, test, or proactively maintaining code in `experiments/` — except when retiring a shared identifier (a pipeline handle, resource, env var): sweep it too, since those scripts run against real infrastructure and a stale allowlist still targets what you deleted.
- **Never** reuse code, patterns, style, or conventions from `experiments/` — it does not have to follow project standards.
- **Write all experiment/prototype artifacts** under `experiments/<username>/`, mirroring the repository's directory structure. Experiment design docs live under `experiments/<username>/<project>/docs`, alongside the prototype they describe.
- **Exception — `/prototype`.** A product change the user might keep is built on a branch of the real tree, so trying it is the real app and closing the draft PR discards it. A spike that must not sit on a production path still goes under `experiments/<username>/`.
- **Exception — model benchmark results.** The code of a model, effort, provider or harness comparison stays experimental, but its result — arms, figures, spend, per-case data — goes to the ledger `docs/benchmarks/` (one entry per benchmark), read before any new comparison and written by the `benchmark-models` skill, so a measurement is never repeated because its outcome lived only in a session.

**Design docs** for MVPs and major architecture/platform work live in `docs/design/` (experiment docs under `experiments/<username>/<project>/docs`). Use `/design` to create and `/design-review` to review them. They are **system documentation** — current state, not history — and **complement the code, not replace it**: record only what the code cannot show (the why behind decisions and still-relevant rejected alternatives; the dragons with their disposition — addressed / accepted / open; and, until launch, decided vs. open and built vs. pending). Anything the code already shows is cut in favor of a code pointer. Decisions belong to the user: a doc must never be where the user first learns one was made. When implementation diverges from a recorded decision, bring the divergence to the user and update the doc; when it merely fleshes out a decision already taken, leave the doc alone.

**Research** from the `state-of-the-art-research` skill lives in `docs/research/<topic>/`, with an index in `docs/research/README.md` read before any new research.

**Deploy & infrastructure code** lives in one deploy directory — templates, build specs, and deploy shell scripts — never under a service directory. A script written for one hand-run operation (a DNS cutover, a one-time data migration) is not deploy code: it goes under `experiments/<username>/`.

**Customer account references** — always write an account as its opaque `<ACCOUNT_ID>`, looked up rather than guessed, optionally with a non-personal label.

**Agent skills** live in the agent's skill folder; write them per `docs/handbook/WRITING_FOR_AI_AGENTS.md`. The `description` is the trigger the model matches on: it should fit every situation the skill is for and none it isn't. Never duplicate rules already in `AGENTS.md` — reference it as the single source; skills carry only skill-specific workflow. When adding, renaming, or changing the merge/review semantics of a developer-workflow skill, update the workflow catalog in the same PR.

---

## Background / Cloud Agent Notes

- When running as a background, cloud, or web agent, **always push changes to remote**: commit and push immediately after each turnaround.
