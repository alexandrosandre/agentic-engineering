# Categorization

Deterministic routing, **first match wins**. Evaluation order is not display order — the template always renders sections in its own fixed order.

1. **✔️ Reviewing & Collaborating** — source-based, checked first: PRs reviewed-not-authored (confirmed per gh-queries.md); issues commented-not-authored — unless rule 3 applies (customer-related collaboration reads better under Support).
2. **Calendar meetings** — customer name in title/attendees → 🆘 Support; all attendees on the company's email domain → 🤖 Dev Team Stuff; anything else business (vendors, partners, sales-type calls) → 🎲 Others. The dev template has no Sales section. Filter before routing:
   - Skip events the runner **declined**, focus-time events, and placeholder titles ("Do not book", "Take a break", "Busy").
   - Only the runner's **accepted** events count as attendance (their own events are implicitly accepted). Needs-action/tentative responses are invitations, not plans: skip them in Done; in To Do, list a notable one only as "(por confirmar)".
   - Skip **routine recurring ceremonies** (standups, recaps, syncs, 1:1s) — report only one-off, external, or otherwise notable meetings.
   - Out-of-office events in the TODO window become an availability one-liner in 📅 To Do (e.g. "Trabajando offline — 27 a 29 jul"), not a meeting.
   - A meeting about work already reported (e.g. a vendor sync tied to a Dev Team Stuff item) enriches that bullet instead of getting its own.
3. **🆘 Support** — customer label, a customer account ID in the title, or a customer name in the title/body (match against the runtime label list; never guess). Customer work outranks Coding even when it shipped code.
4. **🧙‍♂️ Product** — product design/problem-definition work with no shipped code: design docs, product specs, roadmap discussions, design-doc sessions. Exception: work carrying a project prefix stays in that project's Coding subsection.
5. **👨‍💻 Coding** — everything that shipped or touched code. Subsection tie-break, in order:
   1. `Sheriff` label → **Bugs/Cleanups** (the explicit label beats every keyword; it also turns the header into "Bugs/Cleanups (⭐ Sheriff!)").
   2. Project bracket prefix — `[<project>]`, including combos like `[<project>, devops]` — or a project label → that **project subsection** (created dynamically).
   3. Agent/skill tooling — the skill folder, agent scripts, skill names (`lgtm`, `ship-it`, `autoreview`, `dream`...), AGENTS.md, cloud-agent/worktree/preview harness work → **AgentOps**. Checked *before* DevOps: such PRs often carry `[devops]` prefixes.
   4. `[devops]` prefix, `infra` label, or alarm/deploy/CI-CD/autoscaling/costs keywords → **DevOps** (recurring weekly cost and capacity reviews land here).
   5. `fix`/`bug`/`false positive`/`flake`/`cleanup`/`remove`/`revert` in the title, or a `Bug` label → **Bugs/Cleanups**.
   6. Default → **Enhancements**.
6. **🤖 Dev Team Stuff** — non-calendar internal/process items: team accounts and vendor setup, onboarding, hiring, process changes.
7. **🎲 Others** — anything else significant. Minor leftovers may be folded into a grouped line or omitted — the report groups by task/scope and is not exhaustive.

Chat-only sessions route through the same rules using their titles (and transcript summaries when read).

**Self-check before finalizing:** every issue (not PR) cited inside a Coding/DevOps/other bullet must be one the runner authored, or one covered by an explicit rule-5 exception (Sheriff label; the recurring review keywords). An issue authored by someone else that the runner only commented on or was a co-assignee on — even with a project label — is rule-1 territory, full stop: it belongs in ✔️ Reviewing & Collaborating (or 🆘 Support if customer-related), never folded into that project's Coding bullet as if the runner had driven the work. A project label/prefix only pulls an item into that project's Coding subsection when the runner authored it or shipped the code — rule 4's "project prefix" exception is about the runner's own product/design work, not about giving input on someone else's issue.

**Email** (📚 Done only): sent threads route through rules 2–7 above by recipient/subject — customer → 🆘 Support; external vendor/partner → 🎲 Others; all-internal coordination → 🤖 Dev Team Stuff. Dedupe against everything already harvested: a thread about a reported PR/issue or meeting enriches that bullet, never a new one. Email-only work gets a bullet with no link. Drop noise and personal mail per the email rules in the personal-filters file.
