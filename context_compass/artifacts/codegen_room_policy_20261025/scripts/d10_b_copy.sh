#!/usr/bin/env bash
# Copy the checkout to a fresh /tmp tree for D-10's option-B runs (melder_0, 2026-10-25).
# usage: d10_b_copy.sh <dir>   (copies src, tests, pyproject.toml and the files the whole suite reads; not docs/)
set -eu
dest="${1:?dir}"; repo="$HOME/mnt/melder_private"
mkdir -p "$dest" /tmp/m0s2/tmp
rsync -a --delete --exclude __pycache__ --exclude __melder_cache__ --exclude "*.pyc" --exclude .pytest_cache \
  "$repo/src" "$repo/tests" "$repo/pyproject.toml" "$repo/README.md" "$repo/.readthedocs.yaml" "$repo/codecov.yml" \
  "$repo/benchmarks" "$repo/llm_support" "$repo/.github" "$repo/release_docs" "$repo/architecture_and_design" \
  "$repo/UX_and_AIX_experiences" "$dest/"
mkdir -p "$dest/context_compass"
rsync -a --delete "$repo/context_compass/system_docs" "$dest/context_compass/"
echo "copied to $dest: $(du -sh "$dest" | cut -f1)"
