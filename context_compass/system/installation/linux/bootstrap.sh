#!/usr/bin/env bash
set -euo pipefail

# context_compass/system/installation/linux/bootstrap.sh
# Contract:
# - Safe to inspect; nothing happens unless user runs it.
# - Installs uv (if missing), then creates the active environment.
# - Installs dependencies from installation/environments/requirements.txt.
# - Seeds SQLite/Kuzu DBs via installation/build_runner.py.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
SYSTEM_ROOT="$(cd -- "${INSTALL_ROOT}/.." && pwd)"
REPO_ROOT="$(cd -- "${SYSTEM_ROOT}/../.." && pwd)"
ENV_SCRIPT="${INSTALL_ROOT}/environments/linux/install_active_env.sh"
PY_VERSION_FILE="${INSTALL_ROOT}/environments/python_version.md"
ENV_ROOT="${INSTALL_ROOT}/environments/active_environments"
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

read_py_version() {
  if [[ ! -f "${PY_VERSION_FILE}" ]]; then
    say "ERROR: Missing python_version.md at ${PY_VERSION_FILE}"
    exit 20
  fi
  local py_version
  py_version="$(tr -d '[:space:]' < "${PY_VERSION_FILE}")"
  if [[ -z "${py_version}" ]]; then
    say "ERROR: python_version.md is empty."
    exit 21
  fi
  printf '%s' "${py_version}"
}

env_path_for_version() {
  local py_version="$1"
  local env_name="context_compass_py${py_version//./_}"
  printf '%s' "${ENV_ROOT}/${env_name}"
}

main() {
  if [[ ! -x "${ENV_SCRIPT}" ]]; then
    say "ERROR: Missing env installer at ${ENV_SCRIPT}"
    exit 22
  fi

  local py_version
  py_version="$(read_py_version)"

  local env_path
  env_path="$(env_path_for_version "${py_version}")"
  local venv_py="${env_path}/bin/python"

  say "Repo root: ${REPO_ROOT}"
  say "Install root: ${INSTALL_ROOT}"
  say "Python version: ${py_version}"
  say "Environment path: ${env_path}"

  run bash "${ENV_SCRIPT}"

  if [[ ! -x "${venv_py}" ]]; then
    say "ERROR: venv python not found at ${venv_py}"
    exit 23
  fi

  run "${venv_py}" "${INSTALL_ROOT}/build_runner.py" \
    --manifest "${INSTALL_ROOT}/build_manifest.json"

  say ""
  say "OK: environment ready and databases seeded."
  say "Next steps:"
  say "  ${venv_py} context_compass/system/ai_restricted/system_management/validate.py --repo-root ."
}

main "$@"
