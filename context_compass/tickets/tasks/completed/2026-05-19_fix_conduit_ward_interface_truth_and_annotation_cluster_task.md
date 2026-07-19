# Task: fix conduit ward interface truth and annotation cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-conduit-ward-interface-truth-and-annotation-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T10:56:28Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `conduit_ward.py` mypy cluster by correcting stale public
interface drift, tightening local annotation/narrowing issues, and keeping the
result truthful to the real runtime contracts.

## Ticket Contract
- ENTRY_GATE: the user supplied a bounded `conduit_ward.py` mypy cluster and
  explicitly directed interface-first fixes with no weird shims.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
  - directly implicated public interfaces only where the surface is real:
    - `src/melder/utilities/interfaces/iconduitward.py`
    - `src/melder/utilities/interfaces/idetail.py`
    - `src/melder/utilities/interfaces/ispellbook.py`
    - `src/melder/utilities/interfaces/ispell.py`
    - `src/melder/utilities/interfaces/iconduit.py`
    - `src/melder/utilities/interfaces/icontract.py`
  - directly implicated contract concretes only if interface truth requires it:
    - `src/melder/aether/conduit/conduit_ward/contract/contract.py`
    - `src/melder/aether/conduit/conduit_ward/contract/details.py`
    - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- DEPENDENCIES:
  - current conduit/cloud/cluster owner model
  - existing public typing contract policy for interfaces
  - no casts, no fake local protocols, no compatibility shims
- EXIT_GATE:
  - the targeted `conduit_ward.py` mypy cluster is gone
  - stale/lying public interfaces are corrected at the source
  - validation confirms the bounded slice
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any implicated interface
  appears to expose the wrong architectural responsibility and the correct
  public contract is ambiguous

## Scope Boundaries
- In scope:
  - stale public interface truth causing the `conduit_ward.py` cluster
  - local annotation/narrowing fixes tied to that truth
  - contract concrete alignment when the interface is already the real public
    contract
- Out of scope:
  - unrelated repo-wide mypy debt
  - broader conduit/aether redesign beyond directly implicated surfaces

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user supplied a new bounded conduit-ward cluster and
  explicitly requested interface-first mypy fixes

## Steps / Checklist
- [ ] identify the stale public interface surfaces first
- [ ] patch truthful interface contracts before local concrete fixes
- [ ] patch local `ConduitWard` annotations and narrowings
- [ ] rerun targeted mypy on the conduit-ward ring
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded conduit-ward interface-truth fix
- a bounded conduit-ward annotation/narrowing fix

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/utilities/interfaces/iconduitward.py`
- `src/melder/utilities/interfaces/idetail.py`
- `src/melder/utilities/interfaces/ispellbook.py`
- `src/melder/utilities/interfaces/ispell.py`
- only if required by the truthful fix:
  - `src/melder/utilities/interfaces/icontract.py`
  - `src/melder/utilities/interfaces/iconduit.py`
  - `src/melder/aether/conduit/conduit_ward/contract/contract.py`
  - `src/melder/aether/conduit/conduit_ward/contract/details.py`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\conduit_ward\conduit_ward.py`

