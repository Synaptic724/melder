# Task: fix spellcrafter blueprint and error contract cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-19-fix-spellcrafter-blueprint-and-error-contract-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-19T15:20:00Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current bounded mypy cluster spanning spellbook validation errors,
blueprint patch/injection/execution plans, graph mutation, mutation-conduit
interface typing, spell requirements finder, and the Phase 12 no-overrides
executor while keeping public contracts truthful and avoiding unrelated
SpellCrafter redesign.

## Ticket Contract
- ENTRY_GATE: the user supplied this exact bounded follow-up cluster.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`
  - `src/melder/aether/spellbook/spell_crafter/blueprints/patch_maps.py`
  - `src/melder/aether/spellbook/spell_crafter/blueprints/injection_plan.py`
  - `src/melder/aether/spellbook/spell_crafter/blueprints/execution_plan.py`
  - `src/melder/aether/conduit/meld/overrides/graph_mutator.py`
  - `src/melder/utilities/interfaces/imutationconduit.py`
  - `src/melder/aether/spellbook/spell_crafter/spell_requirements_finder/spell_requirements_finder.py`
  - `src/melder/aether/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
  - directly implicated support interfaces only if the source proves they are stale
- DEPENDENCIES:
  - current RootResolutionBlueprint and DagIndex targeting contracts
  - current spell-parameter requirement public interface
  - no shims, no fake surfaces, no unrelated blueprint/runtime redesign
  - raise to Mark directly if the contract becomes ambiguous
- EXIT_GATE:
  - the targeted reported errors in these files are gone
  - any public interface changes remain truthful and bounded
  - focused validation confirms the lane
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the lane requires a broader
  blueprint/runtime API redesign instead of local typing cleanup

## Scope Boundaries
- In scope:
  - local optionality, generic, and return typing cleanup
  - truthful public interface updates where the source proves stale contract drift
  - local no-untyped-def cleanup in graph mutation / mutation conduit surfaces
- Out of scope:
  - unrelated repo-wide mypy debt
  - broad SpellCrafter pipeline redesign

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user selected this exact blueprint/error-contract
  cluster as the next active lane.

## Steps / Checklist
- [x] read the exact failing slices in the reported files
- [x] classify local typing debt versus stale public contract drift
- [x] patch the bounded file/interface fixes
- [x] rerun focused mypy on the reported files
- [x] rerun directly implicated unit tests when behavior-sensitive files move
- [x] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- a bounded SpellCrafter blueprint / error-contract typing fix

## Files / Paths Impacted
- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`
- `src/melder/aether/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/aether/spellbook/spell_crafter/blueprints/injection_plan.py`
- `src/melder/aether/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/aether/conduit/meld/overrides/graph_mutator.py`
- `src/melder/utilities/interfaces/imutationconduit.py`
- `src/melder/aether/spellbook/spell_crafter/spell_requirements_finder/spell_requirements_finder.py`
- `src/melder/aether/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- only if required by the truthful fix:
  - directly implicated support interfaces

## Validation
- `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\utilities\custom_exceptions\spellbook_validation_error.py src\melder\aether\spellbook\spell_crafter\blueprints\patch_maps.py src\melder\aether\spellbook\spell_crafter\blueprints\injection_plan.py src\melder\aether\spellbook\spell_crafter\blueprints\execution_plan.py src\melder\aether\conduit\meld\overrides\graph_mutator.py src\melder\utilities\interfaces\imutationconduit.py src\melder\aether\spellbook\spell_crafter\spell_requirements_finder\spell_requirements_finder.py src\melder\aether\spellbook\spell_crafter\blueprints\phase12_no_overrides_executor.py src\melder\utilities\interfaces\ispellparameterrequirement.py 2>&1 | Select-String 'src\\melder\\utilities\\custom_exceptions\\spellbook_validation_error.py:|src\\melder\\aether\\spellbook\\spell_crafter\\blueprints\\patch_maps.py:|src\\melder\\aether\\spellbook\\spell_crafter\\blueprints\\injection_plan.py:|src\\melder\\aether\\spellbook\\spell_crafter\\blueprints\\execution_plan.py:|src\\melder\\aether\\conduit\\meld\\overrides\\graph_mutator.py:|src\\melder\\utilities\\interfaces\\imutationconduit.py:|src\\melder\\aether\\spellbook\\spell_crafter\\spell_requirements_finder\\spell_requirements_finder.py:|src\\melder\\aether\\spellbook\\spell_crafter\\blueprints\\phase12_no_overrides_executor.py:|src\\melder\\utilities\\interfaces\\ispellparameterrequirement.py:'`
  - no matching file-local mypy errors
- `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\custom_exceptions\test_spellbook_validation_error.py tests\unit\melder\spellbook\spell_crafter\blueprints\test_injection_plan_core.py tests\unit\melder\spellbook\spell_crafter\blueprints\test_execution_plan_core.py tests\unit\melder\spellbook\spell_crafter\blueprints\test_patch_maps_core.py tests\unit\melder\spellbook\spell_crafter\blueprints\test_phase12_no_overrides_executor.py tests\unit\melder\spellbook\test_conjure_hotspot_fixes.py tests\component\melder\spellbook\spell_crafter\spell_requirements_finder\test_spellbook_component_spell_requirements_finder.py`
  - `67 passed, 1 warning`

