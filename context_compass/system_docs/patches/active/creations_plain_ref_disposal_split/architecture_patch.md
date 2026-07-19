# architecture_patch

## Metadata
- Patch ID: creations_plain_ref_disposal_split
- Status: draft
- Owner: codex
- Created: 2026-05-26T22:36:42Z
- Updated: 2026-05-26T22:36:42Z

## Patch Scope and Non-Goals
- Objective:
  Split retained creation storage into plain refs for non-disposable entries
  and disposal-tracked entries that still carry explicit disposal metadata.
- Non-goals:
  - changing `many` retention semantics
  - redesigning spellspace ownership
  - changing phase 10-12 planning contracts

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| creations | modify | remove universal wrapper assumption from retained storage | none |
| meld | modify | retrieval paths currently assume every retained entry is a `Creation` | creations |
| creation_runtime_codegen | modify | generated runtime lookup paths currently assume `creation.value` | creations |

## Interface and Boundary Deltas
- Boundary delta 1:
  `Creations` stops treating `Creation` as the universal retained-entry shape.
- Interface delta 1:
  extract/restore payloads must carry generic stored-entry shapes, not only
  `Creation` wrappers.

## Cross-Component Invariants
- Invariant 1:
  non-disposable retained entries remain reusable and retrievable.
- Invariant 2:
  explicit disposal still runs only for entries registered with disposal
  metadata.
- Invariant 3:
  spellspace retained entries preserve spellspace isolation.

## Migration and Rollout Order
1. Update `Creations` storage and extract/restore semantics.
2. Update `Meld` retrieval paths.
3. Update generated creation runtime lookup/registration seams.
4. Validate transfer and pooled-reset paths.

## Rollback Strategy
- Rollback trigger:
  incorrect retrieval or transfer behavior under focused validation.
- Rollback steps:
  restore universal `Creation` storage and revert retrieval assumptions.
- Post-rollback verification:
  rerun the focused conduit/meld/creations rings.

## Validation Expectations and Evidence Plan
- Validation item 1:
  direct `Creations` unit behavior across unique/spellspace/transfer paths.
- Evidence source 1:
  focused conduit/creations unit tests.
- Validation item 2:
  `Meld` and generated no-overrides/overrides paths still retrieve correctly.
- Evidence source 2:
  focused meld/conduit execution tests.

## Ticket Coverage Map
- Epic: none
- Story: none
- Tasks:
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
  - `tickets/tasks/2026-05-26_implement_plain_ref_creation_storage_for_non_disposable_entries_task.md`

## Unknowns and Decision Requests
- UNKNOWN:
  whether any currently unexercised transfer rollback path depends on raw
  `Creation` identity beyond extract/restore payload passing.
- DECISION_REQUEST:
  none

## Context / Handoff Summary
- What changed:
  patch lane opened for the storage split
- What remains:
  implementation plus focused validation
- Next entrypoint:
  `component_patch_creations.md`
