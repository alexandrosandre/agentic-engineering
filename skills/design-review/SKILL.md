---
name: design-review
description: Review and refine a design doc. Use when the user asks to review, critique, or advance the status of a doc in docs/design/ or experiments/<username>/<project>/docs.
license: CC-BY-4.0 AND MIT
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
  adapted_from: https://github.com/EveryInc/compound-engineering-plugin
  upstream_license: MIT
---

# Design Review

Adapted from the document-review skill in EveryInc/compound-engineering-plugin (MIT, Copyright (c) 2025 Every); changes by Alexandros Andre Chaaraoui.

Improve design docs through structured review at any stage of the lifecycle. A review has two jobs, in this order:

1. **Find what the analysis missed** — dragons, unstated assumptions, missing load-bearing whys.
2. **Cut the doc to the result** — everything the "What Goes in the Doc" tests in the sibling `/design` skill (`../design/SKILL.md`) reject. An overgrown doc gets skimmed instead of read and fills agent context with rot, so cutting is review work, not cosmetics.

"Dragons" means concrete failure modes, complexity, and unknowns, matching the term used by `/design`.

## Step 1: Get the Document

**If a document path is provided:** Read it, then proceed to Step 2.

**If no document is specified:** Ask which design doc to review, or look for the most recent `Draft` or `In Review` doc in `docs/design/` and experiment docs under `experiments/<username>/<project>/docs`.

## Step 2: Assess

Read the doc alongside the code it describes — the code test cannot be run from the doc alone. When the doc sits in a **subfolder** of `docs/design/`, read its siblings there too: that folder groups docs about one system, so the boundary between them cannot be judged from one doc alone. Docs directly under `docs/design/` are unrelated top-level designs and have no such boundary. Then simulate a fresh session holding only the code and this doc (the resume test):

- Would it **break something** because a why is missing? A non-obvious design shape with no recorded reason is as much a finding as excess prose.
- Could it **continue the work** — does the doc say what is decided vs. open and built vs. pending, and does that match git and code reality?
- What would it **learn faster and less ambiguously from the code** than from the doc? Those passages are cut candidates.

Then probe the design itself:

- Is the problem stated precisely? Do the requirements match the stated design category (experiment / prototype, MVP, major architecture / platform)?
- Are there dragons the analysis missed — unstated assumptions about scale, existing behavior, or data shapes; blast radius; interactions between decisions; data migrations and their rollback; external-coupling surfaces (public APIs, SDK methods, persisted formats, ingestion schemas)? A non-trivial design with no dragons recorded anywhere signals unknown unknowns were not probed — though a small design whose dragons were all neutralized may legitimately carry a thin ledger.
- Are decisions inherited from the existing codebase surfaced as decisions?

Note findings. Don't fix yet.

## Step 3: Evaluate

Check the doc against these criteria; failures become findings:

| Criterion | What to Check |
|-----------|---------------|
| **Result, not process** | Decided decisions are collapsed to decision entries; no trade-off tables, culled candidates, or per-option dragons remain for anything already decided |
| **Complements the code** | Nothing the code or a test already shows; code pointers instead of prose; no implementation details (helper names, internal type shapes) |
| **One owner per subject** (subfolder docs only) | Nothing a sibling in the same subfolder owns is restated — cite it by path; a why or a dragon lives with the decision it belongs to, not in whichever doc noticed it. Two docs claiming one subject means one is the authority and the other cites it |
| **Load-bearing whys** | Every recorded rationale passes the breakage test — and every non-obvious design shape has its why recorded |
| **Decision provenance** | Non-inherited Decisions entries record the user's motivation; entries that look agent-decided and are not marked inherited are re-surfaced to the user for confirmation or re-opening |
| **Dragon quality** | Dragons are concrete and cited (code path, doc URL, production observation, or a measurement to take), not generic; each carries its disposition, whose evidence still holds under the doc's current decisions — a disposition measured under a since-retired choice is a staleness finding; for experiments only, uncited unknowns are allowed when the experiment answers them |
| **State current** | Decided/open and built/pending match git and code reality; State section deleted when Launched |
| **Clarity** | Goal is unambiguous; no vague language ("probably", "might need to", "consider") |
| **Category fit** | Design category stated up front; dragons and optimization target match it; requirements cover the category's non-functional axes (running/infra cost only for major architecture / platform) |
| **Specificity** | Design is concrete enough to implement without re-designing mid-sprint |
| **Open-option quality** | For undecided decisions: honest pros/cons; no single recommended path unless the user explicitly asked for one |
| **YAGNI** | No speculative scope; simplest approach that meets stated requirements |
| **No effort estimates** | No human-days, story points, sprints, or "too much code" reasoning |
| **Timelessness** | Present-tense system documentation; no "previous state", "before this branch", or "we changed X to Y" framing — especially when status is Under Implementation or Launched |

## Step 4: Identify the Critical Improvement

Among everything found in Steps 2–3, does one issue stand out that would meaningfully block or derail implementation? If so, this is the "must address" item. Highlight it prominently before listing minor findings.

## Step 5: Make Changes

Present your findings, then:

1. **Auto-fix** (git history preserves cut content, so cuts are recoverable):
   - Vague language; historical/delta framing rewritten to present-tense system description.
   - Prose failing the code test — cut, or replaced by a code pointer.
   - Analysis behind decided decisions — collapsed to a decision entry that keeps the load-bearing why.
   - Stale State entries (built items still listed as pending, decided items still listed as open) — removed or corrected against git and code reality. In legacy docs state may live as Open questions or inline status notes; treat those the same.
   - Legacy sections reshaped toward `/design`'s "Doc Structure" when their content moves anyway (collapsed decisions land in Decisions, risks in Dragons); don't churn sections that already work. List every cut and collapse in the chat summary so the user can veto. Cutting and collapsing are not removing: both carry forward any why or dragon embedded in the affected passage that passes the breakage test — when unsure, carry it forward. Approval is needed only to drop one entirely.
2. **Ask approval** before: removing a why or a dragon the code does not show (a wrong call about what is load-bearing loses real information), restructuring an open decision's live analysis, changing the selected approach, altering requirements.
3. **Update** the doc inline — no separate files, no review-metadata sections.

## Step 6: Offer Next Action

After changes are complete, ask:

1. **Refine again** — Another review pass
2. **Advance status** — update Status in the doc header to match reality (`In Review`, `Approved`, `Under Implementation`, `Launched`); advancing to `Launched` also deletes the State section
3. **Review complete** — Exit without status change

### Iteration Guidance

After 2 passes, recommend completion—diminishing returns are likely. Allow further iteration if the user wants it.

Return control to the caller (workflow or user) after selection.

## What NOT to Do

- Do not rewrite retained content for style; the author's voice stays. The tests decide what is retained — cutting a whole code-mirroring passage is cutting, not restyling
- Do not add new requirements or options the user hasn't discussed
- Do not produce a separate "review summary" file
- Do not change the user's selected option without explicit user approval

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `design-review`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
