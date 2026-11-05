# simplify

**What.** A fresh-eyes review of the branch's own changed files for what they can lose without changing behavior: code nobody needs yet, logic the repository already has, constructs a cold reader trips on, and work done twice. It fixes what it finds with behavior-preserving rewrites and verifies with targeted lint and tests.

**Why.** Agents write working code that is often longer than it needs to be: a hand-rolled helper next to an existing one, a defensive branch for a value the caller guarantees, a comment restating the next line. A pass with no session context sees the code the way the next reader will. Its guard rails matter as much as its checklist:

- **Scope is only what the author changed on the branch**, never files that came in through a merge from the base.
- **Behavior-preserving only.** What other code relies on (inputs, outputs, writes, errors, public interfaces) stays as it is, and code that fast local tests cannot verify (infrastructure templates, access policies, tuned SQL) is left alone.
- **Parallel mechanisms are reported, not merged.** A new flag that serves a goal an existing setting already serves is a design decision for the user.
- Extraction follows the rules' bar: only non-obvious logic used more than twice.

**How it fits.** The agent runs it before each commit (a pre-commit habit in the rules or a hook), and on request. It complements `/contextual-review`, which owns intent.

**Wire up.** Nothing beyond the linters and test commands your `AGENTS.md` names.

**Origin.** Written by the author from this repository's engineering rules (`rules/AGENTS.md`, Code Style and Testing & Verification): a branch-only scope, what must not move, four questions in the order they settle each other, targeted verification, and parallel mechanisms reported instead of merged. Coding agents ship cleanup passes of their own; this one shares no text with them.
