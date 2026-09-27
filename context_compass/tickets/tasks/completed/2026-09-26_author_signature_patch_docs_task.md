# Task: Author the patch docs for the signature-determinism and phase-8 digest tranche

- Completed: 2026-09-26T13:14:31Z
- Summary: Architecture and component patch docs for tranche T1 written first (patch gate), amended twice to
  the implemented shape, consumed by tasks 2-5 and promoted into the canonical maps at story closure;
  patch folder archived under system_docs/patches/completed/.

## Metadata
- Task ID: TASK-2026-09-26-author-signature-patch-docs
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T13:14:31Z

## Objective
Satisfy the patch-framework entry gate for tranche T1: an `architecture_patch.md` and a
`component_patch_spell_compiler.md` under `system_docs/patches/active/codegen_signature_determinism_2026_09_26/`
that state the boundary delta (one leaf signature module), the byte-compatibility invariant, the freeze
canonicalization rule, the phase-8 digest change, migration order, rollback and validation; then the
consumption mapping note (patch section -> implementation step -> validation step) required before code.

## Ticket Contract
- ENTRY_GATE: Story opened on the owner's T1 approval; active board row routes here.
- EXECUTION_BOUNDARY: the patch folder above and this ticket/story; read-only over `src/` and `tests/`.
- DEPENDENCIES: candidates.md (C-A, C-H); driver.md hashing hazards; the source reads recorded in the
  notes below; `agent_onboarding/default/engineer/skills/patch_framework_gating.md` and
  `patch_artifact_consumption.md`.
- EXIT_GATE: both patch docs exist, are linked from the story, and the consumption mapping note is
  recorded here; status review; the next task's Propose -> Confirm message can cite them.
- FAILURE_ESCALATION: DECISION_REQUEST if the canonicalization rule needs an owner choice beyond the
  default recorded in the component patch; BLOCKER if a signature input cannot be made deterministic.

## Scope Boundaries
- In scope: the two patch docs; a `code_description_patch` is NOT required (no complex control flow,
  no new gate pipeline, no rollback semantics beyond "revert the module").
- Out of scope: any edit under `src/` or `tests/`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened and routed by fable_0 on the owner's T1 approval (2026-09-26).
- from_state: in_progress
- to_state: review
- transition_reason: Both patch docs written and linked; consumption mapping recorded (2026-09-26); exit
  gate met; owner review alongside the task 2 proposal.
- from_state: review
- to_state: done
- transition_reason: Owner accepted tasks 1-5 and the story after the third owner-run green suite report
  ("yeah sure looks good", 2026-09-26T13:14:31Z); canonical docs promoted, patch folder archived, boards synced.

## Steps / Checklist
- [x] P1: record the source facts the docs rest on (serializer, freeze, call-site argument types, the
      payload origin, the phase-8 key path) in `## Notes`.
- [x] P2: write `architecture_patch.md` (boundary delta, invariants, migration order, rollback,
      validation, ticket map).
- [x] P3: write `component_patch_spell_compiler.md` (before/after for the three helpers and the phase-8
      key path; canonicalization rule; failure-mode deltas; ordering constraints).
- [x] P4: consumption mapping note (patch section -> implementation step -> validation step); link the
      docs from the story; task -> review.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- system_docs/patches/active/codegen_signature_determinism_2026_09_26/architecture_patch.md
- system_docs/patches/active/codegen_signature_determinism_2026_09_26/component_patch_spell_compiler.md

## Files / Paths Impacted
- The patch folder, this ticket and the story only.

## Validation
- Not run.
- Recommended commands:
  - none (documentation task).

