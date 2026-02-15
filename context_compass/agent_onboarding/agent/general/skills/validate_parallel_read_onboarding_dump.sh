#!/usr/bin/env bash

set -euo pipefail

manifest_path="context_compass/agent_onboarding/parallel_read_onboarding_dump/manifest.txt"
max_age_minutes=120

usage() {
  cat <<'EOF'
Usage: validate_parallel_read_onboarding_dump.sh [--manifest <path>] [--max-age-minutes <n>]

Validates parallel onboarding dump manifest/source/chunk hashes without Python dependencies.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest)
      [[ $# -ge 2 ]] || { echo "Missing value for --manifest" >&2; exit 1; }
      manifest_path="$2"
      shift 2
      ;;
    --max-age-minutes)
      [[ $# -ge 2 ]] || { echo "Missing value for --max-age-minutes" >&2; exit 1; }
      max_age_minutes="$2"
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

if [[ ! "$max_age_minutes" =~ ^-?[0-9]+$ ]]; then
  echo "max-age-minutes must be an integer. Received: $max_age_minutes" >&2
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

manifest_dir="$(cd "$(dirname "$manifest_resolved")" && pwd)"

declare -a reasons=()

chunk_size="$(header_value 'ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: ' "$manifest_resolved")"
total_source_files="$(header_value 'ONBOARDING_PARALLEL_DUMP_TOTAL_SOURCE_FILES: ' "$manifest_resolved")"
total_lines="$(header_value 'ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: ' "$manifest_resolved")"
total_chunks="$(header_value 'ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: ' "$manifest_resolved")"
built_epoch="$(header_value 'ONBOARDING_PARALLEL_DUMP_BUILT_AT_EPOCH: ' "$manifest_resolved")"
source_manifest_raw="$(header_value 'ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST: ' "$manifest_resolved")"
source_manifest_hash_raw="$(header_value 'ONBOARDING_PARALLEL_DUMP_SOURCE_MANIFEST_SHA256: ' "$manifest_resolved")"

[[ "$chunk_size" =~ ^[0-9]+$ ]] || reasons+=("Missing/invalid chunk size header.")
[[ "$total_source_files" =~ ^[0-9]+$ ]] || reasons+=("Missing/invalid total source files header.")
[[ "$total_lines" =~ ^[0-9]+$ ]] || reasons+=("Missing/invalid total lines header.")
[[ "$total_chunks" =~ ^[0-9]+$ ]] || reasons+=("Missing/invalid total chunks header.")

if [[ "$built_epoch" =~ ^[0-9]+$ ]]; then
  now_epoch="$(date -u +%s)"
  age_minutes=$(( (now_epoch - built_epoch) / 60 ))
  if (( age_minutes < 0 )); then
    reasons+=("Manifest build epoch is in the future.")
  elif (( max_age_minutes >= 0 && age_minutes > max_age_minutes )); then
    reasons+=("Manifest is stale. age_minutes=$age_minutes max_age_minutes=$max_age_minutes")
  fi
else
  reasons+=("Missing/invalid build epoch header.")
fi

declare -A source_hashes
while IFS= read -r line; do
  payload="${line#ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_SHA256: }"
  relative_path="${payload%%|*}"
  hash_value="${payload#*|}"
  if [[ -n "$relative_path" && -n "$hash_value" ]]; then
    source_hashes["$relative_path"]="${hash_value^^}"
  fi
done < <(
  awk '
    $0 == "ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_BEGIN" { in_section=1; next }
    $0 == "ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_HASHES_END" { in_section=0; exit }
    in_section && /^ONBOARDING_PARALLEL_DUMP_SOURCE_FILE_SHA256: / { print $0 }
  ' "$manifest_resolved"
)

(( ${#source_hashes[@]} > 0 )) || reasons+=("No source-file hash entries found.")

declare -a chunk_entries=()
while IFS= read -r payload; do
  chunk_entries+=("$payload")
done < <(
  awk '
    $0 == "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_BEGIN" { in_section=1; next }
    $0 == "ONBOARDING_PARALLEL_DUMP_CHUNK_HASHES_END" { in_section=0; exit }
    in_section && /^ONBOARDING_PARALLEL_DUMP_CHUNK: / {
      sub(/^ONBOARDING_PARALLEL_DUMP_CHUNK: /, "", $0)
      print $0
    }
  ' "$manifest_resolved"
)

(( ${#chunk_entries[@]} > 0 )) || reasons+=("No chunk records found.")

if [[ "$total_chunks" =~ ^[0-9]+$ ]] && (( ${#chunk_entries[@]} != total_chunks )); then
  reasons+=("Chunk count mismatch. header=$total_chunks parsed=${#chunk_entries[@]}")
fi

source_manifest_resolved=""
if [[ -z "$source_manifest_raw" ]]; then
  reasons+=("Missing source manifest path header.")
else
  source_manifest_resolved="$(resolve_existing_path \
    "$source_manifest_raw" \
    "$repo_root/$source_manifest_raw" \
    "$script_dir/$source_manifest_raw" || true)"
  if [[ -z "$source_manifest_resolved" ]]; then
    reasons+=("Source manifest path cannot be resolved: $source_manifest_raw")
  else
    source_manifest_hash_actual="$(hash_file "$source_manifest_resolved")"
    if [[ -z "$source_manifest_hash_raw" ]]; then
      reasons+=("Missing source manifest hash header.")
    elif [[ "${source_manifest_hash_raw^^}" != "$source_manifest_hash_actual" ]]; then
      reasons+=("Source manifest hash mismatch.")
    fi
  fi
fi

if [[ -n "$source_manifest_resolved" ]]; then
  mapfile -t source_entries < <(
    awk '
      {
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0);
        if ($0 == "" || $0 ~ /^#/) next;
        print $0;
      }
    ' "$source_manifest_resolved"
  )

  if [[ "$total_source_files" =~ ^[0-9]+$ ]] && (( ${#source_entries[@]} != total_source_files )); then
    reasons+=("Total source files mismatch. header=$total_source_files current=${#source_entries[@]}")
  fi

  for relative_path in "${source_entries[@]}"; do
    if [[ -z "${source_hashes[$relative_path]+set}" ]]; then
      reasons+=("Missing source hash entry for: $relative_path")
      continue
    fi

    resolved_source="$(resolve_existing_path \
      "$relative_path" \
      "$repo_root/$relative_path" \
      "$script_dir/$relative_path" || true)"
    if [[ -z "$resolved_source" ]]; then
      reasons+=("Cannot resolve source file from manifest: $relative_path")
      continue
    fi

    actual_hash="$(hash_file "$resolved_source")"
    if [[ "${source_hashes[$relative_path]}" != "$actual_hash" ]]; then
      reasons+=("Source file hash mismatch: $relative_path")
    fi
  done
fi

sum_chunk_lines=0
expected_start=1
expected_chunk_number=1
for entry in "${chunk_entries[@]}"; do
  IFS='|' read -r chunk_number chunk_name start_line end_line line_count chunk_hash <<< "$entry"

  [[ "$chunk_number" =~ ^[0-9]+$ ]] || { reasons+=("Invalid chunk number entry: $entry"); continue; }
  [[ "$start_line" =~ ^[0-9]+$ ]] || { reasons+=("Invalid chunk start line entry: $entry"); continue; }
  [[ "$end_line" =~ ^[0-9]+$ ]] || { reasons+=("Invalid chunk end line entry: $entry"); continue; }
  [[ "$line_count" =~ ^[0-9]+$ ]] || { reasons+=("Invalid chunk line count entry: $entry"); continue; }

  if (( chunk_number != expected_chunk_number )); then
    reasons+=("Chunk numbering gap/mismatch at position $expected_chunk_number.")
  fi
  expected_chunk_number=$((expected_chunk_number + 1))

  if (( start_line != expected_start )); then
    reasons+=("Chunk start-line discontinuity at $chunk_name: expected=$expected_start actual=$start_line")
  fi
  if (( end_line < start_line )); then
    reasons+=("Chunk end-line is before start-line: $chunk_name")
  fi
  expected_start=$((end_line + 1))

  chunk_path="$manifest_dir/$chunk_name"
  if [[ ! -f "$chunk_path" ]]; then
    reasons+=("Missing chunk file: $chunk_name")
    continue
  fi

  actual_chunk_hash="$(hash_file "$chunk_path")"
  if [[ "${chunk_hash^^}" != "$actual_chunk_hash" ]]; then
    reasons+=("Chunk hash mismatch: $chunk_name")
  fi

  actual_line_count="$(awk 'END{print NR}' "$chunk_path")"
  if (( actual_line_count != line_count )); then
    reasons+=("Chunk line-count mismatch: $chunk_name manifest=$line_count actual=$actual_line_count")
  fi

  sum_chunk_lines=$((sum_chunk_lines + line_count))
done

if [[ "$total_lines" =~ ^[0-9]+$ ]] && (( sum_chunk_lines != total_lines )); then
  reasons+=("Total lines mismatch. header=$total_lines chunks_sum=$sum_chunk_lines")
fi

if (( ${#reasons[@]} > 0 )); then
  printf 'Parallel onboarding dump validation failed:\n' >&2
  for reason in "${reasons[@]}"; do
    printf ' - %s\n' "$reason" >&2
  done
  exit 1
fi

manifest_hash="$(hash_file "$manifest_resolved")"
echo "ONBOARDING_PARALLEL_DUMP_VALIDATED: true"
echo "ONBOARDING_PARALLEL_DUMP_MANIFEST: $manifest_resolved"
echo "ONBOARDING_PARALLEL_DUMP_MANIFEST_SHA256: $manifest_hash"
echo "ONBOARDING_PARALLEL_DUMP_CHUNK_SIZE_LINES: $chunk_size"
echo "ONBOARDING_PARALLEL_DUMP_TOTAL_SOURCE_FILES: $total_source_files"
echo "ONBOARDING_PARALLEL_DUMP_TOTAL_LINES: $total_lines"
echo "ONBOARDING_PARALLEL_DUMP_TOTAL_CHUNKS: $total_chunks"
