#!/usr/bin/env bash

set -euo pipefail

manifest_path="context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt"
output_dir="context_compass/agent_onboarding/parallel_read_onboarding_dump"
chunk_size_lines=500

usage() {
  cat <<'EOF'
Usage: build_parallel_read_onboarding_dump.sh [--manifest <path>] [--output-dir <path>] [--chunk-size-lines <n>]

Builds onboarding chunk artifacts named onboarding_read_XX under parallel_read_onboarding_dump.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest)
      [[ $# -ge 2 ]] || { echo "Missing value for --manifest" >&2; exit 1; }
      manifest_path="$2"
      shift 2
      ;;
    --output-dir)
      [[ $# -ge 2 ]] || { echo "Missing value for --output-dir" >&2; exit 1; }
      output_dir="$2"
      shift 2
      ;;
    --chunk-size-lines)
      [[ $# -ge 2 ]] || { echo "Missing value for --chunk-size-lines" >&2; exit 1; }
      chunk_size_lines="$2"
      shift 2
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

if [[ ! "$chunk_size_lines" =~ ^[0-9]+$ ]] || (( chunk_size_lines <= 0 )); then
  echo "chunk-size-lines must be a positive integer. Received: $chunk_size_lines" >&2
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

hash_file() {
  local target="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$target" | awk '{print toupper($1)}'
    return 0
  fi
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$target" | awk '{print toupper($1)}'
    return 0
  fi
  echo "Missing sha256 tool (sha256sum/shasum)." >&2
  return 1
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

if [[ "$output_dir" = /* ]]; then
  output_resolved="$output_dir"
else
  output_resolved="$repo_root/$output_dir"
fi

mkdir -p "$output_resolved"
manifest_output="$output_resolved/manifest.txt"

mapfile -t manifest_entries < <(
  awk '
    {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0);
      if ($0 == "" || $0 ~ /^#/) next;
      print $0;
    }
  ' "$manifest_resolved"
)

if [[ ${#manifest_entries[@]} -eq 0 ]]; then
  echo "Manifest produced no readable entries: $manifest_resolved" >&2
  exit 1
fi

combined_tmp="$(mktemp)"
source_hash_tmp="$(mktemp)"
chunk_hash_tmp="$(mktemp)"
trap 'rm -f "$combined_tmp" "$source_hash_tmp" "$chunk_hash_tmp"' EXIT

for relative_path in "${manifest_entries[@]}"; do
  resolved_path="$(resolve_existing_path \
    "$relative_path" \
    "$repo_root/$relative_path" \
    "$script_dir/$relative_path")" || {
    echo "Missing readset file: $relative_path" >&2
    exit 1
  }

  file_hash="$(hash_file "$resolved_path")"
  printf 'ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_SHA256: %s|%s\n' "$relative_path" "$file_hash" >> "$source_hash_tmp"

  printf '===== BEGIN FILE: %s =====\n' "$relative_path" >> "$combined_tmp"
  cat "$resolved_path" >> "$combined_tmp"
  printf '\n' >> "$combined_tmp"
  printf '===== END FILE: %s =====\n' "$relative_path" >> "$combined_tmp"
done

total_lines="$(wc -l < "$combined_tmp" | tr -d '[:space:]')"
if [[ -z "$total_lines" || "$total_lines" -eq 0 ]]; then
  echo "Combined onboarding content is empty." >&2
  exit 1
fi

total_chunks=$(( (total_lines + chunk_size_lines - 1) / chunk_size_lines ))
pad_width="${#total_chunks}"
if (( pad_width < 2 )); then
  pad_width=2
fi

rm -f "$output_resolved"/onboarding_read_* "$manifest_output"

for ((chunk_number = 1; chunk_number <= total_chunks; chunk_number++)); do
  start_line=$(( (chunk_number - 1) * chunk_size_lines + 1 ))
  end_line=$(( chunk_number * chunk_size_lines ))
  if (( end_line > total_lines )); then
    end_line="$total_lines"
  fi
  line_count=$(( end_line - start_line + 1 ))

  chunk_name="$(printf "onboarding_read_%0${pad_width}d" "$chunk_number")"
  chunk_path="$output_resolved/$chunk_name"

  sed -n "${start_line},${end_line}p" "$combined_tmp" > "$chunk_path"
  chunk_hash="$(hash_file "$chunk_path")"
  printf 'ONBOARDING_PARALLEL_DUMP_CHUNK: %d|%s|%d|%d|%d|%s\n' \
    "$chunk_number" "$chunk_name" "$start_line" "$end_line" "$line_count" "$chunk_hash" >> "$chunk_hash_tmp"
done

built_at_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
built_at_epoch="$(date -u +%s)"
source_manifest_hash="$(hash_file "$manifest_resolved")"

{
  echo "ONBOARDING_PARALLEL_DUMP_VERSION: 1"
  echo "ONBOARDING_PARALLEL_DUMP_BUILT_AT_UTC: $built_at_utc"
  echo "ONBOARDING_PARALLEL_DUMP_BUILT_AT_EPOCH: $built_at_epoch"
  echo "ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: $chunk_size_lines"
  echo "ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST: $manifest_path"
  echo "ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST_RESOLVED: $manifest_resolved"
  echo "ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST_SHA256: $source_manifest_hash"
  echo "ONBOARDING_PARALLEL_DUMP_TOTAL_SOURCE_FILES: ${#manifest_entries[@]}"
  echo "ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: $total_lines"
  echo "ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: $total_chunks"
  echo "ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_BEGIN"
  cat "$source_hash_tmp"
  echo "ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_END"
  echo "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_BEGIN"
  cat "$chunk_hash_tmp"
  echo "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_END"
  echo "ONBOARDING_PARALLEL_DUMP_COMPLETE: $total_chunks chunks serialized."
} > "$manifest_output"

manifest_hash="$(hash_file "$manifest_output")"
echo "ONBOARDING_PARALLEL_DUMP_WRITTEN: $output_resolved"
echo "ONBOARDING_PARALLEL_DUMP_MANIFEST: $manifest_output"
echo "ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: $chunk_size_lines"
echo "ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: $total_lines"
echo "ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: $total_chunks"
echo "ONBOARDING_PARALLEL_DUMP_MANIFEST_SHA256: $manifest_hash"
