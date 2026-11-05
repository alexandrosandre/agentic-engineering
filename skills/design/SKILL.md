---
name: design
description: Brainstorm design options for a feature and document the result. Use when the user asks to design a new feature or a major change to an existing one, compare implementation approaches, or create/update a design doc in docs/design/ or experiments/<username>/<project>/docs.
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---
# Design Doc

## When to Use
- Use when a user asks to design a new feature or a major change to an existing one.
- Use when a feature needs a design doc, whether before coding or to document an existing design.

## Purpose

The design process exists to find dragons: the failure modes, constraints, and unknowns that stay invisible until implementation. The process is done when every dragon found is addressed by the design, consciously accepted as a risk, or open with a concrete way to resolve it.

The doc is not a record of that process. It persists only what the code cannot show — the load-bearing whys, the dragon ledger, and where the work stands — per "What Goes in the Doc" below. The full analysis lives in the conversation.

## Instructions
1. Collect the feature name or description from the user.
2. Ask for the design category if it is not already clear:
   - **Experiment / prototype**: optimize for speed of learning and cheap disposal.
   - **MVP**: optimize for time to honest user feedback and a graceful path forward.
   - **Major architecture / platform change**: optimize for long-term correctness, lock-in, maintenance cost, running/infra cost, and external-contract stability.
3. If the scope is unclear, ask which areas of the codebase are involved.
4. Before analysis, check whether a prior prototype exists in docs or code in the design area, including prior design docs in `docs/design/` or `experiments/<username>/<project>/docs`. If a prototype, or a design that was abandoned or superseded by one already live, exists and the user wants a fresh design, name it and ask the user to delete it and start in a fresh session before continuing. Do not proceed with "ignore that folder" instructions; agents will still read it and be biased by it. A doc that describes a live system stays: a full rewrite gets a new doc rather than an edit of the old one (an edited doc leaves a reader unable to tell which parts still hold), and the old doc keeps describing the live system, with a pointer to the new one, until the rewrite launches; then delete it (git history keeps it), or keep only the parts that still hold and point the rest to the new doc.
5. Explore the relevant code to understand current patterns. A design doc — this one or any other — is a map, not evidence: before a decision rests on a claim it makes about the system (a behavior, a constant, a "handled by"), verify the claim against the current code; docs record what was true when written. This applies even when you are the agent who wrote the doc — your own earlier sessions' claims age exactly like anyone else's.
6. Annotate existing code as:
   - **Load-bearing**: interfaces, public contracts, data formats, or behavior the design must preserve unless the user explicitly decides otherwise.
   - **Replaceable**: implementation details that can change without breaking the load-bearing surfaces.
7. Lay out viable implementation options in the conversation. When one is a clear front-runner, recommend it and name the evidence that makes it one; when none is, say so instead of ranking them. A design that starts from a `state-of-the-art-research` report ranks and recommends its proposals as that skill sets.
8. Resolve open questions and decisions with the user, per "Decisions Are the User's" below. What stays unresolved is recorded as open in State, never silently decided by the agent.
9. Do not write the design doc until options and requirements are discussed and every recorded decision — inherited entries aside — was made by the user.
10. Once agreed, write the design doc in the right location:
    - Experiments / prototypes: `experiments/<username>/<project>/docs`.
    - MVPs and major architecture / platform changes: `docs/design/`. Follow "Doc Structure" below, not nearby docs — existing docs may not follow it.
11. After writing the doc, suggest the user run `/design-review` to review it. Once the design is finished, `/prototype` is another option: it builds a disposable version the user can try, with the doc's decisions as constraints.

Documenting an existing design (already built): step 4's fresh-design rule and the option brainstorm in steps 7-9 do not apply — the built system is the decided design. Record as-built choices as inherited decisions with their mined motivation, mine whys and dragons from the code, git history, and the user, and still bring dragon dispositions and anything unresolved to the user. Each mined motivation names where it was found (a PR, a design doc, a session transcript, a memory); one with no source is recorded as inferred or unknown, with what was searched, since every later session reads the doc's why as fact.

## Design Category

The process, brainstorming rigor, and doc structure stay the same for all design categories. The category only changes which risks to surface and what to optimize for.

