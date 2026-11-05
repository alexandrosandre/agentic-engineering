# find-skills

**What.** Finds and installs agent skills from public catalogs: it searches skills.sh with the Skills CLI (`npx skills find`), consults the aihero.dev curated catalogue for engineering-process skills, and queries the airskills.ai catalog API for discovery. Before anything is installed it looks the skill up on a public security registry (verified-skill.com) and reports what it found, then installs into the repository's own skills folder, either with `npx skills add` or by copying the files from a public GitHub source.

**Why.** Someone has usually already written a good skill for a common domain, and an agent that only searches when asked misses most of them. So this version is meant to fire proactively, while the agent plans a task. The opinion behind its install path is that a skill is code the agent will obey: it is installed into the repository, where it is reviewed and versioned like the rest of the instructions, only from sources that can be read first, and with its verification state on the record. The registry check informs the user and never blocks: the user decides.

**How it fits.** A utility skill that sits beside the rest of the collection. A skill it installs is a starting point: before relying on it, adapt it to your agent (Step 5 of the skill) and to the repository's rules, the same way the skills here were adapted.

**Wire up.** Node.js for `npx skills`, `curl`, and the GitHub CLI (`gh`) for the public-GitHub copy path. Replace the example folder `.agents/skills/` with the folder your agent reads; if several agents share the repository, symlink their skills folders to one copy.

**Origin.** Adapted from the `find-skills` skill in [vercel-labs/skills](https://github.com/vercel-labs/skills), licensed MIT (Copyright (c) 2026 Vercel, Inc.). This version forked from an early-2026 revision of that skill and changed it as follows:

- Rewrote the description and the "when to use" list so the agent also searches proactively while planning a task, not only when the user asks.
- Added two discovery sources next to skills.sh: the aihero.dev curated catalogue (installed through the same npx path, with its one-time setup skill), and the airskills.ai public catalog API, used for discovery only and installed only from a public GitHub source by copying the files.
- Added a verification step before any install: a lookup on the verified-skill.com security registry with a trusted-publisher fast path for vendor orgs, a table mapping each registry state to what to report, standing caveats about what "verified" does and does not mean, and a manual-review checklist for skills the registry does not know. It is informational and never blocks the install.
- Install repo-local by default, into the repository's skills folder, instead of the upstream's global (`-g`) install; added the public-GitHub copy path with `gh api`.
- Added a step for adapting skills written for one specific coding agent (paths, tool names, permission blocks, slash commands).
- Added a reference list of the largest public skill repositories, grouped by how they install.
- Dropped the upstream's "understand what they need" step, its search-category table and search tips, and its suggestion to create a skill with `npx skills init` when nothing is found; the fallback is now "say which sources you searched, then do the task directly".
- Added the repository's closing convention: name the skills used, and update the skill when it needed a workaround.

The upstream skill has since added a skills.sh leaderboard check and quality heuristics (install counts, stars, source reputation) before recommending a skill, and an `--owner` search filter; this version does not carry them and relies on its registry verification step instead.
