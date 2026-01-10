#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cc_root="$(cd "${script_dir}/../../../.." && pwd)"

"${cc_root}/system/ai_restricted/system_management/environment_check.sh" "$@"
