# architecture_patch

## Metadata
- Patch ID: source_doc_namespace_normalization_2026_06_12
- Status: in_progress
- Owner: codex
- Created: 2026-06-12T13:00:58Z
- Updated: 2026-06-12T13:00:58Z

## Patch Scope and Non-Goals
- Objective:
  - normalize stale source-file and module-namespace references in the active
    source-system docs so they match the live tree
  - repair the public conjure posture wording where the live API now uses
    `dynamic`
  - repair the canonical graph through expand-edit-compress and regenerate the
    readable graph view
- Non-goals:
  - mutation-research or crystallizer documentation refresh
  - broad narrative rewrites without a directly evidenced drift seam
  - low-signal file inventory work for `__init__`, metadata shims, caches, or
    pyc files

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| source architecture narrative | modify | stale path and conjure API references were misleading the runtime story | live source verification |
| source components narrative | modify | stale path and compiler-owner references were misleading component contracts | live source verification |
| canonical graph surfaces | modify | node/file/edge namespace drift made the graph disagree with the live source tree | patch-lane expanded graph copy |

## Interface and Boundary Deltas
- Boundary delta 1:
  - source-system docs now treat the live spellbook root as
    `src/melder/aether/spellbook/**`, not `src/melder/spellbook/**`
- Boundary delta 2:
  - public AR runtime paths now live under `src/melder/nexus/**`, not
    `src/melder/aether/nexus/**`
- Interface delta 1:
  - public Spellbook conjure posture is described through `dynamic`, not
    `automatic`
- Interface delta 2:
  - high-level compiler ownership is described as `SpellCompiler` / `SpellCompilerArtifact`
    where the live code proves those names

## Cross-Component Invariants
- canonical docs must point at real live files
- graph edits must continue through expand-edit-compress
- mutation-research and crystallizer references remain out of scope for this
  patch unless required by a later explicit lane
- readable graph output must remain valid JSON and stay within the 220-char
  line contract

## Migration and Rollout Order
1. Verify the live path and namespace drift in narrative docs and graph.
2. Patch the high-signal narrative seams first.
3. Patch the expanded graph working copy.
4. Recompress canonical graph storage.
5. Regenerate the readable graph view.
6. Re-measure remaining stale namespace/path residue before widening scope.

## Rollback Strategy
- Rollback trigger:
  - any normalization pass introduces non-existent live paths or invalid JSON
- Rollback steps:
  1. restore the pre-patch expanded graph working copy from git if needed
  2. overwrite canonical graph from the restored working copy
  3. revert narrative doc edits for the affected slice only
- Post-rollback verification:
  - canonical and readable graph JSON parse
  - doc references again point at existing files or are explicitly marked stale

## Validation Expectations and Evidence Plan
- Validation item 1:
  - `src_graph.json` parses after recompression
- Evidence source 1:
  - `ConvertFrom-Json` over canonical graph
- Validation item 2:
  - `readable_src_graph.json` parses and stays at 220-char max line length
- Evidence source 2:
  - `ConvertFrom-Json` plus max-line-length measurement
- Validation item 3:
  - targeted stale path/API scans materially shrink after each slice
- Evidence source 3:
  - `rg -n` / `rg -c` scans over the source docs and graph surfaces

## Ticket Coverage Map
- Epic:
  - `tickets/epics/2026-06-12_investigate_source_system_doc_drift_excluding_mutation_and_crystallizer_epic.md`
- Story:
  - `tickets/stories/2026-06-12_investigate_aether_directory_doc_drift_story.md`
- Tasks:
  - `tickets/tasks/2026-06-12_investigate_current_source_system_doc_drift_task.md`

## Unknowns and Decision Requests
- UNKNOWN:
  - how much of the remaining compiler/aetheric-frame/dev-ops narrative drift
    is still safely mechanical versus needing a deeper content pass
- DECISION_REQUEST:
  - none yet; continue with surgical non-mutation audit slices

## Context / Handoff Summary
- What changed:
  - this patch lane formalizes the current source-doc namespace and graph
    normalization work
- What remains:
  - deeper non-mutation narrative seams still need verification
- Next entrypoint:
  - `tickets/tasks/2026-06-12_investigate_current_source_system_doc_drift_task.md`
