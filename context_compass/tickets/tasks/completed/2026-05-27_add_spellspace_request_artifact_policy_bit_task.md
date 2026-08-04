# Task: Add Spellspace Request Artifact Policy Bit

## Metadata
- Task ID: TASK-2026-05-27-add-spellspace-request-artifact-policy-bit
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p0
- Created: 2026-05-27T23:06:55Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Add one artifact-level policy bit that records whether a spell's reachable
graph requires a spellspace-origin request, without changing meld creation
behavior or adding runtime gating yet.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved a narrow start focused on the
  artifact bit only and explicitly rejected a second heavy graph walk.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - directly implicated focused tests only
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-27_spellspace_sharded_runtime_ownership_epic.md`
  - `tickets/tasks/2026-05-27_investigate_spellspace_owned_creations_and_meld_lane_task.md`
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
- EXIT_GATE:
  - one artifact field exists for the spellspace-request policy bit
  - the bit is computed from existing Phase 5 graph/index work without a new
    recursive graph walk
  - focused unit validation passes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the narrow artifact-only cut
  cannot be done without widening into runtime gating or broader compiler
  redesign.

## Scope Boundaries
- In scope:
  - artifact field addition
  - Phase 5 computation/storage of the bit
  - focused tests
- Out of scope:
  - runtime gating in `Conduit.meld(...)` / `SpellSpace.meld(...)`
  - phase-12 executor changes
  - spellspace runtime ownership changes
  - board-wide or architecture-doc rewrites

## Steps / Checklist
- [ ] Add the active task row and note route.
- [ ] Add one artifact field for the policy bit and clear it in artifact reset paths.
- [ ] Compute and attach the bit during Phase 5 using existing graph/index work.
- [ ] Add focused Phase 5/artifact tests.
- [ ] Run focused validation and record results.

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py`

## Noting Behavior
- Note focus: artifact-only policy-bit storage, existing-graph reuse, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-27T23:06:55Z
  TYPE: DECISION
  CLAIM: The starting slice is intentionally narrow. We are not adding runtime
    gating yet. We are only adding one artifact policy bit and computing it
    from existing Phase 5 graph/index work so we avoid a second heavy graph walk.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:178-273
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:491-520
  IMPACT: The patch can stay inside artifact + Phase 5 + focused tests without
    drifting into runtime or executor churn.
  NEXT: route the board to this task, then patch the artifact field and the
    Phase 5 computation seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T23:06:55Z
  TYPE: FACT
  CLAIM: The narrow implementation seam is Phase 5 artifact attachment, not
    runtime and not Phase 12. The patch adds `_requires_spellspace_request_phase5`
    to `SpellCompilerArtifact`, clears it in Phase 5 artifact reset, and computes
    the bit once from the already-built `SpellSystemIndex` dependency graph during
    `_attach_phase5_artifacts_for_snapshot(...)`. No runtime gating was added.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py
  IMPACT: The feature starts as artifact-only metadata exactly where the user
    wanted it, without widening into `Conduit.meld(...)`, `SpellSpace.meld(...)`,
    or executor changes.
  NEXT: run the focused artifact and Phase 5 unit rings, then record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T23:06:55Z
  TYPE: MEASURE
  CLAIM: The artifact-only cut is landed and the focused validation ring is
    green. `SpellCompilerArtifact` now carries `_requires_spellspace_request_phase5`,
    Phase 5 computes it from the already-built `SpellSystemIndex` dependency graph,
    and the focused artifact + frame-wide/local Phase 5 unit files passed without
    widening into runtime gating.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5_local.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_compiler\test_spell_compiler_artifact.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5_local.py`
  IMPACT: We now have the policy bit at the artifact seam with no runtime or
    executor churn, and the next decision is whether to propagate/stamp/use it.
  NEXT: get review on this narrow cut, then decide whether the next slice is
    stamping the bit onto `Spell` or wiring the actual request-origin gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T23:06:55Z
  TYPE: FACT
  CLAIM: The first implementation draft was too heavy because it added a second
    explicit dependency walk in Phase 5. That was corrected. The landed code now
    reuses `SpellSystemRootBlueprintBuilder._reachable_by_id_for(snapshot)` and
    only performs a spellspace-set intersection while Phase 5 is already attaching
    artifacts to scoped spells.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:178-203
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py
  IMPACT: The policy bit no longer adds a second graph traversal pass. It now
    piggybacks on the existing reachability memo exactly where the user wanted
    the optimization pressure kept under control.
  NEXT: review this corrected artifact-only cut before widening into spell
    stamping or runtime request-origin gating.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the narrow first implementation slice for spellspace-request
policy: compute and store the artifact bit only, using existing Phase 5
graph/index work, with no runtime gating yet.

