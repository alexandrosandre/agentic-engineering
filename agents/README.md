# Subagents

Subagent definitions: a name, a description the lead agent matches on, a fixed tool list, and a short system prompt. The point of a definition, rather than a general-purpose subagent with a careful brief, is the tool list: a limit that must hold belongs in the tools a subagent has, not in prose it may or may not follow (`rules/WRITING_FOR_AI_AGENTS.md`, delegation briefs).

| Subagent | What it is for |
| --- | --- |
| [`web-researcher`](web-researcher.md) | One slice of the literature sweep in [`state-of-the-art-research`](../skills/state-of-the-art-research/README.md): reads pages on the public web to their end and writes notes. |

## web-researcher

**What.** A researcher that reads many web pages anyone can publish, and therefore holds only web search, web fetch, a full-text page reader and a file-writing tool for its notes. No shell, no file read, no access to internal data.

**Why.** The research skill sends several researchers onto the open web at once. Each one reads untrusted text that may try to steer it. A general-purpose subagent would read those pages while holding a shell, file reads and whatever credentials the session has, so a single planted instruction could reach customer data or an outbound channel. With this tool list the worst a steered researcher can do is write a bad note, and the lead agent reads every note as evidence, never as instructions. The lead never fetches pages itself for the same reason: it holds the customer data.

**How it fits.** The skill's brief carries everything the researcher needs: the system as measured (aggregates only), the questions, the recency window, the notes path, and the full text of the skill's `references/researcher.md` (search method, the full-text reading rule, source judgment, notes format). The definition itself stays a few lines, so the same researcher serves the first round, the second pass and later drill-down questions.

**Wire up.** Place the file in `.claude/agents/`. Its tools are Claude Code's names (`ToolSearch`, `WebSearch`, `WebFetch`, `Write`) plus `mcp__web-reader__read_page`, the full-text page reader that [`tools/web-reader/`](../tools/web-reader/) serves once registered in `.mcp.json` under the name `web-reader`; another harness needs its own names for the same five tools. Restrict where writes may land with the harness's own permission controls. Harnesses read agent definitions and tool servers at session start, so restart the session after adding either.
