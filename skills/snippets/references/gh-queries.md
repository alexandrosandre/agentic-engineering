# GitHub harvest queries

All searches go through `gh api search/issues`. Two hard rules:

1. **Always pass `-X GET`.** With `-f` params alone, `gh api` switches to POST and the search endpoint returns 404. This is the single most common failure mode of this skill.
2. Always request labels: they drive categorization (`Sheriff`, `P0`, `Bug`, `infra`, per-customer labels...).

Shared setup (dates are the DONE window, `YYYY-MM-DD`, UTC):

```bash
LOGIN=$(gh api user --jq .login)
JQ='.items[] | {number, title, state, labels: [.labels[].name]}'
SEARCH() { gh api -X GET search/issues -f q="repo:<org>/<repo> $1" \
  -f per_page=100 --paginate --jq "$JQ"; }
```

## Done facets

| Facet | Query |
| --- | --- |
| PRs merged | `is:pr author:$LOGIN merged:$A..$B` |
| PRs closed unmerged | `is:pr author:$LOGIN is:unmerged closed:$A..$B` (report only if notable, e.g. superseded work) |
| Issues created | `is:issue author:$LOGIN created:$A..$B` |
| Issues closed | `is:issue author:$LOGIN closed:$A..$B` — also run the `assignee:$LOGIN -author:$LOGIN` variant (see confirmation below) |
| Issues commented | `is:issue commenter:$LOGIN -author:$LOGIN updated:$A..$B` |
| PRs still open | `is:pr is:open author:$LOGIN created:$A..$B` — see staleness check below before reporting. Older open PRs (created pre-window) surface via their in-window sessions (Step 3), not this query |
| PRs reviewed | `is:pr reviewed-by:$LOGIN -author:$LOGIN updated:$A..$B` — candidates only, see below |

A PR reported "(en curso)" will reappear as merged in the next period's report — that is intentional (progress → done), not double-counting. PRs merged after the window report only in the period they merge.

## Still-open PR staleness check

A still-open PR is not automatically "the work happened, en curso" — a draft opened and then abandoned is not ongoing work. Check before reporting:

```bash
gh pr view $N --json isDraft,createdAt,updatedAt --jq '{isDraft, createdAt, updatedAt}'
```

Drop it (don't report in Coding or To Do) when `isDraft` is true AND `updatedAt` equals (or is within minutes of) `createdAt` — i.e. no activity since it was opened. A non-draft PR, or a draft with real follow-up activity (commits, comments, review requests after creation), is genuine ongoing work — keep it.

## Reviewed-PR confirmation

GitHub search has no review-date qualifier, so `updated:` over-matches (a PR touched today surfaces even if the runner reviewed it months ago). Confirm every candidate and keep only PRs with a review submitted inside the window:

```bash
gh api --paginate "repos/<org>/<repo>/pulls/$N/reviews" \
  --jq "[.[] | select(.user.login==\"$LOGIN\") | .submitted_at]"
```

## Assignee-closed issue confirmation

Where issues are routinely co-assigned to several people (a lead alongside the actual owner), `assignee:$LOGIN -author:$LOGIN` badly over-matches: many hits are tickets the runner was never actually part of. Never report one of these from assignee status alone. Before reporting, confirm real involvement — at least one of:

```bash
gh issue view $N --json comments --jq "[.comments[] | select(.author.login==\"$LOGIN\") | .createdAt]"
gh pr view <linked-PR> --json reviews --jq "[.reviews[] | select(.user.login==\"$LOGIN\")]"
```

- The runner has a comment on the issue itself, OR
- The runner authored or reviewed the PR that closed it.

An empty result on both means the runner was a bystander co-assignee — drop the issue entirely, don't fold it into a bullet. This applies per-issue, not per-batch: a co-assignee pattern on one ticket does not clear the others.

## Issue-comment confirmation

The issues-commented facet over-matches the same way: `updated:$A..$B` fires when *anyone* touches the issue, even if the runner's comment is months old. Confirm every candidate and keep only issues where the runner commented inside the window:

```bash
gh api --paginate "repos/<org>/<repo>/issues/$N/comments" \
  --jq "[.[] | select(.user.login==\"$LOGIN\") | .created_at]"
```

## Closed issue ≠ done

Never report a closed issue as fixed from its state alone — closure signals are loose. Before claiming a fix, verify:

```bash
gh issue view $N --json stateReason,labels,closedByPullRequestsReferences,comments
```

- `stateReason` `NOT_PLANNED`/`DUPLICATE`, or the `Stale` label → discarded: never report as done (drop it, or report the decision itself if notable).
- `stateReason` `COMPLETED` is **not** sufficient: `closedByPullRequestsReferences` also lists unmerged PRs — require the linked PR to be MERGED (`gh pr view <n> --json state,mergedAt`).
- No merged PR → read the last comments: a terse deprioritization ("P3", "wontfix", "dup") means discarded; an actual answer or operational/config resolution means done.
- Fix merged after the window → the fix belongs to the next period's report; this period reports only the diagnosis.
- Still unclear → claim only what is certain ("diagnosticado", "investigado"), never a fix.

## Sheriff detection

`updated:` would over-match here like everywhere else (anyone touching an old still-assigned Sheriff item would flip the star). Use window-precise qualifiers instead — sheriff-duty output is created or closed during the duty window:

```bash
for Q in "created:$A..$B" "closed:$A..$B"; do
  gh api -X GET search/issues -f q="repo:<org>/<repo> label:Sheriff assignee:$LOGIN $Q" \
    -f per_page=100 --paginate --jq '.items[].number'
done
```

Any hit → the runner did sheriff duty this period → "Bugs/Cleanups (⭐ Sheriff!)". The sheriffing skills always apply the `Sheriff` label **and assign the sheriff** on the issues and PRs they create — both halves matter, since `assignee:` does not match author-only items.

## To Do facets

The source of truth for in-progress and next work is the board: the team's GitHub Project (`<project board>`, in org `<org>`). Open/draft PRs are **not** a To Do signal — drafts can sit stale for months — and neither is being a co-assignee on an issue someone else drives. Requires the `read:project` token scope (`gh auth refresh -s read:project`).

```bash
PROJECT=$(gh project list --owner <org> --format json \
  --jq '.projects[] | select(.title=="<project board>") | .number')
gh project item-list "$PROJECT" --owner <org> --format json --limit 1000 \
  --jq '.items[] | select((.assignees // []) | index("'"$LOGIN"'"))
        | [.status, (.content.number // ""), ((.labels // []) | join("|")), .title] | @tsv'
```

`.assignees` is a flat login array and `.content.number` the issue/PR number (`.labels` can be null — use `(.labels // [])` if projecting it). Statuses are the board's columns: `To do`, `Next`, `Planned`, `Bugs`, `In progress`, `Done`. An issue moves to `In progress` when a PR declares it (the issues-in-progress CI agent in `ci-agents/`).

Report `In progress`, `Next`, `To do`, and non-`Stale` `Bugs` items. Skip `Done`, and skip `Blocked`/`Stale`-labeled or long-horizon `Planned` items unless clearly imminent. Prefix the bullet with `P0:` when the item carries the `P0` label.

## Label list (customer detection)

```bash
gh api -X GET repos/<org>/<repo>/labels -f per_page=100 --paginate --jq '.[].name'
```

Fetch once per run; never hardcode customer names (the list churns). Process labels (`P0/P1/P2`, `Bug`, `Enhancement`, `Chore`, the scope labels, `Sheriff`, `Stale`, `Blocked`, ...) are not customers; treat brand/organization-looking labels as customers.
