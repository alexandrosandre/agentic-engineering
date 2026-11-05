---
name: test-browser
description: Verify web app behavior in the editor's built-in browser. Use when the user asks to test UI changes in the browser or validate frontend behavior after changes. Local interactive sessions in an editor with a built-in, agent-controllable browser only.
license: CC-BY-4.0
metadata:
  author: Alexandros Andre Chaaraoui
  source: https://github.com/alexandrosandre/agentic-engineering
---
# Browser Test

## When to Use
- After frontend code changes, before creating a PR.
- When validating a PR's visual correctness.
- When the user asks to "test in the browser", "check the UI", or "verify the frontend".
- Proactively after modifying UI components, CSS, routing, or page layouts.

## Instructions

### 1. Start Local Servers

Start the API and the web app dev server for **this worktree** with the repository's local-stack startup script (backgrounded). Do not rely on `lsof` to detect running servers — they may belong to a different worktree.

The stack must run on read-only credentials, against the test account only; what it still writes, and where, is documented with the startup script.

The command runs in the background. Read its output to find the line that prints the web app's URL (a per-branch local HTTPS URL such as `https://web-<branch-slug>.localhost:<port>`). Wait until it appears before proceeding (poll the output file every few seconds), then reuse that URL for all browser navigations. The script wires the web app to this worktree's API automatically.

### 2. Determine Test Scope

Pick one based on current context:

- **PR number given:** `gh pr view <N> --json files -q '.files[].path'`
- **Current branch:** `git diff --name-only origin/master...HEAD`
- **User specifies routes:** use those directly.

Filter to files under the web app's source folder. If no web app files changed and the user explicitly asked for browser testing, test the default routes (sign-in, the account list, the test account's home). If no files changed and this is a proactive check, tell the user there are no frontend changes and stop.

### 3. Map Changed Files to Routes

Keep a table in this skill mapping the web app's source folders to the routes that exercise them. Its shape:

| File pattern | Routes to test |
|---|---|
| `pages/login/`, `auth/` | `/signin` |
| `pages/<area>/` | that area's route under the test account |
| `components/` | Check imports to find parent pages; test those |
| app entry points | sign-in, the account list, the test account's home |
| `assets/`, stylesheets | the account list and the test account's home (visual check) |
| stores, hooks, helpers | the account list and the test account's home |

When in doubt, test the account list and the test account's home at minimum.

**Always use the designated test account (`<ACCOUNT_ID>`).** Do not navigate to other customer accounts.

### 4. Run Browser Tests

Use the browser tools your agent has (list tabs, navigate, resize, snapshot, fill, click, wait for text, console messages, network requests, screenshot). Follow this sequence:

#### 4a. Setup

1. **List tabs** to inspect existing browser tabs.
2. **Open or reuse a tab:**
   - If no browser tab exists, navigate to the web app URL from the logs.
   - If a browser tab already exists, reuse that tab.
3. **Keep the tab to yourself:** tell the user you are driving the tab and ask them not to use it until you hand it back; if your browser tools can block user input on a tab, use that.
4. **Resize** to width 1920, height 1080. Always maximize before taking screenshots.

#### 4b. Authenticate

After navigating, wait 3 seconds, then snapshot and check the page URL and content:

**Case A — Already authenticated:** the URL is the account list and the snapshot contains account names (not an error boundary). Proceed to step 4c.

**Case B — Redirected to sign-in:** when the startup script enabled a dev auto-login from test credentials in the shell (it prints so), sign-in completes by itself: wait a few more seconds and re-check for Case A before doing anything. Otherwise log in:

1. Read the test username and password from their shell environment variables. If not set, source the shell profile and check again. If still not set, hand the tab back and ask the user to log in manually in the editor's browser pane, then resume after they confirm.
2. Snapshot to get the form element refs (the email and password text boxes).
3. Fill the email field with the username.
4. Fill the password field with the password.
5. Click the submit button.
6. Wait for text that only the signed-in account list shows (timeout 15000 ms) to confirm login succeeded.
7. Snapshot to verify you're on the account list.

