#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
CONTEXT_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${CONTEXT_ROOT}/.." >/dev/null 2>&1 && pwd)"
BOOTSTRAP="${REPO_ROOT}/context_compass/system/installation/linux/bootstrap.sh"

DRY_RUN="${DRY_RUN:-0}"
args=()
for arg in "$@"; do
  case "$arg" in
    --dry-run|-n)
      DRY_RUN=1
      ;;
    *)
      args+=("$arg")
      ;;
  esac
done

if [[ ! -x "${BOOTSTRAP}" ]]; then
  echo "ERROR: missing bootstrap script at ${BOOTSTRAP}" >&2
  exit 1
fi

DRY_RUN="${DRY_RUN}" bash "${BOOTSTRAP}" "${args[@]}"
