# test-browser

**What.** Verifies web app changes in the editor's built-in browser: starts the local stack for this worktree, maps the changed files to the routes that exercise them, signs in with the test account, and for each route waits for real content, checks the page structure, the console and a screenshot, exercises changed interactions, and ends with a pass/fail table.

**Why.** Type checks and unit tests do not show a blank page, an error boundary or a console full of uncaught errors. The skill encodes the details that make browser checks reliable for an agent: start servers per worktree instead of trusting a port that may belong to another branch; lock the browser while driving it; resize before screenshots; wait incrementally because data-heavy pages are slow locally and a CSS spinner does not appear in the accessibility tree; read console messages at debug level as well as error, filtered by page; and touch only the designated test account.

**How it fits.** Local interactive sessions only. Screenshots taken along the way follow the rules' instruction to share visual evidence as you go.

**Wire up.** An editor whose browser the agent can drive, your local-stack startup script, a test account with credentials in the shell environment, and the route map table filled in for your web app.
