#!/usr/bin/env bash
# install.sh — project-level setup for wordcount.
#
#   bash install.sh
#
# Runs as an unprivileged user, installs nothing from the system package
# manager (no sudo/apt/dnf/brew), and EXITS — it never starts a server or any
# long-running process.  Safe to re-run: every step is idempotent.
#
# The runtime has no third-party dependencies; the only thing installed here is
# the test runner declared in requirements.txt.  System prerequisites (a Python
# 3.8+ interpreter) are listed in INSTALL.md, never installed by this script.
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "error: python3 was not found on PATH (set PYTHON=/path/to/python3)" >&2
    exit 1
fi

"$PYTHON" - <<'PY'
import sys

if sys.version_info < (3, 8):
    sys.exit("error: Python 3.8+ is required, found %d.%d" % sys.version_info[:2])
print("python: %d.%d.%d" % sys.version_info[:3])
PY

# 1. Refresh the packaging tooling, then install the declared project deps.
echo "==> installing project dependencies (requirements.txt)"
if ! "$PYTHON" -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1; then
    echo "warning: could not refresh pip/setuptools/wheel; continuing with the ones present"
fi

if ! "$PYTHON" -m pip install -r requirements.txt; then
    if "$PYTHON" -c 'import pytest' >/dev/null 2>&1; then
        echo "warning: requirements.txt could not be installed; the pytest already present satisfies it"
    else
        echo "error: could not install requirements.txt and no pytest is available" >&2
        exit 1
    fi
fi

# 2. Self-check: the module imports and the CLI counts a real file.
echo "==> self-check: import and smoke run"
"$PYTHON" -c 'import wordcount; print("import ok: wordcount", wordcount.__version__)'
"$PYTHON" wordcount.py examples/sample.txt

# 3. Self-check: the shipped test suite runs green.
echo "==> self-check: test suite"
"$PYTHON" -m unittest -q test_wordcount.py

cat <<'DONE'

Setup complete. There is no database, no migration and no seed step: this tool
is read-only and keeps no state.

Count a file:   python3 wordcount.py <file>
See it work:    bash demo.sh
Run the tests:  python3 -m unittest test_wordcount.py
Help:           python3 wordcount.py --help
DONE
