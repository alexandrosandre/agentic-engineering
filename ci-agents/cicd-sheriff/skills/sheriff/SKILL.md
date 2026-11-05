---
name: sheriff
description: Alias for review-alarms — the on-call sheriff's production alarm review. Use when triaging alarm notifications, reviewing active alarms, or debugging alarm patterns.
disable-model-invocation: true
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---

# Sheriff (alias)

`/sheriff` is an alias for `review-alarms` — the on-call sheriff's review of the monitoring service's alarms (it stamps every issue/PR with the `Sheriff` label).

Invoke the `review-alarms` skill now and follow it end to end, forwarding whatever input the user passed to `/sheriff` (alarm notification, alarm URL, resource name, or none). That skill is the single source of truth for the workflow, priority framework, and label convention — nothing is duplicated here.

## Closing

- If this skill's instructions failed or needed a workaround, update this file.
