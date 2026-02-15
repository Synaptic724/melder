# Task: Add Melder JIT Toggle to `test_shallow_all` Benchmark

## Metadata
- Task ID: TASK-2026-02-15-add-melder-jit-toggle-to-test-shallow-all
- Story: standalone
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Add a benchmark-level Melder configuration toggle in `benchmarks/testing_other_di/test_shallow_all.py` so runs can opt into JIT mode or keep default configuration behavior.

## Scope Boundaries
- In scope:
- Add a Melder-only benchmark env option for compilation mode (`default` vs `jit`, with optional explicit `aot`).
- Apply the option in both Melder runtime builders used by this file.
- Add focused tests for the new toggle helper behavior.
- Out of scope:
- Library runtime behavior changes outside benchmark harness.
- Broad benchmark refactors unrelated to this toggle.

## Steps / Checklist
- [x] Add env-backed helper(s) for Melder compilation mode selection.
- [x] Apply helper in `_build_runtime_melder` and `_build_rotation_melder`.
- [x] Add targeted pytest coverage for helper behavior.
- [x] Run targeted validation for new tests.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Configurable Melder JIT/default benchmark option in `test_shallow_all`.
- Targeted tests validating mode parsing and config application.

## Files / Paths Impacted
- `benchmarks/testing_other_di/test_shallow_all.py`

## Validation
- Ran:
  - `python -m pytest benchmarks/testing_other_di/test_shallow_all.py -q -k "melder_compilation_mode"` -> `4 passed, 48 deselected`
- Notes:
  - Non-blocking pytest cache permission warning on `.pytest_cache` (WinError 5).

## Risks / Rollback Notes
- Risk: accidentally forcing non-default behavior when env var is unset.
- Mitigation: default mode path performs no configuration write.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Melder benchmark builders currently only set `phase_scheduler_workers_per_spellbook` and immediately conjure; there is no benchmark env toggle for JIT/AOT mode.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:1056-1059, benchmarks/testing_other_di/test_shallow_all.py:1092-1092, benchmarks/testing_other_di/test_shallow_all.py:1440-1443, benchmarks/testing_other_di/test_shallow_all.py:1485-1485
  IMPACT: Benchmark runs cannot currently switch JIT on while preserving default behavior when unset.
  NEXT: Add a Melder compilation-mode helper driven by env and apply it in both Melder builders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Added env-driven Melder compilation-mode helpers (`default|jit|aot`), wired them into both Melder runtime builders, and added focused helper tests validating default no-op, JIT false write, AOT true write, and invalid-value fail-fast behavior.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:377-406, benchmarks/testing_other_di/test_shallow_all.py:1090-1090, benchmarks/testing_other_di/test_shallow_all.py:1475-1475, benchmarks/testing_other_di/test_shallow_all.py:1635-1692
  IMPACT: `test_shallow_all` now supports benchmark-level JIT opt-in while preserving current default behavior when env var is unset.
  NEXT: Run targeted pytest for `melder_compilation_mode` tests and record results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Targeted helper test slice passes (`4 passed, 48 deselected`) for Melder compilation mode handling.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:1657-1692
  IMPACT: Benchmark toggle behavior is validated and ready for acceptance review.
  NEXT: Ask user to confirm acceptance criteria, then close and move task to completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The default-mode helper test uses `monkeypatch.delenv(...)`, and user-run full-suite output shows this can still leave ambient mode influence (`full_ahead_of_time_compilation=False`) in this Windows environment, causing the default assertion to fail.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:1657-1664, benchmarks/testing_other_di/test_shallow_all.py:343-348, benchmarks/testing_other_di/test_shallow_all.py:393-406
  IMPACT: The test needs explicit env override to force default mode deterministically.
  NEXT: Replace `delenv` with explicit empty-string `setenv` in the default-mode test and rerun `-k "melder_compilation_mode"`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The helper implementation currently hardcodes `_melder_compilation_mode` default as `"jit"` instead of `"default"`, so unset/empty env forces JIT and breaks expected default behavior.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:377-390, benchmarks/testing_other_di/test_shallow_all.py:393-405
  IMPACT: This is the direct cause of the failing default-mode test and wrong runtime default semantics for benchmark runs.
  NEXT: Change the helper default literal to `"default"` and rerun targeted `melder_compilation_mode` tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: After fixing helper default mode to `"default"`, targeted mode tests now pass (`4 passed, 48 deselected`), including the default-mode no-write assertion.
  EVIDENCE: benchmarks/testing_other_di/test_shallow_all.py:377-390, benchmarks/testing_other_di/test_shallow_all.py:1657-1665
  IMPACT: Benchmark toggle now preserves default behavior when env is unset/empty and supports explicit JIT/AOT overrides.
  NEXT: Return task to review and ask user to confirm acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation and follow-up fix are complete. Pending user acceptance confirmation to close and move task to completed.
