#!/bin/bash
# After-response hook: commit uncommitted changes and push.
# Runs after each prompt answer. Covers an agent forgetting to commit and/or push when it edited
# repo files.
#
# Only runs when CLOUD_AGENT=1 (set in the cloud agent's environment secrets), never in a local
# session, where uncommitted changes are the developer's work in progress.
# Reads JSON from stdin (the editor's hook protocol) and discards it.
set -e

# Only in cloud agent sessions
case "${CLOUD_AGENT:-}" in
    *[1YyTt]*) ;;
    *) cat >/dev/null; exit 0 ;;
esac

# Consume stdin (the editor sends JSON)
cat >/dev/null

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT"

# 1. Commit uncommitted changes to tracked files (agent forgot to commit). New files stay out:
# a stray scratch or secrets file must never reach the remote unreviewed.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "[sync] Uncommitted changes — committing..."
    git add -u
    git commit -m "chore: agent session sync"
fi

# 2. Push any unpushed commits (agent forgot to push)
NEED_PUSH=false
if git rev-parse --verify @{u} >/dev/null 2>&1; then
    # Upstream exists: only push if we have local commits not on remote (ahead)
    if [ -n "$(git rev-list @{u}..HEAD 2>/dev/null)" ]; then
        NEED_PUSH=true
    fi
else
    # No upstream: new branch, push to create it
    NEED_PUSH=true
fi

if [ "$NEED_PUSH" = true ]; then
    echo "[sync] Pushing to remote..."
    if git rev-parse --verify @{u} >/dev/null 2>&1; then
        git push || echo "[sync] Push failed (check for diverged branches)"
    else
        git push -u origin HEAD || echo "[sync] Push failed (check remote access)"
    fi
fi

exit 0
