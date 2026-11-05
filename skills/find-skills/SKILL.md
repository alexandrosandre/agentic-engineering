---
name: find-skills
description: Discover skills via npx skills (skills.sh), the aihero.dev catalogue, and airskills.ai; install via npx or public GitHub copy. Use proactively when a task could benefit from specialized guidance, or when asked to find or install a skill.
license: CC-BY-4.0 AND MIT
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
  adapted_from: https://github.com/vercel-labs/skills
  upstream_license: MIT
---

# Find Skills

Adapted from the find-skills skill in vercel-labs/skills (MIT); changes by Alexandros Andre Chaaraoui.

This skill helps you discover and install skills from the open agent skills ecosystem into your agent's skills folder (this skill uses `.agents/skills/` as the example; substitute the folder your agent reads). Every skill lands in that one folder regardless of the agent it was originally written for. Airskills is used only for catalog discovery; install airskills results by copying from public GitHub sources into the skills folder.

> **Several agents, one folder:** when more than one coding agent works in the repository and they read different skills folders, symlink the others to the one you install into, so a skill installed once is available to all of them.

## When to Use This Skill

Use this skill when:

- **The user asks directly**: "how do I do X", "find a skill for X", "is there a skill that can...", or expresses interest in extending capabilities
- **You're planning the task**: While thinking about how to approach a request, ask yourself "could an existing skill help here?"—if the task involves a common domain (React, testing, design, deployment, etc.), search proactively without waiting for the user to suggest skills
- **The task could benefit from specialized guidance**: Writing tests, reviewing PRs, optimizing performance, creating docs, or any domain where a curated skill might exist

## Skill sources

Use `npx skills` for skills.sh, browse the aihero.dev catalogue for engineering-process skills, and use the airskills.ai public catalog only for discovery. Repo-local installs come from `npx skills` or public GitHub sources copied into the skills folder.