**Case C — Error boundary while authenticated:** the URL is the account list but the snapshot shows the error boundary's text or a network error. This usually means the API server is down. Check the terminal output for API errors. If the API crashed, unlock the browser, report it to the user, and stop — browser tests need a working API for authenticated pages.

**Case D — Need to re-login:** if the user explicitly asks to log in with test credentials but the browser already has a session, first navigate to the logout route, wait 2 seconds, then navigate to sign-in and follow Case B. To sign in as a different user while auto-login is enabled, use the sign-in route's manual mode.

If login fails (MFA prompt, error message), hand the tab back and ask the user to log in manually, then resume.

#### 4c. Test Each Route

For each route from step 3:

1. **Navigate** to the web app URL plus the route.
2. **Wait for content:** a local API can be slow; data-heavy pages can take 30+ seconds to load. Use this strategy:
   - Wait 3 seconds, then snapshot.
   - If the snapshot has very few refs (only the always-present widgets) and/or a screenshot shows a spinner, the page is still loading. A spinner drawn by a CSS animation does **not** appear in the accessibility snapshot — take a screenshot to check visually if needed.
   - Wait 10 more seconds, snapshot again. Repeat up to 3 times (total ~33s max).
   - For lighter pages (sign-in, the account list), the first 3-second wait is usually sufficient.
3. **Snapshot** — verify the page structure looks correct:
   - Page title is not blank.
   - Key content elements are present (headings, tables, navigation).
   - No error boundary text ("Something went wrong", "Error", "Network Error").
4. **Console** — check for JavaScript errors:
   - Messages accumulate across all navigations. Filter by the current page URL.
   - Real errors may arrive at `debug` level (error boundaries, uncaught exceptions) as well as `error`. Check both.
   - Ignore known noise (the browser tool's own messages, dev-server connect messages, devtools download hints, the app's version banner).
   - Flag: API client errors, `Uncaught`, `SyntaxError`, `TypeError`, `ReferenceError`, error boundary stack traces.
5. **Screenshot** for evidence.
6. **Interactions** (if the changed code involves interactive elements):
   - Snapshot the interactive elements to list clickable ones.
   - Click key interactive elements (buttons, tabs, dropdowns) and verify the resulting state with another snapshot.
   - For form changes: fill test values and verify validation.

#### 4d. Cleanup

1. Hand the tab back to the user when all tests are complete.

### 5. Handle Failures

When a test fails:

1. Take a screenshot of the error state.
2. Collect console messages.
3. Optionally check network requests for failed API calls.
4. Report the failure to the user with:
   - Route that failed.
   - What went wrong (error boundary, console error, missing content).
   - Screenshot evidence.
5. Ask how to proceed: **fix now**, **skip**, or **stop testing**.

### 6. Test Summary

After all routes are tested, present a summary:

```
## Browser Test Results

**Branch:** <branch_name>
**Server:** <web app URL>

| Route | Status | Notes |
|-------|--------|-------|
| /accounts | Pass | |
| /accounts/<ACCOUNT_ID> | Pass | |
| /signin | Fail | Console error: ... |

### Console Errors: <count>
- <list non-trivial errors>

### Result: PASS / FAIL / PARTIAL
```

## Important Notes
- **Always maximize** the browser (1920x1080) before taking screenshots.
- **Keep the tab to yourself** while testing, and hand it back when done.
- **Test account only.** Do not modify or navigate to other customer accounts.
- Inspect existing tabs first and reuse one that already exists.
- The snapshot returns an accessibility tree with element refs. Always snapshot before clicking to get current refs.
- Use incremental waits with snapshot checks, not one long wait. Light pages need ~3s; data-heavy pages need up to 33s.
- A snapshot with only the always-present widgets means the page hasn't rendered yet. Wait longer.

## Closing

- End your response with a blockquote line: **Skills used:** then each skill name in backticks (this skill: `test-browser`; include other skills if used).
- If this skill's instructions failed or needed a workaround, update this file.
