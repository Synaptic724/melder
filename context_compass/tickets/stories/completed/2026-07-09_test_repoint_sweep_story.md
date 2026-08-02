# Story: test re-point sweep + suite re-homing (S-test)

- Completed: 2026-07-10T09:10:00Z
- Summary: 3 suites re-homed onto their real owners + the describe boundary
  assertion + the auto-flush cadence regression; import paths were already
  final from the S2-S4 sweeps. Owner-run FULL crystallizer tree 614/614;
  owner accepted at epic closure.

## Metadata
- Story ID: STORY-2026-07-09-test-repoint-sweep
- Parent Epic: EPIC-2026-07-09-crystallizer-subsystem-decomposition
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-10T07:20:00Z
- Updated: 2026-07-10T07:20:00Z

## Problem / Opportunity
The epic's test DECISION (00:10Z) deferred bulk test alignment to one sweep
after S4. In practice the import-path halves were swept en route (S2/S3/S4
gates all read zero repo-wide), so the residue is verb-level: suites that
drove the old ledger verbs directly, plus the cadence lane no test covered.

## Ticket Contract
- ENTRY_GATE: S4 sentinel GREEN (owner, 2026-07-10).
- EXECUTION_BOUNDARY: test tree only (re-homing + one regression); zero src
  changes.
- EXIT_GATE: owner-run FULL crystallizer tree green (unit + component +
  integration) - the epic's tranche-law exit.
- FAILURE_ESCALATION: any failure implicating src semantics -> CONFLICT.

## Tasks
- [x] T1: verb-caller inventory (tool-layer grep over the whole test tree
      for every removed/reshaped verb): exactly 3 files -
      test_kit_export_import.py (profile-cache suite),
      test_crystallizer_cache.py (2 tests), test_persistence_system.py
      (boot-verb test). All import paths were already final (S2-S4 sweeps).
- [x] T2: RE-HOMED the profile-cache suite onto AssetManagementSystem
      (borrowed-record pattern, borrower-before-owner teardown, on-disk
      probes via a public CrystallizerCache surface instead of the old
      `system._crystallizer_cache` internal reach).
- [x] T3: RE-HOMED the cache suite's two system-verb tests onto asset
      flush/reload verbs (insert-if-absent + flush-all contracts kept
      verbatim).
- [x] T4: RE-HOMED the boot-verb test onto CrystalLoaderSystem + EXTENDED
      it: asserts the additive world-scope admission view and the durable
      describe_last_load state.
- [x] T5: NEW auto-flush cadence regression
      (test_auto_flush_cadence_ships_the_automatic_seal, integration
      suite): the S3 lane that called a removed verb - caught by gate grep,
      never by a test - now has a symptom-named harness proving the cadence
      seal reaches the cache.
- [ ] T6: owner-run full crystallizer tree; on green this story closes and
      S5 (doc/graph promotion) opens.

## Acceptance Criteria
- Zero test files reference removed/reshaped ledger verbs (grep-proven).
- Owner-run full crystallizer tree green.

## Applicable Anti-Patterns
- [ ] Re-homing preserves contracts verbatim (no assertion weakening).
- [ ] "Not run." until the owner runs.

## Noting Behavior
- Story notes: inventory evidence + run results.

## Notes
- DATETIME: 2026-07-10T07:20:00Z
  TYPE: FACT
  CLAIM: T1-T5 complete in one pass. Inventory surprise (good): the epic
    planned a big re-point sweep, but S2-S4 swept import paths to FINAL
    homes en route, leaving only 3 verb-level re-homes + 1 new regression.
    Parse floor: kit suite PARSE OK; the other three edited files hit the
    null-tail replica variant (bash reads them truncated mid-docstring at
    pre-edit lengths) - all three DISKS verified complete via tool-layer
    reads (cache :150-162, persistence_system :280-289, integration
    cadence test at :801). Execution: Not run - owner full-tree run
    requested.
  EVIDENCE:
  - tests/unit/melder/crystallizer/persistence/test_kit_export_import.py:1-160
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:801-835
  IMPACT: The whole crystallizer test tree should now be green - the
    epic's bulk-red window closes.
  NEXT: owner runs the full tree (commands in the board row / report).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-10T07:45:00Z
  TYPE: FACT
  CLAIM: FULL-TREE RUN 1 (owner): 613/614 GREEN across unit + component +
    integration (integration rerun 13/13 first). The single failure was one
    more verb-level residue my T1 inventory missed - the ledger describe()
    test asserting the `cached_checkpoint_count` key S3 deliberately moved
    to the asset system (my grep swept CALL sites, not KEY assertions).
    FIX: the test now asserts the key's ABSENCE with a boundary-law comment
    ("the record owns no disk truth") - it enforces the split instead of
    contradicting it. Execution: Not run - rerun of the one file requested.
  EVIDENCE:
  - tests/unit/melder/crystallizer/persistence/test_persistence_system.py:315-341
  IMPACT: 614/614 expected; S-test exit gate then satisfied.
  NEXT: owner reruns test_persistence_system.py; on green S-test closes,
    S5 opens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Verb-level re-homing of 3 suites onto the S3/S4 owners + the cadence
regression; import paths were already final. Owner full-tree run gates S5.