## Risks / Rollback Notes
- The docs must not restate a rule the code contradicts: every before/after line cites the range read.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [ ] No patch claim from a docstring or a grep hit; each before-line cites the code.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure (merge into `src_components.md`, archive the folder).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: signature path; freeze canonicalization; phase-8 key path.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T09:05:00Z
  TYPE: FACT
  CLAIM: Source facts for the docs (read this session). (1) `SharedCompilerExecutions` and
    `CodegenCreationSchemaHelpers` carry byte-identical copies of `serialize_codegen_signature_part`
    (typed one-byte tags N/B1/B0/I/F/S/Y; containers and other objects via `pickle.dumps(protocol=5)`
    with a `repr` fallback), `hash_codegen_signature` (sha256 over parts joined by `|`) and
    `freeze_phase11_schema_value` (primitives pass; dicts -> sorted (key, frozen) tuples; lists/tuples
    -> tuples; sets -> repr-sorted tuples; anything else -> `repr(value)`); four consumers import the
    helpers class under the alias `SharedCompilerExecutions`; the phase-11 class docstring states it
    must not reach back into the phase helper surface (dependency direction). (2) `pickle.dumps` of a
    raw `set`/`frozenset` of strings is iteration-ordered (hash-seed dependent); no call site read
    passes a raw set today: parts are ids, tuples of frozen rows, sorted names, enum members and
    signature strings (phase 8; generalized manifest; the three generalized steps; the phase-11 variant
    payload; the phase 8-11 digest). (3) The `repr` fallback is reached by user-supplied SpellContract
    override payloads: `injection_spec.contract_payload` originates from
    `contract_shape.contract_overrides_by_*` in the injection processor strategy and its values are
    frozen into step rows and the no-overrides signature row, so an object with a default `repr`
    yields a process-local executor signature today. (4) Phase 8 builds `_build_root_blueprint_rows`
    twice and hashes the pool-wide rows per root; the None clause of the skip check is last; the two
    key slots have no reader outside the strategy (resets only); `id(path_registry)` is a deliberate
    process-local part of the key.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:58-137
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:397-424
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1311-1355
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1387-1416
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:1-158
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:357-500
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:197-250
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:508-535
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py:110-138
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_overrides_codegen_creation_step.py:112-140
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1195-1265
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2713-2747
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:190-230
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:303-348
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:118-372
  IMPACT: The set hazard is a guard for the future, not a live defect; the `repr` hazard is live for
    object-valued contract payloads; the duplication is real and byte-identical today, so a single
    implementation can be byte-compatible for every currently deterministic input.
  NEXT: P2: write architecture_patch.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T09:08:00Z
  TYPE: FACT
  CLAIM: P2-P4 done. Consumption mapping (patch section -> implementation step -> validation step):
    architecture Interface delta 1 (leaf module, both facades delegate) -> task 2 U2 -> unit delegation
    tests + corpus test; Interface delta 2 (canonical freeze: class/function/enum strings, marker tuple
    for other objects; sets frozen before pickling) -> task 2 U2 -> freeze unit cases + two-process
    determinism test; Invariant 1 (byte-compatibility, no generation bump) -> task 2 U3 corpus fixture
    captured BEFORE the edit -> corpus test; Interface delta 3 (phase-8 pool digest, None-first, root
    rows once) -> task 3 H2 -> digest/None-first/equality unit tests + breakdown harness before/after;
    Migration order 1-5 -> tasks 2 then 3 then promotion; Rollback -> git restore of pure functions.
    Task 1 exit gate met; docs linked from the story.
  EVIDENCE:
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/architecture_patch.md
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/component_patch_spell_compiler.md
  - tickets/stories/2026-09-26_signature_determinism_and_phase8_digest_story.md
  IMPACT: The patch-framework entry gate is satisfied for tasks 2 and 3; code edits still wait on the
    owner's confirmation of each Propose -> Confirm message.
  NEXT: Task 2 U1: Propose -> Confirm (files, symbols, freeze rule, set rule).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T09:05:00Z: in progress; P1 recorded. Resume at P2 (architecture_patch.md), then P3, P4.
STATE 2026-09-26T09:08:00Z: task 1 in REVIEW (patch docs complete). Task 2 waits on the owner's U1 confirmation.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
