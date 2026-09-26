# Task: Unify the codegen signature serializer into one leaf implementation with a determinism test

## Metadata
- Task ID: TASK-2026-09-26-unify-codegen-signature-serializer
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: ready
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T09:05:00Z

## Objective
One implementation of `serialize_codegen_signature_part`, `hash_codegen_signature` and
`freeze_phase11_schema_value` in a new leaf module, with `SharedCompilerExecutions` and
`CodegenCreationSchemaHelpers` delegating to it; canonical freezing of classes, functions and enum members
and an explicit marker for other non-primitive objects; canonical handling of raw sets; a two-process
determinism test plus a byte-compatibility corpus test on the gauntlet book (C-H, the epic's I-0).

## Ticket Contract
- ENTRY_GATE: Patch docs exist and are linked (task 1 in review); the owner confirmed the Propose ->
  Confirm message naming the exact files and symbols; active board row routes here.
- EXECUTION_BOUNDARY: new `src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py`
  (leaf; imports nothing from `melder.aether`), `phases/shared_compiler_executions.py` (the three
  helpers delegate; nothing else), `codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py`
  (the three helpers delegate; nothing else), tests under `tests/unit/melder/spellbook/spell_crafter/`
  and `tests/component/melder/spellbook/`. No other file.
- DEPENDENCIES: task 1 patch docs; melder_0's hunks on `shared_compiler_executions.py` landed (verify
  with `git diff -w` before the edit); the freeze rule decided in the component patch.
- EXIT_GATE: single implementation; both facades delegate; unit tests for tags, canonical freeze,
  set handling and delegation; determinism test and corpus test written; "Not run." until the owner
  reports; status review.
- FAILURE_ESCALATION: RISK if the corpus test shows any previously deterministic signature changing
  bytes (then a generation bump is needed and must be coordinated with melder_0's generation 11);
  CONFLICT on concurrent edits.

## Scope Boundaries
- In scope: the three helpers, their facades, the leaf module, tests.
- Out of scope: step-row builders, transient schema, manifests, emitters, `caching_system.py`.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Created with the story; moves to in_progress after task 1 is in review and the
  owner confirms the file/symbol proposal.

## Steps / Checklist
- [ ] U1: Propose -> Confirm (files/symbols, the freeze rule, the set rule) and owner confirmation.
- [ ] U2: create the leaf module (docstrings per `docstrings.md`; no module-level constants; typing per
      `typing.md`); make both facades delegate; keep public names and signatures.
- [ ] U3: tests - unit (tags, freeze cases, set handling, delegation identity) and component (two
      subprocesses with different `PYTHONHASHSEED` on the gauntlet book; corpus byte-compatibility
      against signatures captured before the change).
- [ ] U4: docstring ritual on touched code; notes; task -> review with "Not run." and the exact
      commands for the owner.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The leaf module; two facades delegating; tests; a corpus fixture under
  `artifacts/codegen_signature_determinism_20260926/` (captured signatures before the change).

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py (new)
- src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py
- tests (new files under the two directories named above)

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/spellbook/spell_crafter tests/component/melder/spellbook`
  - `python benchmarks/testing_other_di/profile_bind_conjure_cycle.py` (cache hit rate across processes)

## Risks / Rollback Notes
- Rollback: delete the leaf module and restore the two facade bodies (pure functions; no state).
- The `shared_assets/` package under `spell_compiler/` may not exist yet: creating it needs an empty
  `__init__.py` only if package discovery requires it (`__init__.py` policy).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No edit under `src/` before the owner confirms the file/symbol proposal.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/
  - artifacts/codegen_signature_determinism_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: serializer; freeze; determinism test; byte-compatibility corpus.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T09:05:00Z
  TYPE: PLAN
  CLAIM: Sequence U1-U4; the corpus fixture is captured BEFORE any edit so byte-compatibility is proved
    against the shipped behaviour, not against the new code's own output.
  EVIDENCE:
  - tickets/tasks/2026-09-26_author_signature_patch_docs_task.md
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:58-137
  IMPACT: Prevents a silent stale-cache hit on the full-hit path, where no fresh signature is computed.
  NEXT: Wait for task 1 review and the owner's confirmation of U1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T09:05:00Z: ready; opens after task 1 (patch docs) is in review and U1 is confirmed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
