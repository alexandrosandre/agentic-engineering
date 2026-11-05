# tools/

The small programs the skills, routines and CI agents rely on. Each one exists because a recurring agent task needed a deterministic step: something that should be computed, not reasoned about, or a capability the agent did not have.

| Tool | What it is | Relied on by |
| --- | --- | --- |
| [transcripts](transcripts/) | Locate agent session transcripts; extract only what the user typed | `contextual-review`, `dream`, `snippets` |
| [rule-bench](rule-bench/) | Replay real prompts under rule variants, blind-judge the answers, test the difference | `dream` (before a rule about what the agent answers lands) |
| [web-reader](web-reader/) | MCP server returning the full text of a public page or PDF, in chunks, public addresses only | `state-of-the-art-research`'s web-researcher subagent |
| [github-rest](github-rest/) | PR operations over REST with `gh`-shaped output, working in cloud sessions where GraphQL is blocked | `create-pr`, `autoreview`, `ship-it`, `lgtm`, the issues-in-progress workflow |
| [test-runner](test-runner/) | Run the checks CI would run, for only what the branch changed | `test`, `contextual-review` |
| [cloud-agent-boot](cloud-agent-boot/) | Cloud agent install command that exits in under a second when no dependency file changed | Every cloud agent session |
| [editor-hooks](editor-hooks/) | After-response hook that commits and pushes whatever a cloud session left behind | Every cloud agent session |

The skills live in [`skills/`](../skills/); the [CI sheriff's detector](../ci-agents/cicd-sheriff/check_readme_workflows.py) lives with the sheriff.

## Conventions

- **Python standard library first.** Only the web reader has third-party dependencies (`lxml`, `pypdf`); everything else runs on a bare Python 3.
- **Tested where it is not glue.** Every Python tool has a `tests/` folder, run together by [agents-tests](../ci-agents/agents-tests/) on PRs that touch them. Fixtures are synthetic.
- **Read-only by default.** Tools that an agent calls while reading untrusted content (pages, transcripts, CI logs) read and print; the ones that write (`github-rest`, `editor-hooks`) do only the one thing their caller asked.
- **Placeholders are named.** Where a tool called an internal service or an agent other than Claude Code, it calls a clearly named stub or constant (`read_only_cloud_env` in rule-bench, the IDE agent's block with `IDE_AGENT_HOME` in transcripts) with a `TODO` saying what to wire.