| Context | Optimize For | Risks to Surface | Acceptable |
|---------|--------------|------------------|------------|
| **Experiment / prototype** | Speed of learning; cheap disposal | Whether it answers the question; whether it can be deleted cleanly; whether results generalize beyond toy data; dragons of the eventual production/fleet stage the experiment exists to de-risk (frame validations so they produce evidence about that stage, not only the prototype) | Lock-in, ugly code, no tests, ignoring scale, ignoring running/infra cost |
| **MVP** | Time to honest user feedback; graceful path forward | Sharp edges for first users; data model evolution; premature external contracts; vendor/library lock-in before the wedge is validated | Limited scale, deferred edge cases, light happy-path tests, narrow option set; running/infra cost is not an analysis dimension |
| **Major architecture / platform change** | Long-term correctness, lock-in, maintenance cost, running/infra cost, external-contract stability | Unknown unknowns; vendor/runtime constraints; cross-decision dependencies; external client surfaces; observability gaps; one-way doors; nonlinear cost shapes | Trade-offs dominated by maintenance and running cost over several years |

Running/infra cost is a first-class analysis axis only for major architecture / platform decisions. Ignore it for experiments and MVPs.

For experiment / prototype contexts, where the code and the throwaway docs go is `AGENTS.md` Conventions, including the `/prototype` exception.

## Option Analysis

The point of options analysis is to surface unknown unknowns: failure modes, dependencies, and constraints that would otherwise be invisible until implementation. Dragons are not "risks we'd handle in passing"; they are consequences we would not have seen without explicit option-by-option scrutiny. If the analysis surfaces no dragons, the analysis is not done.

For each decision:

- Include inherited decisions explicitly. If the design keeps an existing architecture, database, runtime, auth flow, or service boundary, surface that as a decision and say what was considered. Silent inheritance narrows the option space without telling the reader.
- Shortlist viable options. Keep the list small, but do not hide serious candidates.
- List candidates culled and why they were not serious.
- Compare trade-offs against the design category.
- Prefer existing architecture, programming language, database, and library dependencies unless a new one materially wins on the trade-off table. Justify each addition.
- For each option, list "here be dragons": specific complexity, unknowns, and failure modes.
- For MVPs and major architecture, each dragon must cite a source: code path, doc URL, production observation, or a measurement to take. Experiments may list uncited unknowns when the experiment is meant to answer them.
- List external-coupling surfaces per decision: public APIs, SDK methods, persisted formats, ingestion schemas, event names in customer data, or anything else that external clients may depend on. For experiments this is usually "None".
- Mark reversibility per decision: two-way door or one-way door.

Avoid during option analysis:

- Human-effort estimates: days, story points, sprints, or "this is a lot of coding". Coding labor and internal migrations are not decision factors; see `AGENTS.md` Migrations & Compatibility.
- "Phase 1 / phase 2 / experiment first" when the user asked for target architecture.
- New architecture, database, package, language, vendor, or cloud without an explicit justification line.
- Generic dragons such as "hard to operate" or "scaling may be risky".

Validations may be framed as questions, desk checks (`curl`, queries, doc lookups), or concrete experiments. Use whatever would most directly answer the uncertainty.

## Decisions Are the User's

The agent analyzes; the user decides. The doc must never be where the user first learns a decision was made.

- A **decision** exists only where the requirements leave more than one viable option. When the user's instructions or the stated requirements already determine the answer, it is a requirement or constraint — record it under Requirements, not as a decision.
- Bring each decision to the user with the candidates, trade-offs, and dragons, then ask. Use the agent's structured question tool when available; otherwise ask in chat. One decision per question: a batch gets answered as a block, and the later decisions are judged without the answers to the earlier ones.
- Decisions form a tree: many hang off another's answer. Bring a decision only once the decisions it depends on are settled — asked earlier, it rests on an assumption the user never made. When several are ready, the one that gates the most others goes first, a one-way door ahead of everything.
- A question that needs a fact — how the code behaves, what the data holds, what a tool reports — is the agent's to answer by looking it up, never the user's; only the decision goes to the user. While a lookup is pending, bring the decisions that don't depend on it.
- Assume the user holds unstated context — requirements and constraints they consider obvious. Ask for clarification and further input early instead of inferring silently.
- When a stated requirement carries risks or trade-offs the user may not have weighed, expose them and ask before designing around it. A confirmed requirement stays a requirement; the accepted risk goes to the dragon ledger.
- An agent preference is a proposal. Proposals live in the conversation until the user decides; the doc records only user-made decisions, with their motivation, plus inherited and as-built choices marked as such.

## What Goes in the Doc

The doc complements the code, never competes with it. Code is the less ambiguous record of what the system does and how. The doc records the two things code cannot show:

1. **Why** — the reason behind a decision, kept only when not knowing it could break the design or a requirement it fulfills: an invariant future changes must preserve, a constraint that forced the shape, or a tempting alternative rejected for a reason that still holds ("we don't use X because Y").
2. **Where we are** — what is decided vs. still open and built vs. pending, so a fresh session can continue the work. This part shrinks as work completes and is deleted when the doc reaches Launched.

