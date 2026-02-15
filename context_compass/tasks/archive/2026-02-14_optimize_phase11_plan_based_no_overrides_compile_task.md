Completed: 2026-02-14
Summary: Accepted in the phase-testing closure pass; implementation and validation artifacts are captured in this task.

# Task: Optimize Phase11 Plan-Based No-Overrides Compile Path

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase11-plan-based-no-overrides-compile
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce warm phase11 overhead by removing no-overrides IR row payload building
from `run_phase_execution_plan` compile-signature checks while preserving
phase12 no-overrides compile invalidation correctness.

## Scope Boundaries
- In scope:
- Add a plan-based phase12 no-overrides compile/signature path for phase11 hot execution.
- Keep existing codegen-IR payload compile path for lazy `codegen_ir` readers.
- Add focused tests for compile cache invalidation and run-phase behavior.
- Out of scope:
- Rewriting phase11 builder internals.
- Changing exported phase8-11 IR payload schema contracts.

## Steps / Checklist
- [x] Confirm current warm hotspot and compile-path contract boundaries.
- [x] Implement plan-based no-overrides compile/signature path in SpellCrafter.
- [x] Add/adjust focused unit tests for plan-based compile cache behavior and phase11 path wiring.
- [x] Rerun targeted spell-crafter tests and component harness profile.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase11 no-overrides compile path that no longer builds hot IR row payloads
  in `run_phase_execution_plan`.
- Validation artifacts showing contract parity and warm profile delta.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "run_phase_execution_plan or compile_phase12_no_overrides_executor or plan_based_no_overrides_compile"` (pass; `10 passed, 145 deselected`)
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (pass; `1 passed`)
- Artifacts:
  - `context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt`

## Risks / Rollback Notes
- Risk: plan-based signature misses semantic fields and causes stale executor reuse.
- Rollback: revert `run_phase_execution_plan` to payload-based compile path and
  keep lazy full IR capture behavior.

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
  CLAIM: Post-fix reruns are green: targeted spell-crafter slice now passes (`10 passed`) and the phase component harness rerun passes (`1 passed`) while retaining warm phase11 profiling output.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:59-59
  IMPACT: Task is unblocked for review/closure routing with fresh validation artifacts.
  NEXT: Route updated status into the backlog story + attention board and ask for acceptance/closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Fixed test-fixture contract drift by extending `_make_phase11_plan_stub` to always expose `root_instance_key` (defaulting to `(root_spell_id, None)`), matching `ExecutionPlan` expectations used by plan-signature compilation.
  EVIDENCE: tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4234-4265, src/melder/spellbook/spell_crafter/spell_crafter.py:1838-1875
  IMPACT: Preserves strict production plan contracts and removes the two AttributeError failures in plan-based compile cache tests.
  NEXT: Re-run targeted slice and harness and record pass artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: The new plan-based compile cache tests currently fail because `_build_phase12_no_overrides_plan_signature` assumes `plan.root_instance_key` exists, but test stubs use `types.SimpleNamespace` plans without that attribute in one branch.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt:56-58, context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt:94-97, context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt:157-159, context_compass/artifacts/2026-02-14_phase11_plan_based_compile_targeted_unit_tests.txt:195-197, src/melder/spellbook/spell_crafter/spell_crafter.py:1838-1869
  IMPACT: Targeted unit validation is red (`2 failed`) and blocks task closure until signature helper tolerates plan stubs used by current tests.
  NEXT: Patch `_build_phase12_no_overrides_plan_signature` to handle missing `root_instance_key` safely, then rerun targeted unit and component harness validations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented plan-based no-overrides compile/signature path: phase11 hot run now calls `_compile_phase12_no_overrides_executor_from_plan(plan_no_overrides)`, with plan-signature helpers and a new compiler entrypoint that compiles directly from plan steps/transient schema without building no-overrides IR dict rows.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1785-1874, src/melder/spellbook/spell_crafter/spell_crafter.py:2089-2135, src/melder/spellbook/spell_crafter/spell_crafter.py:3925-3929, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:151-233, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5435-5546, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5689-5834
  IMPACT: Removes one hot payload-construction path from `run_phase_execution_plan` while preserving payload-based compile path for lazy `codegen_ir` readers.
  NEXT: Run targeted unit slice and component harness, then capture warm delta.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Warm profile after lazy-capture closure still spends most phase11 time in one full plan build (`_build_execution_plan_variant` + `ExecutionPlanBuilder.build`) plus no-overrides payload export (`_build_phase11_variant_ir_payload`) invoked from `run_phase_execution_plan`.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:14-20, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_lazy_capture_output.txt:28-28, src/melder/spellbook/spell_crafter/spell_crafter.py:3748-3790, src/melder/spellbook/spell_crafter/spell_crafter.py:1725-1790
  IMPACT: Phase11 still has a concrete warm-path optimization slice despite prior variant-reuse and lazy-capture wins.
  NEXT: Replace run-phase payload-based compile-signature path with plan-based compile-signature path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Mutation override route config is only materialized when `spell.has_mutation_override` is true, so a no-overrides compile-path optimization can stay mutation-safe as long as exported IR path behavior remains unchanged.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:195-213, src/melder/spellbook/spell.py:1407-1450
  IMPACT: Confirms this task can focus on no-overrides compile hot path without collapsing mutation variant contracts.
  NEXT: Keep mutation variant generation behavior intact while optimizing no-overrides compile path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task opened from the phase-testing backlog after lazy-capture closure. Plan-based
compile wiring is implemented and the fixture contract drift is fixed by adding
`root_instance_key` to plan stubs used by the new tests. Latest targeted unit
and harness reruns are both passing with refreshed artifacts. Next step is to
route this task status in story/attention-board docs and request acceptance for
closure/move to completed.
