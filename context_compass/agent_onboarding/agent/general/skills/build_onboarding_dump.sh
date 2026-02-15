#!/usr/bin/env bash

set -euo pipefail

manifest_path="context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt"
output_path="context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt"

usage() {
  cat <<'EOF'
Usage: build_onboarding_dump.sh [--manifest <path>] [--output <path>]

Serializes the onboarding readset into a single dump file.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest)
      [[ $# -ge 2 ]] || { echo "Missing value for --manifest" >&2; exit 1; }
      manifest_path="$2"
      shift 2
      ;;
    --output)
      [[ $# -ge 2 ]] || { echo "Missing value for --output" >&2; exit 1; }
      output_path="$2"
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

if [[ "$output_path" = /* ]]; then
  output_resolved="$output_path"
else
  output_resolved="$repo_root/$output_path"
fi

mkdir -p "$(dirname "$output_resolved")"

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

built_at_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
built_at_epoch="$(date -u +%s)"
manifest_hash="$(hash_file "$manifest_resolved")"
meta_tmp="$(mktemp)"
content_tmp="$(mktemp)"
trap 'rm -f "$meta_tmp" "$content_tmp"' EXIT

for relative_path in "${manifest_entries[@]}"; do
  resolved_path="$(resolve_existing_path \
    "$relative_path" \
    "$repo_root/$relative_path" \
    "$script_dir/$relative_path")" || {
    echo "Missing readset file: $relative_path" >&2
    exit 1
  }

  file_hash="$(hash_file "$resolved_path")"
  printf 'ONBOARDING_DUMP_FILE_SHA256: %s|%s\n' "$relative_path" "$file_hash" >> "$meta_tmp"

  {
    echo "===== BEGIN FILE: $relative_path ====="
    cat "$resolved_path"
    printf '\n'
    echo "===== END FILE: $relative_path ====="
  } >> "$content_tmp"
done

{
  echo "ONBOARDING_DUMP_VERSION: 2"
  echo "ONBOARDING_DUMP_BUILT_AT_UTC: $built_at_utc"
  echo "ONBOARDING_DUMP_BUILT_AT_EPOCH: $built_at_epoch"
  echo "ONBOARDING_DUMP_MANIFEST: $manifest_path"
  echo "ONBOARDING_DUMP_SOURCE: $manifest_resolved"
  echo "ONBOARDING_DUMP_MANIFEST_SHA256: $manifest_hash"
  echo "ONBOARDING_DUMP_HASH_ALGO: SHA256"
  echo "ONBOARDING_DUMP_TOTAL_PATHS: ${#manifest_entries[@]}"
  echo "ONBOARDING_DUMP_FILE_HASHES_BEGIN"
  cat "$meta_tmp"
  echo "ONBOARDING_DUMP_FILE_HASHES_END"
  echo "ONBOARDING_DUMP_CONTENT_BEGIN"
  cat "$content_tmp"
  echo "ONBOARDING_DUMP_CONTENT_END"
  echo "ONBOARDING_DUMP_COMPLETE: ${#manifest_entries[@]} files serialized."
} > "$output_resolved"

dump_hash="$(hash_file "$output_resolved")"

echo "ONBOARDING_DUMP_WRITTEN: $output_resolved"
echo "ONBOARDING_DUMP_FILES: ${#manifest_entries[@]}"
echo "ONBOARDING_DUMP_BUILT_AT_UTC: $built_at_utc"
echo "ONBOARDING_DUMP_SHA256: $dump_hash"
