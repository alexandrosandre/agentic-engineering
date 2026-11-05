---
name: problem-definition
description: Help users define problems clearly before jumping to solutions. Use when someone is scoping a new feature, validating a product idea, struggling to articulate what they're building, or falling into the "shiny object trap" with new technology.
license: CC-BY-4.0 AND MIT
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
  adapted_from: https://github.com/RefoundAI/lenny-skills
  upstream_license: MIT
---

# Problem Definition

Adapted from the problem-definition skill in RefoundAI/lenny-skills (MIT, Copyright (c) 2025 Refound AI); changes by Alexandros Andre Chaaraoui.

Help the user state the problem before anyone picks a solution: a problem stated as a feature locks in one answer before the need behind it is understood.

1. **Understand the current framing.** Ask how they think about the problem today, and separate the outcome they want from any method they already have in mind.
2. **Find the struggling moment.** The specific situation where a user gets stuck, what they were trying to do right before it, and what they do today to work around it.
3. **Separate the problem from the solution.** A requested feature, or a technology looking for a use, is a candidate answer, not the problem.
4. **Check that the problem matters.** Who has it, how often, and whether it is a customer problem, a business problem, or both. Where it turns on how our users really behave, read their sessions first (the `read-user-sessions` skill) instead of reasoning from assumed behavior.

When the framing stays abstract, make it concrete: a specific person in a specific moment, or a throwaway prototype they can react to (the `prototype` skill).

Questions that usually move it forward:

- "What is the user doing right before they hit this? What are they trying to get done?"
- "Why hasn't this been solved already? What makes it hard?"
- "If this were solved perfectly, what would be different for the user?"
- "What do people do today to work around it?"

Flag these when you see them: starting from a feature or a technology and working back to a problem; a problem stated so broadly it points to no solution; solving an internal metric without a user need behind it.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `problem-definition`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
