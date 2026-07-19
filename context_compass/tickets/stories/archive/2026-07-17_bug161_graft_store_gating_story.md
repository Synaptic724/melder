# Story: BUG-161 - Explicit graft storage disabled by the automatic-upload knob

## Metadata
- Story ID: STORY-2026-07-17-bug161-graft-store-gating
- Epic: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p2
- Severity: Medium
- Created: 2026-07-18T16:02:55Z
- Updated: 2026-07-18T16:02:55Z

## Root Cause (verified against current source)
AssetManagementSystem.store_index_graft gated on manager.store_enabled, which is
`store_handler is not None AND upload_on_flush` (external_persistence_manager.py:314-328).
store_index_graft is an EXPLICIT, generic store operation, but turning off automatic
flush uploads (upload_on_flush=False) also made store_enabled False, so an otherwise
valid explicitly-invoked graft store was refused with 'requires a store lane' even though
a handler was attached (audit BUG-161).

## Fix (root cause)
Added a has_store_handler property (store_handler presence, independent of upload_on_flush)
and gated store_index_graft on it instead of store_enabled. Explicit graft storage now
depends on handler presence; the automatic checkpoint-flush upload policy no longer governs
it. This composes cleanly with the BUG-162 fix: the store lane is present at the gate, so a
False from store_unit still unambiguously means the remote handler failed.

## Scope Boundaries
- In scope: external_persistence_manager.py (new has_store_handler) + asset_management_system.py
  (store_index_graft gate) + a regression.
- Out of scope: the flush/upload lanes (which correctly still honor upload_on_flush).

## Tasks (Implementation Checklist)
- [x] Re-verify BUG-161 against current source (store_enabled couples handler + upload_on_flush).
- [x] Add has_store_handler (presence-only) property.
- [x] Gate store_index_graft on handler presence, not store_enabled.
- [x] Add a regression (handler present + upload_on_flush=False -> store still ships).
- [ ] User runs the asset-management suite on 3.14t and accepts.

## Acceptance Criteria
- store_index_graft ships with a handler attached regardless of upload_on_flush; the no-store-lane
  refusal still holds when no handler is attached; the suite is green on the user's 3.14t run.

## Validation / Test Plan
- Re-verified against current source; py_compile OK on both changed modules.
- Regression added (upload_on_flush=False + store handler -> store_index_graft returns the id and
  the row is stored). The existing no-store-lane refusal test still guards the absent-handler path.
- Full pytest Not run in-container (AssetManagementSystem import chain + tmp fixtures need 3.14t).
  Agent test-run status: Not run under pytest; the user runs the suite on 3.14t.

## Risks / Mitigations
- Risk: widening the gate could let a store through in an unintended config. Mitigation: it only
  requires a store handler to be explicitly attached; a read-only (no-handler) config still refuses.

## Applicable Anti-Patterns
- [x] Reproduced/verified against source before fixing.
- [x] Root-cause (correct gate), not a defensive guard.
- [ ] No closure before the user's suite run.

## Decision Log
- DATETIME: 2026-07-18T16:02:55Z
  TYPE: DECISION
  CLAIM: Add a presence-only has_store_handler accessor and gate the explicit store on it, keeping store_enabled (handler + upload_on_flush) for the automatic flush lanes that should honor the knob.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
BUG-161 fixed: explicit graft storage now depends on store-handler presence, not the auto-upload
knob. Status review, pending the user's 3.14t suite run. This completes story 06's High+Medium
graft-lane pair (161/162); story 06 now has only BUG-160 and BUG-163 (Medium) remaining.
