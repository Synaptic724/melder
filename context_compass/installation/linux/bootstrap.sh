#!/usr/bin/env bash
set -euo pipefail

# context_compass/installation/linux/bootstrap.sh
# Contract:
# - Safe to inspect; nothing happens unless user runs it.
# - If Python is missing or <3.10, prints instructions and exits non-zero.
# - Creates venv at: context_compass/.venv
# - Installs: pydantic + graphiti-core[kuzu]
# - Smoke test: imports pydantic, kuzu, graphiti_core

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
VENV_DIR="${REPO_ROOT}/context_compass/.venv"
DRY_RUN="${DRY_RUN:-0}"

say() { printf '%s\n' "$*"; }

# Run a command safely (no eval). DRY_RUN prints a shell-escaped version.
run() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    printf '[dry-run] '
    printf '%q ' "$@"
    printf '\n'
    return 0
  fi
  "$@"
}

pick_python() {
  # Prefer python3, then python.
  if command -v python3 >/dev/null 2>&1; then
    printf 'python3'
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    printf 'python'
    return 0
  fi
  return 1
}

require_python_310_plus() {
  local py="$1"
  run "$py" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' \
    || return 1
}

require_venv_module() {
  local py="$1"
  run "$py" -c 'import venv' || return 1
}

main() {
  local PY
  if ! PY="$(pick_python)"; then
    say "ERROR: Python not found."
    say "Install Python 3.10+ (Graphiti requires 3.10+), then re-run:"
    say "  bash context_compass/installation/linux/bootstrap.sh"
    exit 10
  fi

  if ! require_python_310_plus "$PY"; then
    say "ERROR: Python must be 3.10+ (Graphiti requirement)."
    say "Current: $("${PY}" -V 2>&1)"
    exit 11
  fi

  # On Ubuntu/WSL, python3-venv is often missing even when python is present.
  if ! require_venv_module "$PY"; then
    say "ERROR: Python 'venv' module not available for $("${PY}" -V 2>&1)."
    say "On Ubuntu/WSL, install it with:"
    say "  sudo apt update && sudo apt install -y python3-venv"
    exit 13
  fi

  say "Repo root: ${REPO_ROOT}"
  say "Using Python: ${PY} ($("${PY}" -V 2>&1))"
  say "Venv path: ${VENV_DIR}"

  if [[ ! -d "${VENV_DIR}" ]]; then
    run "$PY" -m venv "${VENV_DIR}"
  fi

  local VENV_PY="${VENV_DIR}/bin/python"
  if [[ ! -x "${VENV_PY}" ]]; then
    say "ERROR: venv python not found/executable at ${VENV_PY}"
    exit 12
  fi

  run "${VENV_PY}" -m pip install --upgrade pip
  run "${VENV_PY}" -m pip install --upgrade pydantic "graphiti-core[kuzu]"

  # Smoke test: imports only (no config)
  run "${VENV_PY}" -c \
    "import sys; import pydantic; import kuzu; from graphiti_core import Graphiti; sys.stdout.write('deps ok\n')"

  say ""
  say "OK: deps installed."
  say "Next steps:"
  say "  1) Use this interpreter for tooling:"
  say "     ${VENV_PY} context_compass/tools/validate.py --repo-root ."
  say "  2) Then run scan once your certification gate allows it:"
  say "     ${VENV_PY} context_compass/tools/scan.py --repo-root ."
}

main "$@"
