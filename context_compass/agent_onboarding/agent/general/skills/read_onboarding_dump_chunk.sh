#!/usr/bin/env bash

set -euo pipefail

dump_path="context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt"
chunk_size=500
chunk_index=0
summary_only=0
validate_first=0

usage() {
  cat <<'EOF'
Usage: read_onboarding_dump_chunk.sh [--dump <path>] [--chunk-size <n>] [--chunk-index <n>] [--summary-only] [--validate-first]

Reads one chunk from onboarding_read_dump.txt. Default chunk size is 500 lines.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dump)
      [[ $# -ge 2 ]] || { echo "Missing value for --dump" >&2; exit 1; }
      dump_path="$2"
      shift 2
      ;;
    --chunk-size)
      [[ $# -ge 2 ]] || { echo "Missing value for --chunk-size" >&2; exit 1; }
      chunk_size="$2"
      shift 2
      ;;
    --chunk-index)
      [[ $# -ge 2 ]] || { echo "Missing value for --chunk-index" >&2; exit 1; }
      chunk_index="$2"
      shift 2
      ;;
    --summary-only)
      summary_only=1
      shift
      ;;
    --validate-first)
      validate_first=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! "$chunk_size" =~ ^[0-9]+$ ]] || (( chunk_size <= 0 )); then
  echo "chunk-size must be a positive integer. Received: $chunk_size" >&2
  exit 1
fi

if [[ ! "$chunk_index" =~ ^[0-9]+$ ]]; then
  echo "chunk-index must be a non-negative integer. Received: $chunk_index" >&2
  exit 1
fi

resolve_existing_path() {
  local candidate=""
  for candidate in "$@"; do
    [[ -n "$candidate" ]] || continue
    if [[ -f "$candidate" ]]; then
      (cd "$(dirname "$candidate")" && printf "%s/%s\n" "$(pwd)" "$(basename "$candidate")")
      return 0
    fi
  done
  return 1
}

normalize_abs_path() {
  local path_input="$1"
  local repo_root="$2"

  if [[ "$path_input" = /* ]]; then
    (cd "$(dirname "$path_input")" && printf "%s/%s\n" "$(pwd)" "$(basename "$path_input")")
    return 0
  fi

  (cd "$(dirname "$repo_root/$path_input")" && printf "%s/%s\n" "$(pwd)" "$(basename "$repo_root/$path_input")")
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../../../.." && pwd)"

if (( validate_first == 1 )); then
  "$script_dir/read_onboarding_dump.sh" --dump "$dump_path" --validate-only >/dev/null
fi

dump_resolved="$(resolve_existing_path \
  "$dump_path" \
  "$repo_root/$dump_path" \
  "$script_dir/$dump_path")" || {
  echo "Dump path not found: $dump_path" >&2
  exit 1
}

mapfile -t dump_lines < "$dump_resolved"
total_lines=${#dump_lines[@]}

if (( total_lines == 0 )); then
  echo "Dump file is empty: $dump_resolved" >&2
  exit 1
fi

total_chunks=$(( (total_lines + chunk_size - 1) / chunk_size ))

if (( chunk_index >= total_chunks )); then
  echo "chunk-index out of range. chunk_index=$chunk_index total_chunks=$total_chunks max_index=$((total_chunks - 1))" >&2
  exit 1
fi

start_zero=$(( chunk_index * chunk_size ))
end_zero=$(( start_zero + chunk_size - 1 ))
if (( end_zero >= total_lines )); then
  end_zero=$(( total_lines - 1 ))
fi

start_one=$(( start_zero + 1 ))
end_one=$(( end_zero + 1 ))
chunk_line_count=$(( end_zero - start_zero + 1 ))

echo "DUMP_CHUNK_PATH: $dump_resolved"
echo "DUMP_CHUNK_SIZE: $chunk_size"
echo "DUMP_TOTAL_LINES: $total_lines"
echo "DUMP_TOTAL_CHUNKS: $total_chunks"
echo "DUMP_CHUNK_INDEX: $chunk_index"
echo "DUMP_CHUNK_START_LINE: $start_one"
echo "DUMP_CHUNK_END_LINE: $end_one"
echo "DUMP_CHUNK_LINE_COUNT: $chunk_line_count"

if (( summary_only == 1 )); then
  exit 0
fi

echo "DUMP_CHUNK_CONTENT_BEGIN: index=$chunk_index"
for ((i = start_zero; i <= end_zero; i++)); do
  printf '%s\n' "${dump_lines[$i]}"
done
echo "DUMP_CHUNK_CONTENT_END: index=$chunk_index"
