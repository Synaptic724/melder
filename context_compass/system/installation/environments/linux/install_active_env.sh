#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ENV_ROOT="${SCRIPT_DIR}/../active_environments/linux"
PY_VERSION_FILE="${SCRIPT_DIR}/../python_version.md"
REQS_FILE="${SCRIPT_DIR}/../requirements.txt"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../../../.." >/dev/null 2>&1 && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Installing uv..."
  if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://astral.sh/uv/install.sh | sh
  else
    echo "uv install failed: curl or wget is required."
    exit 1
  fi
  export PATH="$HOME/.cargo/bin:$PATH"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is still unavailable after install. Restart your shell and retry."
  exit 1
fi

if [[ ! -f "${PY_VERSION_FILE}" ]]; then
  echo "Missing python_version.md at ${PY_VERSION_FILE}"
  exit 1
fi

PY_VERSION="$(tr -d '[:space:]' < "${PY_VERSION_FILE}")"
if [[ -z "${PY_VERSION}" ]]; then
  echo "python_version.md is empty."
  exit 1
fi

if [[ ! -f "${REQS_FILE}" ]]; then
  echo "Missing requirements.txt at ${REQS_FILE}"
  exit 1
fi

mkdir -p "${ENV_ROOT}"
ENV_NAME="context_compass_py${PY_VERSION//./_}"
ENV_PATH="${ENV_ROOT}/${ENV_NAME}"

uv python install "${PY_VERSION}"
if [[ ! -d "${ENV_PATH}" ]]; then
  uv venv "${ENV_PATH}" --python "${PY_VERSION}"
fi

# shellcheck disable=SC1091
source "${ENV_PATH}/bin/activate"
uv pip install -r "${REQS_FILE}"

site_packages="$("${ENV_PATH}/bin/python" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
if [[ -z "${site_packages}" ]]; then
  echo "Failed to resolve site-packages for ${ENV_PATH}"
  exit 1
fi
printf '%s\n' "${REPO_ROOT}" > "${site_packages}/context_compass_repo.pth"

echo "Environment ready: ${ENV_PATH}"