## Risks / Rollback Notes
- Medium risk. Most of this looks like local typing debt, but the execution
  plan and parameter-requirement interface surfaces may expose one real public
  contract drift.

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
- DATETIME: 2026-05-19T15:20:00Z
  TYPE: FACT
  CLAIM: The next active lane is the bounded SpellCrafter blueprint and
    error-contract typing cluster. The first step is exact slice reads because
    the report mixes local optionality/generic issues, two likely stale public
    interface surfaces, and one custom-exception typing bucket.
  EVIDENCE:
  - user_error_report: `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`
  - user_error_report: `src/melder/aether/spellbook/spell_crafter/blueprints/patch_maps.py`
  - user_error_report: `src/melder/aether/spellbook/spell_crafter/blueprints/injection_plan.py`
  - user_error_report: `src/melder/aether/spellbook/spell_crafter/blueprints/execution_plan.py`
  - user_error_report: `src/melder/aether/conduit/meld/overrides/graph_mutator.py`
  - user_error_report: `src/melder/utilities/interfaces/imutationconduit.py`
  - user_error_report: `src/melder/aether/spellbook/spell_crafter/spell_requirements_finder/spell_requirements_finder.py`
  - user_error_report: `src/melder/aether/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
  IMPACT: This should stay bounded if the source confirms mostly local typing
    debt instead of wider blueprint/runtime contract redesign.
  NEXT: read the exact failing slices in the reported files and classify local
    residue versus real contract drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T15:22:56Z
  TYPE: FACT
  CLAIM: The live error set is narrower than the pasted report. The current
    bucket is mostly local typing debt: optional `socket_refs` / patch lists in
    `patch_maps.py`, optional instance-key lists in `injection_plan.py`,
    optional `DagNode` results in `graph_mutator.py`, one `SpellIndex.current`
    nullability site in `spell_requirements_finder.py`, one mixed transient
    schema local in `phase12_no_overrides_executor.py`, and local union
    handling in `spellbook_validation_error.py`. Two seams may require truthful
    public contract updates if the source confirms them: `ISpellParameterRequirement`
    is missing keyword/vararg shape properties used by `execution_plan.py`, and
    `IRootResolutionBlueprint` may be too narrow for the patch-map helpers if
    those functions genuinely operate on the public blueprint surface.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:88-229
  - src/melder/aether/spellbook/spell_crafter/blueprints/patch_maps.py:450-499
  - src/melder/aether/spellbook/spell_crafter/blueprints/patch_maps.py:700-799
  - src/melder/aether/spellbook/spell_crafter/blueprints/patch_maps.py:1045-1082
  - src/melder/aether/spellbook/spell_crafter/blueprints/injection_plan.py:289-316
  - src/melder/aether/spellbook/spell_crafter/blueprints/injection_plan.py:618-639
  - src/melder/aether/spellbook/spell_crafter/blueprints/execution_plan.py:1458-1469
  - src/melder/aether/conduit/meld/overrides/graph_mutator.py:135-160
  - src/melder/utilities/interfaces/imutationconduit.py:1-30
  - src/melder/aether/spellbook/spell_crafter/spell_requirements_finder/spell_requirements_finder.py:216-234
  - src/melder/aether/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:420-456
  - src/melder/utilities/interfaces/ispellparameterrequirement.py:1-41
  IMPACT: This still looks like one bounded pass, but I need to verify the two
    possible interface seams before patching.
  NEXT: read the concrete `SpellParameterRequirement`, `IRootResolutionBlueprint`,
    `SpellIndex`, and the local surrounding code for the remaining live sites,
    then patch only the truthful local or interface fixes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T15:28:00Z
  TYPE: FACT
  CLAIM: The first mypy rerun collapsed the lane again. The interface work was
    sufficient; the only live residue is one local `occurrence` name collision
    in `injection_plan.py` and three local Phase 6 formatting locals in
    `spellbook_validation_error.py`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/blueprints/injection_plan.py:637-646
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:203-229
  IMPACT: No broader redesign or new interface widening is needed.
  NEXT: rename the colliding locals, rerun the same focused mypy slice, then
    run the directly implicated unit tests if it comes back clean.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T15:29:24Z
  TYPE: MEASURE
  CLAIM: The blueprint/error-contract lane is green in the bounded checks. The
    only truthful public-contract changes were importing `IConduit` into
    `IMutationConduit` and adding the existing keyword/vararg parameter-shape
    booleans to `ISpellParameterRequirement`; the rest of the bucket collapsed
    through local optionality/generic cleanup in the validation-error, patch
    map, injection plan, execution plan, graph mutator, spell requirements
    finder, and Phase 12 no-overrides executor paths.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:1-246
  - src/melder\aether\spellbook\spell_crafter\blueprints\patch_maps.py:433-1182
  - src/melder\aether\spellbook\spell_crafter\blueprints\injection_plan.py:252-677
  - src/melder\aether\spellbook\spell_crafter\blueprints\execution_plan.py:1458-1469
  - src/melder\aether\conduit\meld\overrides\graph_mutator.py:103-160
  - src/melder\utilities\interfaces\imutationconduit.py:1-30
  - src/melder\utilities\interfaces\ispellparameterrequirement.py:1-53
  - src/melder\aether\spellbook\spell_crafter\spell_requirements_finder\spell_requirements_finder.py:216-234
  - src/melder\aether\spellbook\spell_crafter\blueprints\phase12_no_overrides_executor.py:401-456
  IMPACT: The reported SpellCrafter blueprint and error-contract cluster is
    removed without widening into a broader pipeline redesign.
  NEXT: report the bounded fix and wait for the next exact bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active bounded SpellCrafter blueprint and error-contract typing lane.
