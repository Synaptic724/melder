# Story: BUG-162 - Failed remote graft store reported as successfully shipped

## Metadata
- Story ID: STORY-2026-07-17-bug162-graft-store-failure-truth
- Epic: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p1
- Severity: High
- Created: 2026-07-18T14:11:45Z
- Updated: 2026-07-18T14:11:45Z

## Root Cause (verified against current source)
AssetManagementSystem.store_index_graft (asset_management_system.py:819-825) called
manager.store_unit(...) but DISCARDED its bool result and unconditionally returned the
index_id. In lenient mode (strict_uploads=False) store_unit converts a raising store
handler into False and increments store_failure_count (external_persistence_manager.py:390-402).
So a graft whose only remote store failed was reported to the caller as shipped. Unlike the
checkpoint/formation lanes, the graft lane has NO local durable fallback, so the caller can
discard its sole copy believing it is safely stored (audit BUG-162).

## Fix (root cause)
store_index_graft now honors the store_unit outcome: it captures the bool and, when the
store did not succeed, raises RuntimeError explaining the remote store failed and this lane
has no durable fallback (suggesting retry or strict_uploads). The success path is unchanged
(returns index_id only when the unit actually shipped). Chose raise over a failure sentinel
to stay consistent with the method's existing RuntimeError contract (cleaned / no manager /
no store lane) and its str return; strict_uploads already surfaces the handler error directly.
Because the method passed the store_enabled gate, a handler is attached, so a False from
store_unit unambiguously means the handler failed (never the no-op no-handler branch).

## Scope Boundaries
- In scope: asset_management_system.py store_index_graft + a regression test.
- Out of scope: the other two store_unit call sites (checkpoint/formation have a durable
  fallback and correctly ignore the bool; the emission lane at :990 already returns it).
  BUG-161 (Medium, same method gates on store_enabled/upload_on_flush) is adjacent and remains.

## Tasks (Implementation Checklist)
- [x] Re-verify BUG-162 against current source (store_unit bool discarded).
- [x] Honor the store_unit outcome; raise on a failed store (no phantom success).
- [x] Update the docstring Raises contract.
- [x] Add a lenient-failure regression (raising handler -> RuntimeError, no stored row).
- [ ] User runs the asset-management suite on 3.14t and accepts.

## Acceptance Criteria
- A failing remote store makes store_index_graft raise (not return the id); the successful
  round-trip test still passes; the suite is green on the user's 3.14t run.

## Validation / Test Plan
- Logic re-verified against current source; py_compile OK on the changed module.
- store_unit's False-on-lenient-failure behavior is already covered by
  test_record_version_and_json_contract.py (raising handler -> False, count 1), so the fix is
  the composition 'False -> raise'. New regression asserts the composed behavior end to end.
- Full pytest Not run in-container (AssetManagementSystem import chain + tmp fixtures need 3.14t).
  Agent test-run status: Not run under pytest; the user runs the suite on 3.14t.

## Risks / Mitigations
- Risk: a caller previously relying on the (buggy) always-success return now sees a raise.
  Mitigation: that path was silently losing data; raising is the intended durability contract
  and no in-repo test/caller depended on the false success.

## Applicable Anti-Patterns
- [x] Reproduced/verified against source before fixing.
- [x] Root-cause (honor the outcome), not a defensive guard.
- [ ] No closure before the user's suite run.

## Decision Log
- DATETIME: 2026-07-18T14:11:45Z
  TYPE: DECISION
  CLAIM: Signal graft store failure by raising RuntimeError (consistent with the method's existing raises and str return) rather than adding a failure sentinel; strict_uploads still surfaces the raw handler error.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
BUG-162 fixed: store_index_graft honors store_unit's outcome and raises when the only remote
store failed, so a graft is never reported durable when its sole copy never shipped. Status
review, pending the user's 3.14t suite run. Adjacent BUG-161 (upload_on_flush gating) remains.
