# Move issues with a PR to In progress

A deterministic workflow, no model involved, that moves an issue to "In progress" on the project board as soon as a pull request declares it.

| | |
| --- | --- |
| Trigger | `pull_request` opened, reopened or edited, same-repository and open PRs only |
| Permissions | `contents: read`, plus a fine-grained `PROJECT_BOARD_TOKEN` secret |
| Source | [`workflow.yml`](workflow.yml), [`issues_in_progress.py`](issues_in_progress.py) |

## Why it is in a catalog of agents

Because most PRs here are opened by agents. An agent that works an issue end to end opens the PR, but it does not think about the board, and a board that lags the work is a board nobody trusts. This closes the gap without asking any agent (or person) to remember: the PR description convention the agents already follow ("Fixes #N" when the PR finishes the issue, "Part of #N" when work remains, one line per issue) is the only input.

It is also an example of a principle that runs through this repository: when a step can be deterministic, it should not be an agent's judgment call.

## How it works

- The issue numbers come from `linked_issue_numbers` in [`tools/github-rest/rest.py`](../../tools/github-rest/rest.py), the same parser the PR skills use, so a line only counts when it *declares* the link (a list marker or bold is fine; the same words inside a sentence, a quote or a parenthesis, such as "does not fix #N", are not).
- An issue moves only from a status before work starts. One already In progress or Done, or closed, stays where it is.
- A number that resolves to nothing is reported, the others still move, and the job then fails so the bad reference is visible.
- The job checks out `master`'s script, never the PR's: it runs with a token that can write the organization's boards, and needs nothing from the PR but the event payload.
- Description edits trigger it too, since a description often gains its issue line after the PR opens.

## Wiring it up

- A fine-grained token as the `PROJECT_BOARD_TOKEN` secret (organization Projects read and write; this repository's Issues and Pull requests read). GitHub's workflow token cannot edit organization boards.
- Repository variable `PROJECT_BOARD_NUMBER`.
- The status names in the script (`In progress`, `Done`) set to your board's.
