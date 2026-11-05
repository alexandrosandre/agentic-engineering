# ci-agents/

Agents (and a few deliberately agent-free workflows) triggered by GitHub Actions: an event in the repository starts them, they act through GitHub, and their whole definition (trigger, permissions, prompt, guardrails) is a file reviewed in a PR like any other code.

## Catalog

| Unit | Trigger | Agent? | What it does |
| --- | --- | --- | --- |
| [cicd-sheriff](cicd-sheriff/) | Weekday cron, manual, PRs touching it | Yes, strongest model | Keeps the README's CI badges green: diagnoses red `master` runs, prepares a fix PR through `autoreview`, hands it to a human to merge |
| [issue-triage](issue-triage/) | `issues: opened` | Yes, fast model | Labels, assigns and files every new issue; optionally hands it to the unattended issue agent |
| [public-api-docs](public-api-docs/) | PRs touching the public API | Yes, mid-tier model | Updates the OpenAPI spec and its version inside the PR that changed the API |
| [issues-in-progress](issues-in-progress/) | PR opened or edited | No | Moves the issues a PR declares to "In progress" on the board |
| [stale](stale/) | Daily cron | No | Marks and closes inactive issues and PRs |
| [agents-tests](agents-tests/) | PRs touching the agent tooling | No | Runs the test suites of [`tools/`](../tools/) and the sheriff's detector |

Each folder holds a `README.md` and a `workflow.yml` to install under `.github/workflows/`, plus the skill or script it runs. Workflows that run an agent use Claude Code's GitHub Action (`anthropics/claude-code-action`, pinned to a commit) with a `CLAUDE_CODE_OAUTH_TOKEN` secret, and neutral names for everything else (`CHAT_BOT_TOKEN`).

The unattended issue agent's own workflows (the sweep that starts a session per assigned issue, and the nudge that wakes it on review activity) ship with it in [alice-issue-agent](https://github.com/alexandrosandre/alice-issue-agent).

## The pattern

An agent in CI is a prompt with a trigger, a token and a tool list. Of the four, the trigger and the token decide what can go wrong, so they get the most care.

**Triggers.** Pick the narrowest event that carries the work: `issues: opened` for triage, path-filtered `pull_request` for doc sync, a cron for the sheriff. Skip drafts. Use `concurrency` groups so a long run is not overlapped by its own next schedule (the sheriff serializes repairs) while PR validation runs stay independent and cancel their predecessors.

**Permissions.** Declare `permissions:` per job, starting from `contents: read`, and give write scopes only to the job that writes. The sheriff splits detection (read-only, runs on PRs) from repair (write, runs only on schedule or an explicit manual dispatch from `master`), so a PR can test the whole detector without ever being able to start the agent that writes.

**Guardrails.**

- **Untrusted input is fenced, and the tool list does the real work.** Issue bodies, PR content, CI logs and commit messages are evidence, never instructions; the prompt says so, and the agent's tool allowlist makes it true. The triage agent can run `gh issue`, `gh label` and `gh project`, and nothing else.
- **Secrets the agent does not need never enter its environment.** A step's `env` only exposes what it references, so the chat token is read by the deterministic step after the agent exits; the agent writes a handoff file instead of calling the chat.
- **Privileged jobs run trusted code.** A job that holds a write token checks out `master`'s script, not the PR's; a PR job does not start the repository's MCP servers, whose commands are repository paths and would run the PR's own files with the job's tokens.
- **Third-party actions are pinned to a commit**, and a contract test fails the PR that adds a mutable tag to the sheriff. Repair credentials must never reach code behind a tag someone else can move.
- **The agent never merges.** Every PR an agent opens ends with a named human reviewer. Where the agent must hand work to another automation (triage handing an issue to the issue agent), a deterministic step does the hand-off, behind a repository-variable switch, so the hand-off can be turned off without editing a workflow.
- **The context is scoped.** A sparse checkout keeps the triage agent from loading the repository's `AGENTS.md`: a narrow task gets a narrow context.
- **Silence by default.** No message on green, no comment on no-change PRs.

**Testing the workflow itself.** A workflow that runs an agent with write access is worth a contract test: parse the YAML as text and assert the properties that matter (which job holds which permission, that repair cannot run on a PR, that the agent step never sees the chat token, that every action is pinned). [`cicd-sheriff/tests/test_cicd_sheriff_workflow.py`](cicd-sheriff/tests/test_cicd_sheriff_workflow.py) is the example; the detect job runs it on every PR that touches the sheriff.
