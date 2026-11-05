# routines/

Versioned record of recurring **agent routines**: scheduled AI agents that run a prompt on a cadence, and where each one runs. Left alone, these live only inside the external tools that run them (a cloud agent automation, a local scheduled task, a GitHub Actions cron), untraced and unreviewable. The external tool stays the live execution source of truth; this directory is the versioned mirror you can review and diff.

Each routine is a directory containing:

- `README.md`: what it does, why it exists, plus a metadata table (owner, platform, schedule, model tier, outputs, source).
- `PROMPT.md`: the raw agent instructions, verbatim (not reflowed to house style), so the mirror diffs cleanly against the platform copy.
- Any asset the routine needs that is not already in the repository. Routines that use committed files (a skill, a script) link to them instead of copying.

## Registry

| Routine | Platform | Schedule | Generates | Model tier |
| ------- | -------- | -------- | --------- | ---------- |
| [daily-eng-digest](daily-eng-digest/) | Cloud agent automation | Mon–Fri, start of the workday | Team-chat digest of what merged | A frontier model, high effort |
| [cicd-sheriff](cicd-sheriff/) | GitHub Actions (cron) | Weekdays, three times a day | Fix PR + a team-chat handoff, only after intervention | The strongest available model, highest effort |
| [clean-up-stale-feature-flags](clean-up-stale-feature-flags/) | Cloud agent automation | Weekly | Cleanup PR + team-chat note, only when something changed | A coding-tuned frontier model, high effort |
| [weekly-dev-and-support-kpis](weekly-dev-and-support-kpis/) | Cloud agent automation | Biweekly (weekly trigger, the prompt gates) | Team-chat KPI report | A fast model |
| [dream](dream/) | Local scheduled task, one per developer | Monthly (weekly trigger, the prompt gates) | Memory edits (backed up first) + a draft PR of proposed rules, only when there are proposals | The strongest available model, high effort |

The issue agent's own routines (the sweep that starts a session per assigned issue, and its weekly learn-from-outcomes run) live with the agent in [alice-issue-agent](https://github.com/alexandrosandre/alice-issue-agent), which is meant to be adopted on its own.

The model column names a tier, not a product: the routine's quality bar decides it. A routine that writes code someone will merge, or decides what becomes a rule, gets the strongest model available; a routine that counts search results and formats them gets a fast one.

## Platforms

Where routines run, and the vocabulary for what gets added next:

- **Cloud agent automation**: an always-on cloud automation of the coding-agent vendor, per owner, scheduled, able to open PRs and post to the team chat. The default home for a routine that only needs the repository and the GitHub API.
- **Scheduled cloud routine**: a coding-agent routine run in the vendor's cloud, with its own environment and credentials. Used when the routine needs a provisioned environment but no developer's machine.
- **GitHub Actions (cron)**: a scheduled workflow committed to the repository. Preferred when the schedule, the permissions and the side effects must be reviewable and testable in a PR (see [cicd-sheriff](cicd-sheriff/)), at the cost of sharing GitHub Actions' failure domain.
- **Local scheduled task**: a routine a developer runs from their own machine as a scheduled task of the coding agent's desktop app (it fires while the app is open). A routine may run locally for exactly two reasons, and its README states which one applies:
  1. It is private or experimental tooling: never exposed to the team, never run by anyone else, not even when the owner is out for a long stretch. Team-wide or role-bound automations that must be handed over on call or on vacation do not qualify.
  2. It needs the local machine for setup reasons (credentials, a local stack, data that must not leave the machine). The README then carries a TODO to move it to a hosted runner once that is unblocked, or says why no move is possible.

  Any other reason means the routine runs remotely. [dream](dream/) runs locally under reason 2: memories and session transcripts exist only on the developer's machine and stay there.

The rule behind the policy: a routine is team infrastructure the moment someone else relies on its output. If it lives on one laptop, it dies with that laptop's lid.

## Adding or updating a routine

The platform is the live source; this directory is the mirror. Keep them in sync: when you change a routine in one place, apply the same change in the other in the same sitting.

1. Open the automation in its platform.
2. Copy the agent instructions into `<routine>/PROMPT.md`, verbatim.
3. Fill `<routine>/README.md`: the metadata table and the prose sections (what it does, why, related files, how to install it).
4. Add a row to the Registry above.

Only definitions are versioned. A routine's platform-side state (the platform's memory feature, run history) is not, and a routine should not depend on it: a baseline a routine compares against is reconstructed from durable artifacts (workflow artifacts, a results table, git history) on every run.

Automations that are not engineering (team tool-usage metrics, marketing news digests, scratch automations) are deliberately left out of the registry, and the exclusion is recorded so it is traceable rather than silent.

## Patterns these routines share

- **Gate in the prompt, not the scheduler.** Platforms offer weekly triggers; biweekly and monthly cadences are a weekly trigger whose prompt checks the date first with a shell one-liner, so the model never does date arithmetic.
- **Silence is a valid outcome.** A routine that found nothing posts nothing. A feed of green confirmations trains people to mute it.
- **One output, one owner.** Every PR a routine opens names a human reviewer, and no routine merges.
- **Secrets stay out of the agent.** Where a routine posts to the team chat from CI, the agent writes a handoff file and a deterministic step posts it, so the chat token never reaches the model.
