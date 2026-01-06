#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
CONTEXT_ROOT="$(cd -- "${SCRIPT_DIR}/../../../.." >/dev/null 2>&1 && pwd)"
LANG_FILE="${CONTEXT_ROOT}/system/config/languages.json"

mkdir -p "$(dirname "${LANG_FILE}")"

cat > "${LANG_FILE}" <<'JSON'
{"default_language":"unknown","directory_hints":{},"extensions":{"py":"python"},"schema_version":1}
JSON

echo "Wrote python-only language config: ${LANG_FILE}"
