# Task: Repair conduit_ward BUG-005 test-double drift (owner pytest run 2026-07-18)

## Metadata
- Task ID: TASK-2026-07-18-conduit-ward-bug005-test-drift
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-18T15:45:04Z
- Updated: 2026-07-18T16:40:00Z

## Problem / Opportunity
The owner's 3.14t pytest run (2026-07-18, --last-failed) shows 7 failures + 3 fixture errors
in tests/unit/melder/aether/conduit/conduit_ward/ caused by the BUG-005 atomic-removal fix
landing without its test doubles/expectations: FakeSpellbook lacks _detach_link_contract
(AttributeError in _remove_contract Phase 1), the sever-atomicity fixture keys
_contracted_spells by an unhashable SimpleNamespace spell_index, and the raise-surface /
rollback / severs-when-empty expectations predate the reversible-detach commit order.

## Ticket Contract
- ENTRY_GATE: routed on attention_board.md to helper_f; owner failure list read.
- EXECUTION_BOUNDARY: conduit_ward tests + their doubles; production _remove_contract only
  if a REAL defect (not drift) is evidenced - then note first.
- DEPENDENCIES: BUG-005 fix in conduit_ward.py:945-1050 (its Contract section).
- EXIT_GATE: all 10 listed tests green on 3.14t or reclassified with evidence.
- FAILURE_ESCALATION: DECISION_REQUEST if the BUG-005 contract itself is wrong.

## Failing set (owner run)
- test_conduit_ward.py::test_remove_contract_raises_when_spellbook_sever_fails
- test_conduit_ward.py::test_remove_contract_raises_when_registry_delete_fails
- test_conduit_ward_contracts.py::test_add_spell_to_contract_rolls_back_root_when_dependency_linking_fails
- test_conduit_ward_contracts.py::test_remove_spell_from_contract_removes_detail_and_severs_contract_when_empty
- test_conduit_ward_contracts.py::test_remove_spell_from_contract_swallows_invalidate_contract_consumers_error
- test_conduit_ward_contracts.py::test_remove_spell_from_contract_succeeds_when_contract_key_lookup_fails
- test_conduit_ward_contracts.py::test_remove_root_from_contracts_severs_when_empty
- test_conduit_ward_contracts.py::test_remove_root_from_contracts_across_all_contracts
- test_conduit_ward_sever_failure_atomicity_regression.py (3 fixture ERRORs: FakeSpellbook
  seed_contracted_spell keys by SimpleNamespace spell_index - unhashable)

## Notes
- DATETIME: 2026-07-18T15:45:04Z
  TYPE: HANDOFF
  CLAIM: Filed by helper_f2 on owner directive (allocate remaining pytest failures per
    subsystem owner). Root symptom: doubles lag the BUG-005 reversible-detach contract.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:945-1050
  IMPACT: Conduit_ward suite red blocks the owner's green-tree checkpoint.
  NEXT: helper_f re-verifies each vs the BUG-005 contract, updates doubles/expectations,
    fixes production only on evidenced defect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T16:05:00Z
  TYPE: PLAN
  CLAIM: helper_f claimed this task (mailbox HANDOFF consumed + ACKed 16:05Z). Plan per the
    ticket boundary: (1) md5-verify every read against live device hashes before use (stale-
    stage law from the epic 14:29Z correction note); (2) re-verify each of the 10 failures
    against the BUG-005 reversible-detach contract in conduit_ward.py; (3) fix DOUBLES and
    EXPECTATIONS first - FakeSpellbook gains the three seams, the sever-atomicity fixture
    stops keying maps by unhashable SimpleNamespace (types.SimpleNamespace defines __eq__ so
    __hash__ is None - my 13:32Z harness defect, caught by first real execution), raise/
    rollback/severs-when-empty expectations move to the two-phase commit order; (4) touch
    production _remove_contract ONLY on evidenced real defect, note-first; (5) validate by
    executing whatever subset imports cleanly in the sandbox harness, report the rest Not run.
  EVIDENCE:
  - tickets/tasks/2026-07-18_conduit_ward_bug005_test_double_drift_task.md:1-40
  IMPACT: Lane is owned; drift repair ordered doubles-first per the execution boundary.
  NEXT: Stage + verify conduit_ward.py and the three test files; per-failure FACT notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T16:40:00Z
  TYPE: DECISION
  CLAIM: All 10 failures repaired as DRIFT (zero production defects found; _remove_contract
    re-verified against its BUG-005 Contract and left untouched). Classification and repair:
    (1) 3 fixture ERRORs in test_conduit_ward_sever_failure_atomicity_regression.py - MY OWN
    harness defect from the 13:32Z push: FakeSpell.spell_index was types.SimpleNamespace,
    which defines __eq__ so __hash__ is None, and it keys _contracted_spells -> TypeError at
    seed. Replaced with a hashable FakeSpellIndex class (identity hashing, matching real
    SpellIndex keying). (2) test_conduit_ward.py::raises_when_spellbook_sever_fails -
    retargeted from the removed _sever_link_contract verb to the second-side detach failure
    lane; now also asserts the first side's exact _reattach restore and that destroy never
    ran. (3) test_conduit_ward.py::raises_when_registry_delete_fails - premise DESIGNED OUT
    (commit step is a plain non-fallible pop; __delitem__ is never invoked); RECLASSIFIED and
    replaced by test_remove_contract_commits_after_detach_with_residue_tolerant_pops, which
    guards the new commit order (pre-dropped peer registry entry cannot fail removal; both
    payloads destroyed; no reattach). (4) 6 failures in test_conduit_ward_contracts.py -
    FakeSpellbook lacked the three BUG-005 seams; added _detach_link_contract /
    _reattach_link_contract / _destroy_detached_link_contract mirroring the real lockstep,
    None-when-absent, refuse-overwrite, and destroy semantics over the fake's 3-map surface,
    plus call tracking; the two severs-when-empty tests now assert detach+destroy per peer
    (and that the legacy sever verb stays uncalled), the other four needed the seams only.
    VALIDATION: extracted-doubles EXECUTED in sandbox - sever-suite fixture seeds/detaches/
    reattaches/destroys end-to-end (old code TypeError reproduced), contracts-suite seams
    prove payload roundtrip, exact restore, refuse-overwrite, lockstep raise, destroy, and
    call-order tracking; per-test traces walked all 10 paths against conduit_ward.py:939-1103.
    py_compile green x3. CRLF preserved on the two Windows-authored files (a first patch pass
    normalized newlines - caught by diff-count gate, redone byte-faithful). Full-suite pytest
    on 3.14t: Not run - rides the owner's next run per EXIT_GATE, REOPEN on red.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_sever_failure_atomicity_regression.py:57-84
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:1354-1425
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py:160-165
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward_contracts.py:336-420
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:939-1103
  IMPACT: The conduit_ward slice of the owner's red set is repaired without touching
    production; the green-tree checkpoint unblocks pending the owner's run.
  NEXT: Owner re-runs the 10 on 3.14t; NOTICE sent to helper_f2; REOPEN on any red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
