---
name: create-pr
description: Create a draft PR following project conventions. Use when asked to create a pull request, open a PR, or prepare a branch for review.
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---
# Create PR

## When to Use
- Use when a user asks to create a pull request.
- Use when preparing a draft PR after completing work on a branch.

If there are pending changes (not committed), commit them before proceeding.

1. Fetch and merge origin/master so the branch is current and mergeable:
   ```bash
   git fetch origin master
   git merge origin/master --no-edit
   ```
   If the merge introduces conflicts, stop and tell the user.

2. Detect the GitHub issue number from the branch name or chat history if applicable.

3. Write the PR title and a brief functional-level description, then create the PR — or, if the branch already has an open PR, update it in place. Detect which:
   ```bash
   BRANCH=$(git branch --show-current)
   EXISTING_PR=$(gh pr list --head "$BRANCH" --state open --json number --jq '.[0].number // empty')
   ```
   It prints only an open PR's number, never a closed or merged one's.
   - Do not assume the reader of a PR description, PR comment, or issue comment shares the context of the chat session. Lead with what was proven or decided, keep only the details useful to a reviewer coming in cold, and strip session-internal debugging ephemera.
   - Open the description with one sentence naming the intent a reviewer should judge — `To judge: whether this is the right contract, not whether the wording is good`. Whom to notify, if anyone, is the author's decision: they add the `@handle`s themselves; never address the description to anyone or suggest whom to involve. A person reviews the intent; the review bots read the code on every PR either way, so the line asks for no particular kind of review.
   - Structure the body as `##` sections, in this order: **What**, **Why**, **Risk**, **Decisions to check**, **Out of scope**. Open **What** with one sentence naming the whole change before any file-level detail, then the other changes the fix pulled in. When the PR works an issue, **Why** states the problem as reported and what checking that report against the code and data found. **Risk** exists only when a risk review produced one (the unattended issue agent's pipeline does); copy it in unedited and write **How to revert** under it: whether reverting the squash commit undoes everything, and what stays behind otherwise (written data, a sent email, a released SDK) and how to clean it up. **Decisions to check** are the judgment calls the diff cannot show — a variable left unreverted, a scope boundary drawn, an alternative rejected. Skip a section only when it is genuinely empty. Those sections organize the brief functional-level description; they do not license a long one — each stays at the level of behavior, not a line-by-line walk through the diff.
   - The title names this PR's contribution relative to `origin/master`.
   - The PR title MUST start with project scope(s) in square brackets, followed by a space and description.
     - Format: `[api] <short description>` or `[api, web] <short description>` for multiple scopes.
     - Define one scope per top-level area of your repository (for example `api`, `web`, `backend`, `shared`, `devops`) and a regex that accepts exactly those, such as `^\[(api|web|backend|shared|devops)(, ?(api|web|backend|shared|devops))*\] .+$`.
   - Select the scope(s) based on where the changes are (use your best judgment; pick the dominant area or list multiple if significant changes span areas). Ensure the title matches the regex before creating the PR (adjust if needed).
   - Issue references (`Fixes #N` / `Part of #N` per the Pull Requests & Issues rules in `AGENTS.md`) go at the top of the description, one line per issue, right after the opening sentence. Preview URLs, recordings and a live-questions link, when the run produced them, follow on their own lines so a reviewer finds them without reading further.
   - Use only the changes made in this branch, ignoring changes from merges from master. You should talk about the PR diff.
   - **Database schema changes**: if a table or materialized view definition changed and existing tables need a manual migration, include a section in the PR body with the exact statements needed to migrate them.
   - **Infrastructure changes**: ask for a manual infra run only for a deployment that nothing else reaches, naming that deployment; the reader runs every step listed, so a step the pipeline already takes costs them a needless deploy. For a hand-deployed stack, list the exact ready-to-run command for each stack and environment the change targets, written after reading the script that owns it: some are unfit to rerun as they stand, so a script name alone is not a step.
   - **Deploy steps**: if the PR requires a specific deploy order (infra before code, migrations before deploy, two services in step), add a "Deploy steps" section to the PR body listing the ordered steps.
   - When updating an existing PR, first fetch its current body (`gh pr view "$EXISTING_PR" --json body`), then regenerate the title, the functional summary, and any diff-derived migration / infrastructure / `Deploy steps` sections from the current diff (so a changed diff never leaves stale migration or deploy text behind). Carry over only the free-form human-written prose from that fetched body that is not one of those generated sections.
   - Write the title to `<git-dir>/pr-title.txt` and the description to `<git-dir>/pr-body.md` (`git rev-parse --absolute-git-dir`) — with the file-writing tool or a quoted (`<<'EOF'`) heredoc, both keep backticks and quotes literal. Never inline generated text into a shell string: double quotes expand backticks and `$(...)`, and single quotes break on the first apostrophe. A session sandboxed to a worktree that cannot write the shared git directory writes both files to its scratchpad directory instead and sets `PR_FILE_DIR` below to that directory.
   ```bash
   PR_FILE_DIR="$(git rev-parse --absolute-git-dir)"   # pr-title.txt and pr-body.md written above
   if [ -n "$EXISTING_PR" ]; then
     git push
     gh pr edit "$EXISTING_PR" --title "$(cat "$PR_FILE_DIR/pr-title.txt")" --body-file "$PR_FILE_DIR/pr-body.md"
     PR_URL=$(gh pr view "$EXISTING_PR" --json url --jq .url)
   else
     git push -u origin "$BRANCH"
     PR_URL=$(gh pr create --draft --title "$(cat "$PR_FILE_DIR/pr-title.txt")" --body-file "$PR_FILE_DIR/pr-body.md")
   fi
   ```

4. Print the GitHub link to the new PR and open it in a browser:
   ```bash
   echo "$PR_URL"
   gh pr view "$PR_URL" --web 2>&1 || echo "PR URL: $PR_URL"
   ```
   - Skip the open step on headless environments.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `create-pr`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
