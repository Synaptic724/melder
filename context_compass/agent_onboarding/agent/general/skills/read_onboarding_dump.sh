#!/usr/bin/env bash

set -euo pipefail

dump_path="context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt"
manifest_path="context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt"
max_age_minutes=120
auto_rebuild=1
validate_only=0

usage() {
  cat <<'EOF'
Usage: read_onboarding_dump.sh [--dump <path>] [--manifest <path>] [--max-age-minutes <n>] [--no-auto-rebuild] [--validate-only]

Validates onboarding dump freshness/integrity (timestamp + SHA256) and emits dump content.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dump)
      [[ $# -ge 2 ]] || { echo "Missing value for --dump" >&2; exit 1; }
      dump_path="$2"
      shift 2
      ;;
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
    --no-auto-rebuild)
      auto_rebuild=0
      shift
      ;;
    --validate-only)
      validate_only=1
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

normalize_abs_path() {
  local path_input="$1"
  local repo_root="$2"

  if [[ "$path_input" = /* ]]; then
    (cd "$(dirname "$path_input")" && printf "%s/%s\n" "$(pwd)" "$(basename "$path_input")")
    return 0
  fi

  (cd "$(dirname "$repo_root/$path_input")" && printf "%s/%s\n" "$(pwd)" "$(basename "$repo_root/$path_input")")
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

dump_resolved="$(normalize_abs_path "$dump_path" "$repo_root")"

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

validation_ok=1
validation_reasons=()
dump_built_at_utc=""
dump_built_at_epoch=""
dump_age_minutes=""

validate_dump() {
  local dump_file="$1"
  validation_ok=1
  validation_reasons=()
  dump_built_at_utc=""
  dump_built_at_epoch=""
  dump_age_minutes=""

  if [[ ! -f "$dump_file" ]]; then
    validation_ok=0
    validation_reasons+=("Dump file missing: $dump_file")
    return 0
  fi

  dump_built_at_utc="$(awk -F': ' '/^ONBOARDING_DUMP_BUILT_AT_UTC: /{print $2; exit}' "$dump_file")"
  dump_built_at_epoch="$(awk -F': ' '/^ONBOARDING_DUMP_BUILT_AT_EPOCH: /{print $2; exit}' "$dump_file")"
  dump_manifest_hash="$(awk -F': ' '/^ONBOARDING_DUMP_MANIFEST_SHA256: /{print toupper($2); exit}' "$dump_file")"
  declared_total="$(awk -F': ' '/^ONBOARDING_DUMP_TOTAL_PATHS: /{print $2; exit}' "$dump_file")"

  if [[ -z "$dump_built_at_utc" ]]; then
    validation_ok=0
    validation_reasons+=("Missing ONBOARDING_DUMP_BUILT_AT_UTC header.")
  fi

  if [[ -z "$dump_built_at_epoch" || ! "$dump_built_at_epoch" =~ ^[0-9]+$ ]]; then
    validation_ok=0
    validation_reasons+=("Missing/invalid ONBOARDING_DUMP_BUILT_AT_EPOCH header.")
  else
    now_epoch="$(date -u +%s)"
    dump_age_minutes=$(( (now_epoch - dump_built_at_epoch) / 60 ))
    if (( dump_age_minutes < 0 )); then
      validation_ok=0
      validation_reasons+=("Dump timestamp is in the future: epoch=$dump_built_at_epoch")
    elif (( max_age_minutes >= 0 && dump_age_minutes > max_age_minutes )); then
      validation_ok=0
      validation_reasons+=("Dump is stale. age_minutes=$dump_age_minutes max_age_minutes=$max_age_minutes")
    fi
  fi

  current_manifest_hash="$(hash_file "$manifest_resolved")"
  if [[ -z "$dump_manifest_hash" ]]; then
    validation_ok=0
    validation_reasons+=("Missing ONBOARDING_DUMP_MANIFEST_SHA256 header.")
  elif [[ "$dump_manifest_hash" != "$current_manifest_hash" ]]; then
    validation_ok=0
    validation_reasons+=("Manifest hash mismatch. dump=$dump_manifest_hash current=$current_manifest_hash")
  fi

  if [[ -z "$declared_total" || ! "$declared_total" =~ ^[0-9]+$ ]]; then
    validation_ok=0
    validation_reasons+=("Missing/invalid ONBOARDING_DUMP_TOTAL_PATHS header.")
  elif (( declared_total != ${#manifest_entries[@]} )); then
    validation_ok=0
    validation_reasons+=("Path count mismatch. dump=$declared_total current=${#manifest_entries[@]}")
  fi

  for relative_path in "${manifest_entries[@]}"; do
    expected_line="$(grep -F "ONBOARDING_DUMP_FILE_SHA256: $relative_path|" "$dump_file" | head -n 1 || true)"
    if [[ -z "$expected_line" ]]; then
      validation_ok=0
      validation_reasons+=("Missing file hash entry for: $relative_path")
      continue
    fi

    expected_hash="${expected_line##*|}"
    expected_hash="${expected_hash^^}"

    resolved_path="$(resolve_existing_path \
      "$relative_path" \
      "$repo_root/$relative_path" \
      "$script_dir/$relative_path")" || {
      validation_ok=0
      validation_reasons+=("Readset file missing during validation: $relative_path")
      continue
    }

    actual_hash="$(hash_file "$resolved_path")"
    if [[ "$expected_hash" != "$actual_hash" ]]; then
      validation_ok=0
      validation_reasons+=("File hash mismatch for $relative_path. dump=$expected_hash current=$actual_hash")
    fi
  done

  content_begin_line="$(awk '/^ONBOARDING_DUMP_CONTENT_BEGIN$/{print NR; exit}' "$dump_file")"
  content_end_line="$(awk '/^ONBOARDING_DUMP_CONTENT_END$/{print NR; exit}' "$dump_file")"
  if [[ -z "$content_begin_line" || -z "$content_end_line" || "$content_end_line" -le "$content_begin_line" ]]; then
    validation_ok=0
    validation_reasons+=("Missing or invalid ONBOARDING_DUMP_CONTENT_* markers.")
  fi
}

validate_dump "$dump_resolved"

if [[ $validation_ok -eq 0 && $auto_rebuild -eq 1 ]]; then
  "$script_dir/build_onboarding_dump.sh" --manifest "$manifest_path" --output "$dump_path" >/dev/null
  validate_dump "$dump_resolved"
fi

if [[ $validation_ok -eq 0 ]]; then
  printf 'Onboarding dump validation failed:\n' >&2
  for reason in "${validation_reasons[@]}"; do
    printf ' - %s\n' "$reason" >&2
  done
  exit 1
fi

dump_hash="$(hash_file "$dump_resolved")"
echo "ONBOARDING_DUMP_VALIDATED: true"
echo "ONBOARDING_DUMP_PATH: $dump_resolved"
echo "ONBOARDING_DUMP_BUILT_AT_UTC: $dump_built_at_utc"
if [[ -n "$dump_age_minutes" ]]; then
  echo "ONBOARDING_DUMP_AGE_MINUTES: $dump_age_minutes"
fi
echo "ONBOARDING_DUMP_SHA256: $dump_hash"

if [[ $validate_only -eq 1 ]]; then
  exit 0
fi

awk '
  /^ONBOARDING_DUMP_CONTENT_BEGIN$/ { in_content=1; next }
  /^ONBOARDING_DUMP_CONTENT_END$/ { in_content=0; exit }
  in_content { print }
' "$dump_resolved"
