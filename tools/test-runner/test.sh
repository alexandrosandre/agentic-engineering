#!/bin/bash
# Run the checks CI would run, for only what this branch changed against origin/master.
# Called by the `test` skill; exits at the first failed check.
set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# Python packages of the monorepo, one directory each at the root, each with tests/ inside.
PYTHON_PACKAGES='^(api|backend|worker|shared)$'
# Infrastructure-as-code templates the deploy pipeline lints.
INFRA_TEMPLATES=(
    "deploy/main.yaml"
    "deploy/api.yaml"
    "deploy/web.yaml"
    "deploy/worker.yaml"
)
# Placeholder: your infrastructure-as-code linter.
INFRA_LINT="iac-lint"

echo "🔍 Testing workflow started..."

echo "📡 Refreshing origin/master..."
git fetch --quiet origin master || {
    echo "❌ Failed to fetch origin/master; cannot determine branch-authored changes"
    exit 1
}

ALL_MODIFIED_FILES=$(git diff --name-only origin/master...HEAD || true)

echo "📋 Detecting modified Python packages..."
MODIFIED_FILES=$(echo "$ALL_MODIFIED_FILES" | grep "\.py$" || true)
MODIFIED_PACKAGES=$(echo "$MODIFIED_FILES" | sed 's|/.*||' | grep -E "$PYTHON_PACKAGES" | sort | uniq || true)

echo "📋 Detecting modified web app files..."
MODIFIED_WEB=$(echo "$ALL_MODIFIED_FILES" | grep -E '^web/src/.*\.(ts|tsx)$' || true)

echo "📋 Detecting modified infrastructure templates..."
MODIFIED_INFRA_FILES=()
for template in "${INFRA_TEMPLATES[@]}"; do
    if echo "$ALL_MODIFIED_FILES" | grep -q "^$template$"; then
        MODIFIED_INFRA_FILES+=("$template")
    fi
done

if [ -z "$MODIFIED_PACKAGES" ] && [ ${#MODIFIED_INFRA_FILES[@]} -eq 0 ] && [ -z "$MODIFIED_WEB" ]; then
    echo "ℹ️ No Python packages, infrastructure templates or web app files modified, skipping tests"
    exit 0
fi

[ -n "$MODIFIED_PACKAGES" ] && echo "📦 Modified packages: $MODIFIED_PACKAGES"
[ ${#MODIFIED_INFRA_FILES[@]} -gt 0 ] && echo "📄 Modified templates: ${MODIFIED_INFRA_FILES[*]}"
[ -n "$MODIFIED_WEB" ] && echo "🎨 Modified web app files detected"

# Fake cloud credentials and region, so a module that builds a cloud client at import time
# imports cleanly and a test can never reach a real account.
run_offline() {
    PYTHONPATH="$PROJECT_ROOT/shared:$PYTHONPATH" \
    CLOUD_REGION=test-region \
    CLOUD_ACCESS_KEY_ID=test \
    CLOUD_SECRET_ACCESS_KEY=test \
    "$@"
}

# Lint only the modified files (pylint on a whole package is slow), then test whole packages:
# a change in one module can break a test of another.
if [ -n "$MODIFIED_PACKAGES" ]; then
    echo "📦 Activating venv environment..."
    if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
        source "$PROJECT_ROOT/.venv/bin/activate"
    else
        echo "❌ Could not find venv at $PROJECT_ROOT/.venv (required for Python tests)"
        exit 1
    fi

    echo "🔧 Running pylint on modified files..."
    for package in $MODIFIED_PACKAGES; do
        echo "🔍 Linting $package..."
        PACKAGE_PY_FILES=$(echo "$MODIFIED_FILES" | grep -E "^${package}/.*\\.py$" | sed "s|^${package}/||" || true)
        cd "$PROJECT_ROOT/$package"
        EXISTING_PY_FILES=()
        for file_path in $PACKAGE_PY_FILES; do
            # Deleted files are in the diff but not on disk.
            if [ -f "$file_path" ]; then
                EXISTING_PY_FILES+=("$file_path")
            fi
        done
        if [ ${#EXISTING_PY_FILES[@]} -eq 0 ]; then
            echo "  No existing modified Python files for $package, skipping pylint."
            continue
        fi
        run_offline pylint --rcfile="../.pylintrc" "${EXISTING_PY_FILES[@]}" || {
            echo "❌ Pylint errors found in $package. Please fix before continuing."
            exit 1
        }
    done

    echo "🧪 Running pytest on modified packages..."
    for package in $MODIFIED_PACKAGES; do
        echo "  Testing $package..."
        cd "$PROJECT_ROOT/$package"
        run_offline pytest tests || {
            echo "❌ Tests failed in $package. Please fix before continuing."
            exit 1
        }
    done
fi

if [ ${#MODIFIED_INFRA_FILES[@]} -gt 0 ]; then
    echo "🔧 Linting modified infrastructure templates..."
    cd "$PROJECT_ROOT"
    for template in "${MODIFIED_INFRA_FILES[@]}"; do
        "$INFRA_LINT" -- "$template" || {
            echo "❌ Infrastructure linting failed for $template"
            exit 1
        }
        echo "    ✅ $template passed"
    done
fi

if [ -n "$MODIFIED_WEB" ]; then
    cd "$PROJECT_ROOT/web"
    echo "🔧 Running ESLint on web app files..."
    pnpm lint || {
        echo "❌ ESLint errors found. Please fix before continuing."
        exit 1
    }
    echo "🔍 Running TypeScript type checking..."
    pnpm typecheck || {
        echo "❌ TypeScript type errors found. Please fix before continuing."
        exit 1
    }
    echo "🧪 Running web app tests..."
    # Several agent sessions share one laptop; two workers keep a full run from starving them.
    pnpm test --run --maxWorkers=2 || {
        echo "❌ Web app tests failed. Please fix before continuing."
        exit 1
    }
    echo "✅ Web app tests passed!"
fi

echo "✅ All tests passed!"
