# editor-hooks

An after-response hook that makes a cloud agent session's work durable: after every answer, it commits anything the agent left uncommitted and pushes anything unpushed.

| File | Role |
| --- | --- |
| [`hooks.json`](hooks.json) | An example registration of the hook on an after-response event. It is not any one agent's format: copy the idea into your editor's or agent's own hook config, whose file name, schema and event name vary. |
| [`sync-after-response.sh`](sync-after-response.sh) | The hook: reads and discards the event JSON on stdin, then commits the changes to tracked files (`git add -u`, so a stray new file is never committed) with `chore: agent session sync` and pushes, creating the upstream branch when there is none. |

## Why

A cloud agent session runs in a container that disappears. Agents are told to commit and push after every turn (the repository's `AGENTS.md` says so for background and cloud agents), and they mostly do, but "mostly" is the problem: the turn where the agent forgot is the turn whose work you lose. A hook does not forget. It is the rule turned into a mechanism, which is the general move this repository keeps making: when a rule keeps being broken, stop restating it and make the mistake impossible.

## Guardrails

- **Cloud only.** It does nothing unless `CLOUD_AGENT` is set (put it in the cloud agent's environment secrets). In a local session, uncommitted changes are a developer's work in progress, and auto-committing them would be hostile.
- **Never blocks the session.** Push failures (a diverged branch, missing access) are reported and swallowed; the hook always exits 0.
- **Pushes the branch it is on, whatever it is.** It relies on the session working on a feature branch, which the repository's rules require; pair it with branch protection on `master`.

## Wiring it up

Register the script on your coding agent's after-response (or session-stop) hook event, and set `CLOUD_AGENT=1` in the cloud environment only.
