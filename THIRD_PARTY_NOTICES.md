# Third-party notices

Most of this repository is original work by Alexandros Andre Chaaraoui, licensed under [CC BY 4.0](LICENSE). Three skills started from public, permissively licensed skills and were then adapted. The portions that come from those upstreams stay under their original licenses, whose full texts are in [`licenses/`](licenses/). The adaptations are licensed under CC BY 4.0.

| Skill | Adapted from | Upstream license | Copyright |
| --- | --- | --- | --- |
| [`skills/problem-definition`](skills/problem-definition/) | the `problem-definition` skill in [RefoundAI/lenny-skills](https://github.com/RefoundAI/lenny-skills) | MIT ([text](licenses/MIT-refound-ai-lenny-skills.txt)) | Copyright (c) 2025 Refound AI |
| [`skills/design-review`](skills/design-review/) | the `document-review` skill in [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | MIT ([text](licenses/MIT-every-compound-engineering-plugin.txt)) | Copyright (c) 2025 Every |
| [`skills/find-skills`](skills/find-skills/) | the `find-skills` skill in [vercel-labs/skills](https://github.com/vercel-labs/skills) | MIT ([text](licenses/MIT-vercel-labs-skills.txt)) | Copyright (c) 2026 Vercel, Inc. |

## Acknowledgments

These shaped ideas here, though no text was copied from them:

- Simon Willison's [Agentic Engineering Patterns](https://simonwillison.net/guides/agentic-engineering-patterns/) inspired the rule that every bug found in testing or review gets a regression test that fails before the fix and passes after it (`rules/AGENTS.md`, Testing & Verification).
- `skills/simplify` and `skills/dream` are the author's own versions of two skills that coding agents ship built in: a post-change cleanup pass, and a memory-consolidation pass. `simplify` is written from this repository's own engineering rules; `dream` adds what the built-in lacked: verifying memories against reality and promoting them to rules.
- The research and design documents cite their papers inline.
