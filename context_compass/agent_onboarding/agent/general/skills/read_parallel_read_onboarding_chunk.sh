#!/usr/bin/env bash

set -euo pipefail

manifest_path="context_compass/agent_onboarding/parallel_read_onboarding_dump/manifest.txt"
chunk_number=1
summary_only=0
validate_first=0

usage() {
  cat <<'EOF'
Usage: read_parallel_read_onboarding_chunk.sh [--manifest <path>] [--chunk-number <n>] [--summary-only] [--validate-first]

Reads one onboarding_read_XX chunk from the parallel onboarding dump.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest)
      [[ $# -ge 2 ]] || { echo "Missing value for --manifest" >&2; exit 1; }
      manifest_path="$2"
      shift 2
      ;;
    --chunk-number)
      [[ $# -ge 2 ]] || { echo "Missing value for --chunk-number" >&2; exit 1; }
      chunk_number="$2"
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

if [[ ! "$chunk_number" =~ ^[0-9]+$ ]] || (( chunk_number < 1 )); then
  echo "chunk-number must be >= 1. Received: $chunk_number" >&2
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

header_value() {
  local prefix="$1"
  local file_path="$2"
  awk -v p="$prefix" 'index($0, p) == 1 { sub(p, "", $0); print $0; exit }' "$file_path"
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../../../.." && pwd)"

manifest_resolved="$(resolve_existing_path \
  "$manifest_path" \
  "$repo_root/$manifest_path" \
  "$script_dir/$manifest_path")" || {
  echo "Manifest not found: $manifest_path" >&2
  exit 1
}

if (( validate_first == 1 )); then
  "$script_dir/validate_parallel_read_onboarding_dump.sh" --manifest "$manifest_resolved" >/dev/null
fi

manifest_dir="$(cd "$(dirname "$manifest_resolved")" && pwd)"
chunk_size_lines="$(header_value 'ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: ' "$manifest_resolved")"
total_chunks="$(header_value 'ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: ' "$manifest_resolved")"

chunk_entry="$(
  awk -v target="$chunk_number" '
    $0 == "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_BEGIN" { in_section=1; next }
    $0 == "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_END" { in_section=0; exit }
    in_section && /^ONBOARDING_PARALLEL_DUMP_CHUNK: / {
      sub(/^ONBOARDING_PARALLEL_DUMP_CHUNK: /, "", $0)
      split($0, parts, "|")
      if (parts[1] == target) {
        print $0
        exit
      }
    }
  ' "$manifest_resolved"
)"

if [[ -z "$chunk_entry" ]]; then
  echo "chunk-number out of range. chunk_number=$chunk_number total_chunks=$total_chunks" >&2
  exit 1
fi

IFS='|' read -r record_chunk_number chunk_name start_line end_line line_count chunk_hash <<< "$chunk_entry"
chunk_path="$manifest_dir/$chunk_name"

if [[ ! -f "$chunk_path" ]]; then
  echo "Chunk file not found: $chunk_path" >&2
  exit 1
fi

echo "ONBOARDING_PARALLEL_CHUNK_MANIFEST: $manifest_resolved"
echo "ONBOARDING_PARALLEL_CHUNK_NUMBER: $record_chunk_number"
echo "ONBOARDING_PARALLEL_CHUNK_FILE: $chunk_name"
echo "ONBOARDING_PARALLEL_CHUNK_PATH: $chunk_path"
echo "ONBOARDING_PARALLEL_CHUNK_SIZE_LINES: $chunk_size_lines"
echo "ONBOARDING_PARALLEL_TOTAL_CHUNKS: $total_chunks"
echo "ONBOARDING_PARALLEL_CHUNK_START_LINE: $start_line"
echo "ONBOARDING_PARALLEL_CHUNK_END_LINE: $end_line"
echo "ONBOARDING_PARALLEL_CHUNK_LINE_COUNT: $line_count"

if (( summary_only == 1 )); then
  exit 0
fi

echo "ONBOARDING_PARALLEL_CHUNK_CONTENT_BEGIN: chunk=$record_chunk_number"
cat "$chunk_path"
echo "ONBOARDING_PARALLEL_CHUNK_CONTENT_END: chunk=$record_chunk_number"
