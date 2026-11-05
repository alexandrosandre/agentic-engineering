#!/bin/bash
# boot.sh — cloud agent install/boot script
#
# Designed to be the "install" command of a cloud coding agent's environment. The environment
# boots from a snapshot taken after a full install; on each boot, this script checks whether
# any dependency file changed since the snapshot was taken. If nothing changed, it exits
# immediately (< 1s). If requirements drifted, it re-installs only what is needed.
#
# Usage:  ./tools/cloud-agent-boot/boot.sh          (normal boot — diff-based upgrade)
#         ./tools/cloud-agent-boot/boot.sh --force  (force full reinstall)
set -e

WORKSPACE_ROOT="$(git rev-parse --show-toplevel)"
cd "$WORKSPACE_ROOT"

# Single source of truth for the interpreter version.
PYTHON_VERSION="$(tr -d '[:space:]' < "$WORKSPACE_ROOT/.python-version")"

# ── Paths ──────────────────────────────────────────────────────────────
VENV_DIR="$WORKSPACE_ROOT/.venv"
CHECKSUM_FILE="$WORKSPACE_ROOT/.deps-checksum"
export PATH="$HOME/.local/bin:$PATH"

# ── Dependency files to track ─────────────────────────────────────────
PYTHON_DEP_FILES=(
    ".python-version"
    "pyproject.toml"
    "uv.lock"
    "shared/pyproject.toml"
    "api/pyproject.toml"
    "backend/pyproject.toml"
    "worker/pyproject.toml"
)
WEB_LOCK="web/pnpm-lock.yaml"

# ── Helpers ────────────────────────────────────────────────────────────
compute_python_checksum() {
    local combined=""
    for dep in "${PYTHON_DEP_FILES[@]}"; do
        if [ -f "$dep" ]; then
            combined+="$(sha256sum "$dep")"
        fi
    done
    echo -n "$combined" | sha256sum | cut -d' ' -f1
}

compute_web_checksum() {
    if [ -f "$WEB_LOCK" ]; then
        sha256sum "$WEB_LOCK" | cut -d' ' -f1
    else
        echo "none"
    fi
}

load_saved_checksums() {
    SAVED_PY_CHECKSUM=""
    SAVED_WEB_CHECKSUM=""
    if [ -f "$CHECKSUM_FILE" ]; then
        SAVED_PY_CHECKSUM=$(grep "^python=" "$CHECKSUM_FILE" 2>/dev/null | cut -d= -f2 || true)
        SAVED_WEB_CHECKSUM=$(grep "^web=" "$CHECKSUM_FILE" 2>/dev/null | cut -d= -f2 || true)
    fi
}

save_checksums() {
    local py_cs="$1"
    local web_cs="$2"
    cat > "$CHECKSUM_FILE" <<EOF
python=$py_cs
web=$web_cs
EOF
}

# ── Ensure tools are available ─────────────────────────────────────────
# TODO: wire to your repository's pinned uv installer; a cloud image may lack uv entirely.
ensure_uv() {
    command -v uv >/dev/null 2>&1 || {
        echo "[boot] uv not found; install the version your repository pins."
        exit 1
    }
}

ensure_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "[boot] Creating .venv with Python $PYTHON_VERSION..."
        uv python install "$PYTHON_VERSION"
        uv venv "$VENV_DIR" --python "$PYTHON_VERSION"
    fi
}

# ── Install functions ──────────────────────────────────────────────────
install_python_deps() {
    echo "[boot] Installing Python dependencies..."
    UV_PROJECT_ENVIRONMENT="$VENV_DIR" uv sync --frozen --python "$PYTHON_VERSION" --quiet
    echo "[boot] Python dependencies up to date."
}

install_web_deps() {
    echo "[boot] Installing web app dependencies..."
    corepack enable 2>/dev/null || true
    cd "$WORKSPACE_ROOT/web"
    pnpm install --frozen-lockfile --silent 2>/dev/null
    cd "$WORKSPACE_ROOT"
    echo "[boot] Web app dependencies up to date."
}

# ── Main ───────────────────────────────────────────────────────────────
FORCE=false
if [ "${1:-}" = "--force" ]; then
    FORCE=true
fi

echo "[boot] Cloud agent boot — checking dependencies..."

ensure_uv
ensure_venv

CURRENT_PY_CHECKSUM=$(compute_python_checksum)
CURRENT_WEB_CHECKSUM=$(compute_web_checksum)

# Saved checksums come from the snapshot or the last boot.
load_saved_checksums

NEED_PY=false
NEED_WEB=false

if [ "$FORCE" = true ]; then
    NEED_PY=true
    NEED_WEB=true
    echo "[boot] --force flag: reinstalling everything."
elif [ ! -f "$CHECKSUM_FILE" ]; then
    # First boot after the snapshot: the snapshot has everything installed, so only record
    # what it was installed from.
    echo "[boot] First boot — dependencies already in snapshot. Saving checksums."
    save_checksums "$CURRENT_PY_CHECKSUM" "$CURRENT_WEB_CHECKSUM"
    echo "[boot] Done (no install needed)."
    exit 0
else
    if [ "$CURRENT_PY_CHECKSUM" != "$SAVED_PY_CHECKSUM" ]; then
        NEED_PY=true
        echo "[boot] Python dependencies changed — will re-install."
    fi
    if [ "$CURRENT_WEB_CHECKSUM" != "$SAVED_WEB_CHECKSUM" ]; then
        NEED_WEB=true
        echo "[boot] Web app lock file changed — will re-install."
    fi
fi

if [ "$NEED_PY" = false ] && [ "$NEED_WEB" = false ]; then
    echo "[boot] All dependencies up to date. Nothing to do."
    exit 0
fi

# Run installs, in parallel when both are needed.
if [ "$NEED_PY" = true ] && [ "$NEED_WEB" = true ]; then
    install_python_deps &
    PY_PID=$!
    install_web_deps &
    WEB_PID=$!
    set +e
    wait $PY_PID; PY_EXIT=$?
    wait $WEB_PID; WEB_EXIT=$?
    set -e
    [ $PY_EXIT -ne 0 ] && echo "[boot] ERROR: Python install failed" && exit 1
    [ $WEB_EXIT -ne 0 ] && echo "[boot] ERROR: Web app install failed" && exit 1
elif [ "$NEED_PY" = true ]; then
    install_python_deps
elif [ "$NEED_WEB" = true ]; then
    install_web_deps
fi

save_checksums "$CURRENT_PY_CHECKSUM" "$CURRENT_WEB_CHECKSUM"

echo "[boot] Done — all dependencies installed."
