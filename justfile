# Project task runner — https://just.systems (brew install just)
# Run `just` with no arguments to list available recipes.

frontend := "lightweight_charts_v5/frontend"

default:
    @just --list

# Install the package editable with dev extras, plus frontend deps
install:
    pip install -e .[devel]
    cd {{frontend}} && npm install

# Build the frontend bundle into frontend/build
build:
    cd {{frontend}} && npm run build

# Start the Vite dev server on port 3001 (pair with LWC_V5_DEV_SERVER=1)
dev:
    cd {{frontend}} && npm start

# Lint Python (ruff) and frontend (eslint)
lint:
    ruff check lightweight_charts_v5 demo e2e
    cd {{frontend}} && npm run lint

# Auto-fix Python lint findings
fix:
    ruff check --fix lightweight_charts_v5 demo e2e

# Typecheck the frontend
typecheck:
    cd {{frontend}} && npm run typecheck

# Run the e2e smoke test (needs a built frontend)
test:
    pytest e2e/ -v

# Audit frontend dependencies for high/critical vulnerabilities
audit:
    cd {{frontend}} && npm audit --audit-level=high

# Run the minimal demo app
demo:
    streamlit run demo/minimal_demo.py

# Build sdist + wheel (frontend is built first)
package: build
    rm -rf dist/
    python -m build

# Everything CI checks, locally
check: lint typecheck build test