### npx skills (marketplace discovery)

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem indexed on [skills.sh](https://skills.sh/). Best for **finding and installing public catalog skills**.

**Key commands:**

- `npx skills find [query]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills check` - Check for skill updates
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

### aihero.dev (curated catalogue, npx install)

[aihero.dev/skills](https://www.aihero.dev/skills) is Matt Pocock's curated skill set: an idea→ship engineering spine (`grill-me`, `domain-modeling`, `to-spec`, `to-tickets`, `tdd`, `code-review`, `triage`, …) plus productivity and reference skills, with editorial guides and a changelog. The source repo is [mattpocock/skills](https://github.com/mattpocock/skills), indexed on skills.sh, so it installs through the npx path and passes Step 3 like any other skills.sh result.

Browse it as markdown: https://www.aihero.dev/skills.md (each skill group links its own `.md` twin). Consult it when the task is about engineering process — planning, specs, tickets, TDD, review, triage — or the user names AI Hero or Matt Pocock; keyword search still goes through `npx skills find`.

Install: `npx skills add mattpocock/skills@<skill> -y`. The engineering skills read per-repo configuration (issue tracker, triage labels, domain-doc layout) that `setup-matt-pocock-skills` writes on its one-time run, so install that one alongside them.

### airskills.ai (catalog discovery, public GitHub install only)

[airskills.ai](https://airskills.ai) hosts public skills from **any publisher** as `<user>/<skill>`. Use the public catalog API for discovery, but do **not** install through airskills tooling. Install only when the skill resolves to a public GitHub source that can be inspected and copied into the skills folder. `chrismdp/*` skills are examples only — search the whole catalog, not just that user.

**Search the platform catalog** (any publisher; returns install-ready `slug` values):

```bash
curl -sf -H "X-Airskills-CLI-Version: 0.6.10" \
  "https://airskills.ai/api/v1/public/skills?q=<query>&limit=50"
```

**Install policy:** public GitHub only. If an airskills result has no public GitHub source, report that it is not installable by this skill.

**Docs:** https://airskills.ai/llms.txt · **OpenAPI:** https://airskills.ai/openapi.json

**When to search airskills:** npx find returned nothing, or the user named an airskills-style `owner/skill-name`. Use airskills as discovery, then install only from a public GitHub source.

**Example GitHub-hosted skill** (not on the platform catalog): `chrismdp/airskill-examples` — `code-review`, `conventional-commits`, `go-errors`, `testing-strategy`.

```bash
mkdir -p .agents/skills/code-review
gh api repos/chrismdp/airskill-examples/contents/code-review/SKILL.md --jq .content \
  | base64 -d > .agents/skills/code-review/SKILL.md
```

## How to Help Users Find Skills

### Step 1: Search for Skills

**Search skills.sh:**

```bash
npx skills find [query]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills find react performance`
- User asks "can you help me with PR reviews?" → `npx skills find pr review`
- User asks "I need to create a changelog" → `npx skills find changelog`
- User asks about database schema or query design → `npx skills find <database name>`

The command will return results like:

```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

**Also search the airskills.ai platform catalog** (all publishers — not just `chrismdp`):

```bash
curl -sf -H "X-Airskills-CLI-Version: 0.6.10" \
  "https://airskills.ai/api/v1/public/skills?q=<query>&limit=50"
```

Parse `skills[].slug` (`<user>/<skill>`) and `description`. Before presenting an install option, resolve the result to a public GitHub source. If no public GitHub source exists, present it as "catalog-only / not installable by this skill." Link: https://airskills.ai (platform; no per-skill skills.sh page).

**If both return nothing**, or the user named an airskills-style path (`owner/skill-name`):

1. Check known GitHub skill repos in the reference section below (e.g. `chrismdp/airskill-examples` — example repo only)
2. Browse the public GitHub source, read `SKILL.md`, and copy it into the skills folder
3. Browse airskills docs only for source metadata: https://airskills.ai/docs.md

### Step 2: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install command (npx) or public GitHub copy command
3. A **clickable markdown link**:
   - **npx / skills.sh:** `https://skills.sh/<owner>/<repo>/<skill>` (mandatory for marketplace results)
   - **airskills platform:** https://airskills.ai (discovery only; no skills.sh page exists)
   - **public GitHub source:** source repo URL

Example response (npx):

```
**vercel-labs/agent-skills@vercel-react-best-practices** — React and Next.js
performance optimization guidelines from Vercel Engineering.

Install: `npx skills add vercel-labs/agent-skills@vercel-react-best-practices -y`

Learn more: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

Example response (airskills platform, GitHub source unknown):

```
**chrismdp/retro** — End-of-session retrospective. Reviews the conversation for corrections,
friction, and wasted effort, then proposes durable improvements to skills and rules.

Install: not offered by this skill unless a public GitHub source is available.

Platform: https://airskills.ai
```

Example response (airskills GitHub path):

```
**chrismdp/code-review** — PR review checklist (correctness, security, performance, tests).

Install:
mkdir -p .agents/skills/code-review
gh api repos/chrismdp/airskill-examples/contents/code-review/SKILL.md --jq .content \
  | base64 -d > .agents/skills/code-review/SKILL.md

Source: https://github.com/chrismdp/airskill-examples
```

### Step 3: Verify Before Installing

Run this step for **every** installable skill selected from **either source** — `npx skills` (skills.sh) or a public GitHub source discovered through airskills — before Step 4 installs anything.

Cross-check the selected skill against [verified-skill.com](https://verified-skill.com) — a **verification filter, not a source**. Never install from verified-skill.com directly through this skill.

**Trusted-publisher fast path.** If the GitHub owner slug is an **exact, case-insensitive match** (do **not** fuzzy-match) of one of these vendor orgs, skip the registry check and proceed:
```
anthropics, openai, google, google-gemini, microsoft, vercel, cloudflare, github
```

**Otherwise, look up the skill:**

```bash
curl -sf "https://verified-skill.com/api/v1/skills/<owner>/<repo>/<skill>/security"
npx vskill info <owner>/<repo>/<skill>
```

The `<owner>/<repo>/<skill>` path matches the source GitHub repo — e.g. `mattpocock/skills/tdd`.

**Airskills shortname mapping.** Airskills uses two-segment names (`user/skill`) that don't map directly to the registry's three-segment path. Before looking up:
1. Resolve the underlying public GitHub source from the airskills page, catalog metadata, or an explicit `github:<owner>/<repo>/<path>` reference.
2. Use that GitHub `<owner>/<repo>/<skill>` for the registry lookup.
3. If the source can't be determined or is not public GitHub, do not install it through this skill. Report it as catalog-only and print the manual-review notice below.

**This step is informational — installation is never blocked.** For npx and public GitHub installs alike, always report the verification state and a recommendation; the user decides whether to proceed.

**Map the registry state to what you tell the user:**

| Registry state | What to report |
| -------------- | -------------- |
| **Blocklisted** | Blocklist entry + evidence URLs. Recommend skipping unless the user can… |
| **Tier 1 FAIL** / platform critical findings | Score, findings, security report URL. Recommend… |
| **Tier 1 CONCERNS** (50–79) | Findings + report URL. Recommend skimming findings before relying… |
| **CERTIFIED** (registry-trusted publisher) | Scanning bypassed for trusted publisher. Trust the… |
| **VERIFIED + Tier 1 PASS + Tier 2 PASS** | Scores + last-scanned date. "Scanned cleanly at that… |
| **VERIFIED + Tier 2 PENDING** | Scan incomplete; recommend a quick manual skim. |
| **404 / not on registry** | Print the manual-review notice (below). |

**Always surface these caveats when reporting verification:**

- **VERIFIED ≠ currently secure.** Indexed and scanned at some point; the current security report may show failures.
- **CERTIFIED = trusted publisher.** Scanning is *bypassed* for vendor orgs. Trust the publisher, not the scan.
- **Quality eval is separate from security.** A skill can be VERIFIED but `Degrading` on evals.
- **Registry crawls big repos in bulk.** Inclusion is not hand review.

**Manual-review notice (when 404):**

> Not found on verified-skill.com — this skill has not been independently verified.
>
> Recommended before relying on it:
> 1. Read `SKILL.md` and any referenced scripts/hooks
> 2. Look for: `exec`/`spawn` calls, network requests, filesystem writes outside the skill dir, credential reads, prompt-injection patterns

### Step 4: Offer to Install

Install the skill **into the repository's skills folder**. The Step 3 report is informational for both npx and public GitHub installs — proceed unless the user asks to abort.

**From skills.sh (npx):**

```bash
npx skills add <owner/repo@skill> -y
```

The `-y` flag skips confirmation prompts. Check where the CLI wrote the skill: if it is not the folder your agent reads, move or copy it there.

Use `-g` only if the user explicitly wants a user-level (global) install instead of a repo-local one.

**From public GitHub (including airskills-discovered GitHub sources):**

```bash
mkdir -p .agents/skills/<skill>
gh api repos/<owner>/<repo>/contents/<skill-dir>/SKILL.md --jq .content \
  | base64 -d > .agents/skills/<skill>/SKILL.md
```

For multi-file skills, inspect the public GitHub tree first, then copy the needed files under `.agents/skills/<skill>/`. Do not use airskills tooling for repo-local installs.

### Step 5: Adapt Agent-specific Skills

When a skill was written for one particular coding agent (its catalog, its instructions or its folder layout name that agent), adapt it to the agent you run in after installation:

1. **File paths**: Replace the original agent's config paths (its skills folder, its settings file) with your agent's equivalents
2. **Tool names**: Replace agent-specific tool names (shell, read, write, edit tools) with your agent's equivalents or generic instructions
3. **Config format**: Convert agent-specific instruction files into a `SKILL.md`. Persistent project conventions belong in the appropriate `AGENTS.md` (hierarchically per folder).
4. **Permission model**: Remove permission blocks (allowed-tool lists, permission settings) your agent does not honor
5. **Slash commands**: Replace built-in slash commands of the original agent with your agent's equivalent actions, or remove them

## Largest Skill Repositories by Marketplace (Reference)

For quick reference, these are among the largest skill sources. **The skill is not limited to these**—search with `npx skills find` first, then airskills.ai and public GitHub if needed.

Skills installed via `npx skills` land in the skills folder. Airskills results are installed only when they resolve to public GitHub sources that can be inspected and copied into the skills folder. Skills written for one specific agent require adaptation per Step 5 above.

Repos fall into install categories:

- **npx / skills.sh** — `npx skills add <owner/repo>@<skill-name>` (or `npx skills add <owner/repo>` for all skills). Indexed on skills.sh.
- **airskills.ai catalog** — search public platform metadata, then install only from public GitHub sources by copying into the skills folder. Not on skills.sh.
- **Manual-inspection** — not compatible with either CLI. Browse on GitHub, adapt (Step 5), copy into `.agents/skills/<name>/SKILL.md` or your agent's rules folder.

### npx / skills.sh repos (`npx skills add`)

#### Multi-platform

- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) — Vercel official (~22k ★): React, Next.js, web design, deployment, Playwright, AI SDK
- [vercel-labs/skills](https://github.com/vercel-labs/skills) — Skills CLI repo (~7.5k ★); includes find-skills and utilities
- [mattpocock/skills](https://github.com/mattpocock/skills) — Matt Pocock's "Skills for Real Engineers" (~262k ★): idea→ship workflow, productivity, and reference skills; catalogue, guides, and changelog at [aihero.dev/skills](https://www.aihero.dev/skills)
- [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — Compound Engineering Plugin (~10k ★): plan/work/review/compound workflows, multi-agent review, worktrees; supports several coding agents
- [cursor/plugins](https://github.com/cursor/plugins) — Official Cursor plugin marketplace
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) — Multi-platform curated skills (~9k ★): Anthropic, Google, Vercel, Stripe, etc.

#### Agent-specific (adapt per Step 5)

- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic official catalog (~80k ★): document skills, example skills, spec. **May require adaptation**
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — Agent harness (~56k ★): framework, DB, workflow skills. **Requires adaptation**
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — Curated skills (~39k ★): docs, dev, Composio app automation. **Requires adaptation**
- [openai/skills](https://github.com/openai/skills) — OpenAI official Codex skills catalog (~10k ★): .system, .curated, .experimental. **May require adaptation**

#### Other CLI-installable

- [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) — Google Labs: Stitch UI generation, react:components, enhance-prompt
- [google-labs-code/jules-skills](https://github.com/google-labs-code/jules-skills) — Jules SDK skills; GitHub issue triage, etc.

Many vendors of databases, frameworks and cloud platforms publish an official `agent-skills` repository of their own; when the task centers on one product, search for its vendor's repo (`npx skills find <product>`).

### airskills.ai and public GitHub copy

- [chrismdp/airskills](https://github.com/chrismdp/airskills) — airskills CLI source and API docs; use as reference only, not as the install path for this skill
- Platform catalog — search all public skills: `GET /api/v1/public/skills?q=<query>` (see airskills section above); install only if a public GitHub source is available
- [chrismdp/airskill-examples](https://github.com/chrismdp/airskill-examples) — Example GitHub-only skills: code-review, conventional-commits, go-errors, testing-strategy

Copy example:

```bash
mkdir -p .agents/skills/code-review
gh api repos/chrismdp/airskill-examples/contents/code-review/SKILL.md --jq .content \
  | base64 -d > .agents/skills/code-review/SKILL.md
```

Docs: https://airskills.ai/llms.txt

### Manual-inspection repos (browse, read, copy)

These repos contain valuable prompts, rules, or reference material but do **not** follow the `npx skills` package format. To use them:

1. Browse the repo (`gh repo view <owner/repo> --web` or `gh api repos/<owner/repo>/contents/<path>`)
2. Find the relevant prompt/rule/skill file
3. Adapt the content for your agent (per Step 5)
4. Copy it into `.agents/skills/<name>/SKILL.md` or your agent's rules folder

- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) — A coding agent's system prompts (~5.8k ★): agent prompts, tool descriptions, sub-agent prompts, built-in skills, system reminders; updated per release. Useful as reference for prompt engineering, understanding agent architecture, or extracting specific prompt patterns. **Requires adaptation**

## When No Skills Are Found

Say which sources you searched, then do the task directly.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `find-skills`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
