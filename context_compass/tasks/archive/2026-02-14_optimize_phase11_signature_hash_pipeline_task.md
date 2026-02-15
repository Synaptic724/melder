Completed: 2026-02-14
Summary: Accepted in closure pass; implementation/discovery outcomes are complete and archived.

# Task: Optimize Phase11 Signature Hash Pipeline

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase11-signature-hash-pipeline
- Story: STORY-2026-02-13-optimize-spellcrafter-phases
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce phase11 signature generation overhead in codegen export while preserving
deterministic signatures and invalidation semantics.

## Scope Boundaries
- In scope:
- `_hash_codegen_signature`, `_serialize_codegen_signature_part`, and
  phase11 variant signature assembly paths.
- Low-risk hashing/serialization reductions that keep output stable.
- Out of scope:
- Altering signature schema fields or weakening invalidation correctness.
- Non-phase11 hashing infrastructure.

## Steps / Checklist
- [x] Quantify signature hot segments (`pickle.dumps`, steps row signatures, transient signatures).
- [x] Implement deterministic fastpaths that avoid redundant serialization/hashing work.
- [x] Add/adjust tests for signature determinism and unchanged compile invalidation behavior.
- [x] Validate via focused phase11 tests and component harness cProfile output.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Lower cumulative time in phase11 signature helpers during warm profile runs.
- Evidence-backed parity for signature correctness.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "signature or phase11 or serialize_codegen_signature_part or hash_codegen_signature_fastpaths"` -> `28 passed, 123 deselected`; outputs:
  - `context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests.txt`
  - `context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests_run2.txt`
  - `context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests_run3.txt`
  - `context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests_run4.txt` (contains one expected-failure iteration later fixed)
  - `context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests_run5.txt`
  - `context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests_run6.txt`
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed, 3 warnings`; outputs:
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output.txt` (regression attempt; discarded)
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run2.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run3.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run4.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run5.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run6.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt`

## Risks / Rollback Notes
- Risk: signature drift causing stale or over-eager phase12 recompilation.
- Rollback: revert to current hash/serialize pipeline.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Tuple-hash signature update for `steps_rows_signature` reduced warm signature-path churn: `_serialize_codegen_signature_part` calls dropped `996 -> 612`, `_pickle.dumps` dropped `724 -> 340`, warm total moved `10.833ms -> 9.804ms`, and cProfile sample moved `0.036s -> 0.034s`.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1756-1758, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-41
  IMPACT: Rank-2 now shows measurable warm-path gain instead of near-neutral drift while preserving payload schema and deterministic invalidation semantics.
  NEXT: Hold for user acceptance and close/move if approved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Focused signature/phase11 unit suite still passes after tuple-hash update (`28 passed, 123 deselected`) with no schema contract changes.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests_run6.txt:12-12, src/melder/spellbook/spell_crafter/spell_crafter.py:1756-1758
  IMPACT: Confirms signature-path change is behavior-safe for covered phase11 contracts.
  NEXT: Keep task in review pending acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase11 variant signature currently hashes `steps_rows` by splatting every row (`_hash_codegen_signature(*steps_rows)`), which increases per-row serializer churn in warm runs.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1752-1759, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:33-36
  IMPACT: The signature path performs more `_serialize_codegen_signature_part` calls than needed for stable invalidation, keeping avoidable overhead in the rank-2 hot path.
  NEXT: Change `steps_rows_signature` to hash the tuple payload as one part, then rerun focused unit + harness validations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Final implementation keeps Phase11 payload/schema unchanged and narrows optimization to serializer dispatch only: container-first pickle fallback plus scalar fastpaths (`None/bool/int/float/str/bytes/bytearray`), with no tuple-row signature conversion.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:753-794, src/melder/spellbook/spell_crafter/spell_crafter.py:1767-1812, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4833-4901
  IMPACT: Preserves existing `steps_rows`/`steps_rows_signature` behavior while reducing pickle calls in signature serialization.
  NEXT: Keep-vs-iterate decision based on measured warm delta and cProfile trend.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Compared to the rank-1 anchor, final runs are near-neutral in wall time while reducing pickle call count (`996 -> 724`): warm `group_8_11_total_ms` moved from `10.567` to `10.552/10.833`, and warm cProfile sample moved from `0.035s` to `0.036s`.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run6.txt:7-39, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-39
  IMPACT: Signature-pipeline changes are safe and micro-optimized internally, but global warm-phase benefit is not materially above current anchor.
  NEXT: Decide whether to accept this as a low-risk cleanup or iterate on a different rank-2 approach.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Focused signature/phase11 unit suite passed after final adjustments (`28 passed, 120 deselected`), including new serializer fastpath/fallback tests.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase11_signature_pipeline_unit_tests_run5.txt:1-12, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4833-4901
  IMPACT: Confirms deterministic signature behavior and compile-invalidating semantics remain intact for covered phase11 paths.
  NEXT: Present measured outcome to user for acceptance direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: The first serializer rewrite regressed warm phase8-11 heavily (`group_8_11_total_ms=46.369`, warm cProfile `0.221s`) and made `_serialize_codegen_signature_part` dominant via recursive byte-join overhead.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output.txt:7-26
  IMPACT: Current branch implementation is not acceptable; recursive container serialization must be removed or narrowed.
  NEXT: Replace recursive container fastpath with scalar-only fastpath + pickle fallback, then rerun focused unit/harness validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Keep `steps_rows` schema unchanged (dict rows) for Phase12/override consumers, but change only signature derivation path: compute `steps_rows_signature` from deterministic tuple rows plus serializer fastpaths for primitive/container types before pickle fallback.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:242-263, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:153-171, src/melder/spellbook/spell_crafter/spell_crafter.py:1681-1812
  IMPACT: Preserves external IR payload contract while reducing hash/serialize overhead in hot phase11 export loops.
  NEXT: Implement serializer fastpaths and tuple-row signature helper; then run focused spell-crafter unit tests and harness profile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current signature serialization always attempts `pickle.dumps(part, protocol=5)` for each hash part, and warm phase8-11 profiling shows this path called 3984 times (`_pickle.dumps` cumtime ~0.010s) inside `_serialize_codegen_signature_part`.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:753-773, src/melder/spellbook/spell_crafter/spell_crafter.py:776-797, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:30-33
  IMPACT: Signature generation overhead is materially driven by generic pickle serialization, making deterministic primitive fastpaths a high-confidence optimization target.
  NEXT: Implement deterministic tagged-byte fastpaths for common scalar types before pickle fallback, then validate signature parity with unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Warm phase8-11 cProfile still shows meaningful cost in phase11 signature assembly path (`_build_phase11_variant_ir_payload` + `_hash_codegen_signature` + `_serialize_codegen_signature_part` + `pickle.dumps`).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:18-33, src/melder/spellbook/spell_crafter/spell_crafter.py:747-792, src/melder/spellbook/spell_crafter/spell_crafter.py:1741-1807
  IMPACT: Signature/hash pipeline is a high-confidence second-wave optimization target after capture-frequency reduction.
  NEXT: Build a micro-profile baseline for signature helper call counts and inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Rank-2 execution is implemented and validated with an evidence trail including a
discarded regression attempt and final stabilized serializer-dispatch approach.
Final code keeps signature schema/contracts intact and now includes tuple-hash
signature derivation for `steps_rows_signature`, reducing serializer and pickle
call volume while improving warm profile shape in the latest harness run.
Next step is user direction: accept rank-2 and close/move, or request another
optimization iteration.
