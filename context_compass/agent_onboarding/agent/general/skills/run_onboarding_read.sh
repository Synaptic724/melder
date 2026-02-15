#!/usr/bin/env bash

set -euo pipefail

manifest_path="context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt"
emit_content=1
metadata_only=0

usage() {
  cat <<'EOF'
Usage: run_onboarding_read.sh [--manifest <path>] [--emit-content] [--metadata-only]

Reads every path in the onboarding manifest and prints file contents by default.
Use --metadata-only to print hashes/line counts without file contents.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest)
      [[ $# -ge 2 ]] || { echo "Missing value for --manifest" >&2; exit 1; }
      manifest_path="$2"
      shift 2
      ;;
    --emit-content)
      emit_content=1
      shift
      ;;
    --metadata-only)
      metadata_only=1
      emit_content=0
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

echo "READSET_MANIFEST: $manifest_resolved"
echo "READSET_TOTAL_PATHS: ${#manifest_entries[@]}"

index=0
for relative_path in "${manifest_entries[@]}"; do
  index=$((index + 1))
  resolved_path="$(resolve_existing_path \
    "$relative_path" \
    "$repo_root/$relative_path" \
    "$script_dir/$relative_path")" || {
    echo "Missing readset file: $relative_path" >&2
    exit 1
  }

  echo "READSET_ITEM[$index/${#manifest_entries[@]}]: $relative_path"

  if [[ $metadata_only -eq 1 ]]; then
    line_count="$(wc -l < "$resolved_path" | tr -d '[:space:]')"
    byte_count="$(wc -c < "$resolved_path" | tr -d '[:space:]')"
    file_hash="$(hash_file "$resolved_path")"
    echo "READSET_META[$index/${#manifest_entries[@]}]: lines=$line_count | bytes=$byte_count | sha256=$file_hash"
  fi

  if [[ $emit_content -eq 1 ]]; then
    echo "===== BEGIN FILE: $relative_path ====="
    cat "$resolved_path"
    echo "===== END FILE: $relative_path ====="
  fi
done

echo "READSET_COMPLETE: ${#manifest_entries[@]} files processed."