Run every candidate sentence through these tests:

- **Code test** — does the code or a test already show it? Cut it, whatever the other tests say; where the reader needs an entry point, leave a `path/to/file.py` pointer instead of prose.
- **Ownership test** — does a sibling doc own this subject? Cite that doc instead, whatever the other tests say. A subject has exactly one owning doc: a fact stated in two places drifts, and the reader cannot tell which copy is current.
- **Breakage test** — could a future author who didn't know it break the design or silently drop a requirement? Keep it. Rationale that fails this test is trivia.
- **Resume test** — does a fresh session need it to continue the work? Keep it in State; delete it once the work is done.

A sentence that passes neither the breakage test nor the resume test is cut. The map a reader needs before opening the code — TL;DR, goal, requirements, the architecture shape — always passes: the code shows trees, not the forest.

Consequences:

- A **decided decision** is one short entry: the decision, its load-bearing why, the rejected alternative only when the rejection reason still matters, and a one-way-door mark where applicable. The trade-off tables, culled candidates, and per-option dragons that led there stay in the conversation.
- An **open decision** keeps its live analysis in the doc — the candidates still on the table, their trade-offs and dragons — because that is working state a future session resumes from. When decided, collapse it to a decision entry.
- A **dragon** carries its disposition: addressed (how — keep only when the mitigation could be mistaken for removable complexity), accepted (why the risk is taken — always keep; this is invisible in code), or open (the plan or measurement that resolves it).
- A **measured claim** — in a decision or a dragon's disposition — names the configuration it was measured under (semantics, thresholds, window) and reaches no further: one configuration's numbers support "did not, under X", never "cannot". When a decision changes, every entry whose evidence rests on the retired choice is unproven again: re-validate those entries under the new premises before further work builds on or tunes them. Later sessions resume from the doc, so an over-wide or stale claim steers them all.

## Doc Structure
- **Status** (Draft / In Review / Approved / Under Implementation / Launched), **Authors**, and **Design category** with its optimization target.
- **TL;DR** — 2-4 sentences: what the system does, the key decisions, the bottom line. A reader decides from this alone whether to read on.
- **Goal** — one paragraph: the problem and desired outcome. Note adjacent decisions intentionally out of scope when a reader would assume they are covered.
- **Requirements** — only those that shape the design: functional musts, non-functional ceilings (performance, scale, maintenance; running/infra cost for major architecture / platform decisions), hard constraints.
- **Design** — how the system works, present tense, at the level the code cannot show: component boundaries, data flow, invariants, external-coupling surfaces. Mermaid diagram when the design spans components. Code pointers for entry points.
- **Decisions** — one entry per load-bearing decision, with its motivation, per "What Goes in the Doc" and "Decisions Are the User's". Mark entries the user did not make in this design as inherited (pre-existing architecture, as-built choices).
- **Dragons** — the ledger: each dragon with its citation (per Option Analysis) and its disposition, per "What Goes in the Doc".
- **Notes** — optional, after Dragons: the long explanations the body would otherwise interleave — a mechanism's definition beyond one phrase, the reasoning behind a shape, a limit of the current system. The body keeps its reading flow and cites them as (Note N); a reader skips them on a first pass. Notes still pass the tests in "What Goes in the Doc".
- **State** — only until Launched: open decisions with their live analysis, pending and in-progress work (entries leave as they complete and become visible in code), unresolved questions, and pending validations (an open dragon's plan lives on the dragon, not only here). Delete the section at Launched.

## Writing Guidelines
- Present tense from the start ("the system does"); Status carries the lifecycle, not the prose.
- Assume the reader has the code open — and nothing else. Whys are stated in the doc, not referenced: a chat thread or a meeting is not a recorded why.
- Precise, unambiguous language. Distinguish requirements ("must"), constraints ("cannot"), and recommendations ("should").
- Length is cost: a doc nobody finishes protects nothing, and stale bulk rots faster than it helps. Every sentence must survive the tests in "What Goes in the Doc".

## Anti-patterns
Design docs are **system documentation** — not change logs, PR descriptions, or analysis transcripts. Avoid:
- Describing "previous state" or framing content as deltas ("We changed X to Y", "Previously X, now Y").
- Implementation steps or plan-style numbered sequences. Plans are not versioned, so that material does not belong in a persisted design doc.
- Narrating the development journey ("First we tried X, then switched to Y").

The doc must be understandable by a reader who never saw the old system and never saw the design conversation.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `design`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