## Risks / Rollback Notes
- Medium risk. Several errors point at public interface drift, so the main
  danger is widening the public contract in the wrong direction.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T10:56:28Z
  TYPE: FACT
  CLAIM: The new `conduit_ward.py` cluster is not just local annotation noise.
    It includes stale public interface truth on at least three seams: `IDetail`
    is too thin for the real contract concrete, `ISpellbook` is missing
    spellbook-owned key helpers that `ConduitWard` legitimately uses, and some
    local conduit/lesser-parent typing is being forced through the wrong surface.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1401-1453
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1604-1708
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1924-1926
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2600-2967
  - src/melder/utilities/interfaces/idetail.py:1-19
  - src/melder/utilities/interfaces/ispellbook.py:1-220
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:1-220
  IMPACT: This should be fixed by correcting interface truth first, then
    tightening the local `ConduitWard` annotations. Treating it as local-only
    mypy cleanup would risk encoding the wrong public contract.
  NEXT: inspect the real `Detail` and `Spellbook` surfaces against the failing
    uses, then decide the minimal truthful interface delta.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T10:56:28Z
  TYPE: FACT
  CLAIM: The next truthful interface delta is already visible. `IDetail` is
    missing the actual contract surface used across `Contract` and
    `ConduitWard` (`spell_index`, `spell_id`, `permissions`, `contract_type`,
    `reason`, `sources`, `has_version`, `add_source`, `remove_source`), and
    `ISpellbook` is missing the real key/lookup helpers
    `_make_spell_key(...)` and `_assert_lookup_key_available(...)` that
    `ConduitWard` legitimately uses.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/contract/details.py:1-189
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:183-231
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1401-1453
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1604-1708
  - src/melder/utilities/interfaces/idetail.py:1-19
  - src/melder/spellbook/spellbook.py:1344-1416
  - src/melder/utilities/interfaces/ispellbook.py:625-625
  IMPACT: The clean next move is to patch public interface truth first, then
    revisit the remaining local `ConduitWard` errors without inventing new fake
    fields on unrelated objects.
  NEXT: update `IDetail`, `IConduitWard`, and `ISpellbook` to match the real
    public contract, then rerun the local error pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T10:56:28Z
  TYPE: FACT
  CLAIM: The first interface patch is landed. `IDetail` now matches the real
    contract detail object, `IConduitWard` now carries the source-aware detail
    and removal parameters the concrete already uses, and `ISpellbook` now
    exposes the real lookup-key helpers that `ConduitWard` consumes.
  EVIDENCE:
  - src/melder/utilities/interfaces/idetail.py:1-31
  - src/melder/utilities/interfaces/iconduitward.py:1-760
  - src/melder/utilities/interfaces/ispellbook.py:620-700
  IMPACT: A large slice of the current cluster should now collapse without
    touching runtime behavior. The next pass can focus on local `ConduitWard`
    typing mistakes and any remaining truly missing public surface.
  NEXT: patch the remaining local `ConduitWard` errors, starting with the
    lesser-parent seam and the optional-id narrowings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T10:56:28Z
  TYPE: FACT
  CLAIM: After the local ward typing pass, the residual failures split cleanly.
    Most are stale tests asserting the wrong seam (`child._parent_conduit`
    instead of the ward-owned parent link, and `spell.__name__` instead of the
    spell contract's `spell_name`). One remaining real bug exists in
    `_remove_root_from_contracts(...)`: an indentation error marks a contract
    as successful even when only one source tag was removed and the detail
    stayed alive.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1947-1985
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:294-307
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:391-418
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:470-492
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:1852-1870
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py:1456-1484
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py:2955-2975
  IMPACT: We need one real runtime fix plus a small stale-test sync. The lane
    is still bounded; this is not broader architecture drift.
  NEXT: fix the `removed_any` indentation bug, then retarget the stale ward
    tests to the current public/runtime seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T10:56:28Z
  TYPE: MEASURE
  CLAIM: The bounded conduit-ward lane is green. `conduit_ward.py` has no
    file-local mypy output after the interface/local fixes, and the full
    conduit-ward unit ring passes after syncing the stale tests to the ward-
    owned parent-link seam and the spell-name contract.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1-3010
  - src/melder/utilities/interfaces/idetail.py:1-31
  - src/melder/utilities/interfaces/iconduitward.py:1-860
  - src/melder/utilities/interfaces/ispellbook.py:620-700
  - src/melder/utilities/interfaces/icontract.py:1-120
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:294-492
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:1366-1407
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:1852-1878
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py:1456-1484
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py:2955-2975
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\conduit_ward\conduit_ward.py 2>&1 | Select-String 'src\\melder\\aether\\conduit\\conduit_ward\\conduit_ward.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\conduit_ward` -> `452 passed, 1 warning`
  IMPACT: The user-supplied ward cluster is fixed without casts or shims. The
    real runtime bug was the source-tag success-report indentation in
    `_remove_root_from_contracts(...)`; the rest of the surfaced ward failures
    were stale tests or stale public contracts.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:58:51Z
  TYPE: FACT
  CLAIM: The reopened residual cluster is split between one transfer-side
    interface truth seam and a small local ward cleanup. On the transfer side,
    `IConduit.get_conduit_cloud()` is still typed too weakly to support the
    real public cloud usage, and `transfer_of_ownership.py` is still reaching
    through `_conduit_cloud._get_cluster(...)` plus raw Aether frame internals
    even though the runtime already has better seams (`get_conduit_cloud()` and
    `IAether._get_existing_frame(...)`). On the ward side, the remaining items
    are local: one recursive lesser-conduit return path, one enum-normalization
    return, and two missing parameter annotations on contract helpers.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduit.py:1055-1065
  - src/melder/utilities/interfaces/iconduitcloud.py:1-170
  - src/melder/aether/conduit/conduit.py:2844-2867
  - src/melder/aether/conduit_cloud.py:486-538
  - src/melder\aether\conduit\conduit_ward\transfer\transfer_of_ownership.py:389-404
  - src/melder\aether\conduit\conduit_ward\transfer\transfer_of_ownership.py:555-575
  - src/melder\aether\conduit\conduit_ward\transfer\transfer_of_ownership.py:928-945
  - src/melder\aether\conduit\conduit_ward\transfer\transfer_of_ownership.py:1081-1126
  - src/melder\aether\conduit\conduit_ward\conduit_ward.py:995-1021
  - src/melder\aether\conduit\conduit_ward\conduit_ward.py:1762-1768
  - src/melder\aether\conduit\conduit_ward\conduit_ward.py:2256-2322
  IMPACT: The bounded fix should not expose more private fields. It should
    strengthen the public cloud return contract, add one truthful cluster
    accessor on the cloud interface, move transfer off raw Aether registry
    reach-through, and then finish the local ward annotations.
  NEXT: patch `IConduit`/`IConduitCloud` plus the transfer caller, then clean
    the four remaining local `ConduitWard` typing errors and rerun bounded
    validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:58:51Z
  TYPE: FACT
  CLAIM: The implementation stayed bounded and behavior-preserving. Transfer
    now uses the existing public cloud path (`get_conduit_cloud()`) plus one
    thin public cluster accessor on `IConduitCloud`/`ConduitCloud`, and the raw
    Aether frame-registry reach-through was replaced with a conduit-owner check
    through `_get_conduit_by_spell_id(...)`. The remaining ward residuals were
    local annotations only.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitcloud.py:1-170
  - src/melder/aether/conduit_cloud.py:500-552
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:389-404
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:433-447
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:928-941
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1092-1138
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1008-1021
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1762-1772
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2256-2330
  IMPACT: The lane is ready for bounded validation without widening into new
    architectural surfaces or changing import/runtime behavior.
  NEXT: run filtered mypy on `transfer_of_ownership.py` and `conduit_ward.py`,
    then rerun the focused transfer/ward unit rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:58:51Z
  TYPE: MEASURE
  CLAIM: The file-local mypy slice is clean, but the transfer unit ring now
    fails on stale fake conduit surfaces. The runtime caller moved from private
    `_conduit_cloud` reach-through to the real public `get_conduit_cloud()`
    seam, while the transfer fakes still only provide `_conduit_cloud`.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\conduit_ward\transfer\transfer_of_ownership.py src\melder\aether\conduit\conduit_ward\conduit_ward.py 2>&1 | Select-String 'src\\melder\\aether\\conduit\\conduit_ward\\transfer\\transfer_of_ownership.py:|src\\melder\\aether\\conduit\\conduit_ward\\conduit_ward.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\conduit_ward` -> failures rooted at `FakeConduit` missing `get_conduit_cloud()`
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py: failing trace through preflight borrower enumeration
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:389-404
  IMPACT: The runtime code looks correct for the intended public seam; the next
    bounded step is syncing the transfer fakes to that seam instead of backing
    the runtime out to the old private field path.
  NEXT: patch the transfer test fakes to expose `get_conduit_cloud()` and rerun
    the same ward unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T12:58:51Z
  TYPE: FACT
  CLAIM: After syncing the public cloud seam on the transfer fakes, the
    remaining ward failures all reduce to one more stale fake contract:
    `_spell_in_registry(...)` now uses `IAether._get_existing_frame(...)`, but
    both fake Aether classes still expose only `_get_frame(...)`. That makes
    every registry-presence probe fall back to `False`, which then cascades
    into the execute/snapshot/rollback assertions.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:931-958
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:481-690
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:440-640
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\conduit_ward` -> remaining failures rooted in `_spell_in_registry(...)`
  IMPACT: The runtime code still looks correct and behavior-preserving. The
    next bounded step is to add `_get_existing_frame(...)` to the fake Aether
    test doubles rather than backing the runtime out to the removed raw frame
    registry seam.
  NEXT: patch both fake Aether classes with `_get_existing_frame(...)` as the
    test-facing alias to `_get_frame(...)`, then rerun the same ward unit ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T13:10:21Z
  TYPE: MEASURE
  CLAIM: The reopened residual cluster is green. The transfer caller now uses
    the public cloud seam plus a truthful cluster accessor, the raw Aether
    frame-registry reach-through is gone, the local ward annotations are
    clean, and the stale transfer fakes were synchronized to the new public
    seams. The full ward unit ring passes again.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitcloud.py:1-175
  - src/melder/utilities/interfaces/iaethericframe.py:1-115
  - src/melder/aether/conduit_cloud.py:500-552
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:389-404
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:433-458
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:479-496
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:931-958
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1092-1138
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1008-1021
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1762-1772
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2256-2330
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:451-955
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:410-902
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\conduit_ward\transfer\transfer_of_ownership.py src\melder\aether\conduit\conduit_ward\conduit_ward.py 2>&1 | Select-String 'src\\melder\\aether\\conduit\\conduit_ward\\transfer\\transfer_of_ownership.py:|src\\melder\\aether\\conduit\\conduit_ward\\conduit_ward.py:'` -> no output
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\conduit_ward` -> `452 passed, 1 warning`
  IMPACT: The user-supplied reopened ward/transfer cluster is fixed without
    shims or behavior changes to the live transfer/import/runtime paths.
  NEXT: report the bounded fix and wait for the next exact mypy/runtime bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active conduit-ward interface-truth lane. Current evidence says the right order
is:
1. correct stale public interfaces,
2. patch local ConduitWard typing/narrowing,
3. rerun targeted mypy on the file.
