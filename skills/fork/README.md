# fork

**What.** Creates a new worktree from the user's intent — keywords turned into a branch name, dependencies and env files set up — and opens it where the user starts agent sessions, so the work continues in a fresh chat there.

**Why.** Parallel agent sessions need isolated worktrees, and an editor's built-in worktree button creates a bare checkout without the virtualenv, `node_modules` and env files, so the agent there cannot run tests. Running the repository's own setup script instead keeps every worktree ready to verify its own changes. The skill also refuses to continue the work in the current window: the new worktree is where it belongs.

**How it fits.** Like `/checkout`, but in a new worktree; the branch name follows the same convention.

**Wire up.** A worktree setup script that creates the worktree, installs dependencies, and opens it in your editor or agent app; put its path in the skill.
