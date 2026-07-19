# component_patch_system_docs

## Metadata
- Patch ID: source_doc_namespace_normalization_2026_06_12
- Component: system_docs source surfaces
- Status: in_progress
- Owner: codex
- Created: 2026-06-12T13:00:58Z
- Updated: 2026-06-12T13:00:58Z

## Component Purpose and Boundary
- Current boundary:
  - `src_architecture.md`, `src_components.md`, `src_graph.json`, and
    `readable_src_graph.json` still carried stale path and namespace truth
    from older tree layouts and older public API naming
- Target boundary:
  - those surfaces point at the live non-mutation/non-crystallizer source tree
    and preserve only directly evidenced runtime/compiler naming

## Before/After Behavior Summary
- Before:
  - narrative docs still pointed at old `src/melder/spellbook/**` and old
    `src/melder/aether/nexus/**` paths
  - public conjure posture still described `automatic`
  - canonical/readable graph still held stale spellbook/nexus namespace and
    path families
- After:
  - main narrative docs point at the live spellbook and nexus roots
  - conjure posture is described through `dynamic`
  - graph surfaces are normalized through the patch-lane working copy and
    regenerated readable output

## Interface Deltas
- Inputs:
  - live file-path and module-namespace truth from `src/melder/**`
  - existing system-doc narrative and graph surfaces
- Outputs:
  - corrected narrative references
  - corrected canonical graph storage
  - regenerated readable graph view
- Error semantics:
  - malformed graph changes are rejected by JSON validation before recompression

## State and Lifecycle Deltas
- Owned state changes:
  - patch-lane working copy:
    `system_docs/patches/active/source_doc_namespace_normalization_2026_06_12/src_graph.expanded.json`
- Lifecycle/cleanup changes:
  - the expanded graph remains the edit surface until this patch lane closes

## Failure Mode Deltas
- New failure mode:
  - a mechanical rename can accidentally create references to non-existent
    live paths if not re-verified against the filesystem
- Removed failure mode:
  - the obvious stale spellbook-root and nexus-root path references in the two
    main narrative docs
- Changed failure mode:
  - remaining drift is now narrower and more semantic, not broad obvious
    namespace mismatch

## Dependency and Ordering Constraints
1. Narrative doc updates must stay synchronized with the graph normalization.
2. Canonical graph must be regenerated from the expanded working copy only.
3. Readable graph must be regenerated only after canonical recompression.

## Validation Expectations
- Test/validation item 1:
  - stale path/API scans shrink after each slice
- Evidence target 1:
  - targeted `rg` counts over source docs and graph surfaces
- Test/validation item 2:
  - canonical and readable graph parse as JSON
- Evidence target 2:
  - `ConvertFrom-Json` validation

## Unknowns and Open Decisions
- UNKNOWN:
  - whether the next highest-value seam is compiler-narrative cleanup or
    aetheric-frame/dev-ops path/ownership cleanup
- DECISION_REQUEST:
  - none yet

## Context / Handoff Summary
- What changed:
  - this component patch captures the current system-doc surface normalization
    work and its mechanical boundaries
- Remaining risks:
  - deeper semantic drift remains beyond the obvious namespace/path layer
- Next entrypoint:
  - `system_docs/src_architecture.md`
