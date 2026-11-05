# cloud-agent-boot

`boot.sh`: the install command of a cloud coding agent's environment, written so that a boot costs under a second when nothing changed.

## The problem

Cloud agent environments boot from a snapshot taken after a full install. The naive install command (`uv sync && pnpm install`) re-resolves everything on every boot: tens of seconds to minutes before the agent can do anything, multiplied by every session and every follow-up. The other naive choice, no install command at all, leaves the agent working against a snapshot whose dependencies drifted from the branch's lockfiles, and failing in ways that look like code bugs.

## How it works

It fingerprints the dependency files (the interpreter version, the root and per-package `pyproject.toml` files, `uv.lock`, the web app's `pnpm-lock.yaml`) and compares them with the fingerprints saved at the last boot:

- **First boot after a snapshot**: trust the snapshot, save the fingerprints, exit.
- **Nothing changed**: exit immediately.
- **Something changed**: reinstall only that ecosystem (Python with `uv sync --frozen`, the web app with `pnpm install --frozen-lockfile`), both in parallel when both changed, then save the new fingerprints.
- **`--force`**: reinstall everything.

The interpreter version is read from `.python-version`, the repository's single source of truth for it, never hard-coded here.

## Wiring it up

Set it as the install command in your cloud agent's environment configuration. Adjust `PYTHON_DEP_FILES` and `WEB_LOCK` to your layout, and replace the `ensure_uv` stub with your repository's pinned uv installer. Add `.deps-checksum` to `.gitignore`.

Pairs with [`editor-hooks`](../editor-hooks/), the other half of making cloud sessions behave: this one gets the session started fast, that one makes sure its work is pushed when it ends.
