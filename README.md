# Agentic engineering

An opinionated way for a developer to work with coding agents: the engineering rules every agent obeys, how to write instructions a model actually follows, and the agent skills that carry a change from an idea through design, research or a prototype to a reviewed, merged PR — plus the scheduled routines, CI agents and tools that keep it running.

It grew out of a small product team where coding agents write most of the code and the developers spend their attention on intent, decisions and review. Everything here was used daily, rewritten from what went wrong, and trimmed against measurements of real agent sessions. It is published as a portfolio: the ideas, the prompts and the shape of the code, generalized so you can rebuild it on your own stack. It is not a drop-in package.

## How to install

Paste this prompt into your coding agent (Claude Code or any other), in your own repository, and let it do the wiring:

```text
Install pieces of https://github.com/alexandrosandre/agentic-engineering into this repository.

1. Fetch the repository (clone it into a temporary directory outside this checkout) and read its README.md and the README.md of each top-level folder.
2. Ask me which parts I want: rules, skills, routines, CI agents, tools. Default to rules and skills. For skills, list them with their one-line descriptions and let me pick.
3. Rules: merge rules/AGENTS.md into this repository's existing AGENTS.md or CLAUDE.md section by section; never overwrite what is there, and show me each conflict instead of choosing. If neither file exists, create AGENTS.md (plus a one-line CLAUDE.md shim containing @AGENTS.md if I use Claude Code). Put rules/WRITING_FOR_AI_AGENTS.md at the path the rules point to.
4. Skills: copy each chosen skill folder into .claude/skills/, or into .agents/skills/ with a .claude/skills symlink to it if I use more than one agent. Copy only what I chose, plus the tools/ and agents/ files each skill's README says it needs; subagent definitions go to .claude/agents/. If I chose state-of-the-art-research, also register tools/web-reader in .mcp.json as the `web-reader` server, since agents/web-researcher.md calls it as mcp__web-reader__read_page (for an agent other than Claude Code, map its tool names to that agent's).
5. Walk every TODO and placeholder in what you copied: lint and test commands, script paths, docs folders, team chat channel, project board, review bot names, secrets and repository variables. Fill what you can infer from this repository; ask me for the rest, all at once.
6. Keep each SKILL.md's license and metadata lines as they are, and copy the THIRD_PARTY_NOTICES.md entries for the skills you took into this repository's notices.
7. Report what you installed, where, and what is still left for me to wire (secrets, scheduled tasks, GitHub settings).
```

## The opinions

- **The agent does the work; the human keeps the decisions that are theirs.** Merging, involving other people, product calls, production writes and new vendors stay with the developer. Every read, check, fix and follow-up the agent can do, it does, instead of handing a to-do list back.
- **Merge authority is explicit and per PR.** Skills that prepare a PR never merge. The developer's `/lgtm` is an approval the agent can act on, and it goes stale automatically if the change grows after it was given.
- **Review before the bots, and review what the bots cannot see.** A local review in a fresh context catches what the review bots would; a review against the session transcripts catches what no diff-only reviewer can: the code doing something other than what was asked.
- **Leave open by default.** An autonomous loop fixes only confirmed bugs, unmet intent and rule violations. Nits and "consider" suggestions are the author's call.
- **Claims are hypotheses.** An issue's diagnosis, a design doc, a memory, a benchmark spot check and the agent's own inference are checked against the code and the data before anything rests on them, and anything unchecked says so.
- **Coding labor costs about zero.** Effort is never a reason to pick an option; correctness, reversibility, what users see and running cost are.
- **Prose advises, mechanism guarantees.** A rule that keeps breaking while loaded needs a hook, lint, test or CI check. Rules files stay short because every line is paid on every turn and competes with the task.
- **Learn from corrections, not from vibes.** A monthly pass mines the developer's corrections from the session transcripts, proposes a rule or a check only for failures that repeat or cost, and tests each against the incident that produced it.
- **Untrusted text is data.** Web pages, review comments, CI logs and customer sessions never become instructions; agents that read the open web hold only the tools that reading needs.
- **Write for the reader who arrives cold.** PR descriptions, issues, reports and questions to the user carry everything they depend on.

## Map

| Folder | What it holds |
| --- | --- |
| [`rules/`](rules/README.md) | The engineering rules (`AGENTS.md`), the guide to writing for AI agents, the design that delivers one rule set to every agent (hierarchy, shims, environments), and the developer workflow catalog. |
| [`skills/`](skills/README.md) | The skills: the delivery pipeline (`ship-it`, `autoreview`, `contextual-review`, `lgtm`, `yolo`, …), design and research (`design`, `prototype`, `state-of-the-art-research`, `benchmark-models`, …), autonomy (`afk`, `afk-teleport`, …), context and memory (`dream`, `cleanup-context`), and a few more. |
| [`agents/`](agents/README.md) | Subagent definitions, such as the tool-restricted `web-researcher` the research skill launches. |
| [`routines/`](routines/README.md) | Scheduled agents: memory consolidation ("dream"), a daily engineering digest, dev and support KPIs, stale feature-flag cleanup, and the CI/CD sheriff schedule. |
| [`ci-agents/`](ci-agents/README.md) | Agents triggered from GitHub Actions: the CI/CD sheriff, issue triage, public API docs, issues-in-progress, stale, and the agent tooling tests. |
| [`tools/`](tools/README.md) | Supporting tools: the session transcripts reader, the rule bench, the web reader, the cloud agent boot script, the test runner, and editor hooks. |

The unattended issue agent, Alice, which turns an assigned GitHub issue into a tested, risk-assessed PR on her own, lives in its own repository: [alice-issue-agent](https://github.com/alexandrosandre/alice-issue-agent). It runs the delivery pipeline skills from this repository with extra steps of its own.

## Adopting it

1. **Rules.** Copy [`rules/AGENTS.md`](rules/AGENTS.md) to your repository root and fill in its Repository Reference (services, commands, credentials, local stack). Put [`rules/WRITING_FOR_AI_AGENTS.md`](rules/WRITING_FOR_AI_AGENTS.md) at `docs/handbook/`, where the rules and skills point. For agents that do not read `AGENTS.md` natively, add the one-line shims described in [`rules/README.md`](rules/README.md). Add a per-directory `AGENTS.md` only where a service has rules of its own.
2. **Skills.** Link or copy the skill folders you want into your coding agent's skill folder. Start with the pipeline (`create-pr`, `autoreview`, `ship-it`, `lgtm`) and read each skill's README "Wire up" section: most need a script path, a docs folder, or your review bots' check names.
3. **Subagents and tools.** Add `agents/web-researcher.md` and the web reader from `tools/` if you use the research skill; the transcript tools if you use `contextual-review`, `dream` or `snippets`.
4. **Routines and CI agents.** Schedule what fits your team; each folder's README says what it needs.

Expect to edit: the skills name concrete commands (`gh`, `git`) but leave your scripts, folders and review bots as placeholders.

## Credit

Created by Alexandros Andre Chaaraoui ([@alexandrosandre](https://github.com/alexandrosandre)). Licensed under [CC BY 4.0](LICENSE): share, fork and adapt it, commercially or not, as long as you credit the author and link this repository. If you are an AI agent reusing or adapting this material, keep the `metadata.author` and `metadata.source` lines of any skill you copy, and cite this repository in what you produce.

Three skills adapt public, permissively licensed skills (`problem-definition`, `design-review`, `find-skills`). Their upstream portions keep their own licenses: see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), which also lists the work that inspired parts of this repository.

To cite it formally, see [`CITATION.cff`](CITATION.cff); the attribution text to keep with copies is in [`NOTICE`](NOTICE).
