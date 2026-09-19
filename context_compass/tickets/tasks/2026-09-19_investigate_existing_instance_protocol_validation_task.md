# Task: Investigate Protocol admission for existing unique objects through bind and compiler

## Metadata
- Task ID: TASK-2026-09-19-investigate-existing-instance-protocol-validation
- Story: STORY-2026-09-19-existing-instance-protocol-admission
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T10:52:47Z
- Updated: 2026-09-19T11:15:11Z

## Objective
Establish why an incompatible existing instance can bind under an explicitly declared Protocol,
which compiler/runtime stages trust that admission, and the smallest coherent repair boundary.
Preserve the current unique-only existing-object model and exact-reference injection.

## Ticket Contract
- ENTRY_GATE: owner explicitly requests Protocol investigation; the attention board routes here.
- EXECUTION_BOUNDARY: source/document reads, native regressions, clearly labeled diagnostic probes
  and a repair proposal. No production source changes in this investigation.
- DEPENDENCIES: retained Protocol regressions, accepted existing-instance planner repair, current
  Bind/profile/validation/lookup source, and the owner's unique-instance baseline correction.
- EXIT_GATE: native failure reproduced, bind-to-compiler trust boundaries evidenced, repair hypothesis
  qualified against controls, remaining choices and exact affected files stated for review.
- FAILURE_ESCALATION: separate direct admission parity from broader Protocol features; characterize
  shared class/instance limitations without treating a larger type-checker redesign as authorized.

## Scope Boundaries
- In scope: supplied non-callable instances, declared Protocol spellframes, class controls, unique
  admission, required/explicit/collection/contract dependency selection as relevant, compiler validation,
  actual instance members versus class members, pre/post-conjure and staged bind entrypoints.
- Out of scope: external-registration APIs, expanded lifetimes, object-state reconstruction, disposal
  changes, provider-artifact repair and automatic discovery of all Protocols an object could satisfy.
- Existing class/factory/concrete-frame/string-frame behavior is a control, not an invitation to change it.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: bind/compiler trace, native reproductions and admission-only qualification establish a repair boundary.

## Steps / Checklist
- [x] Trace profile selection and bind admission, including existing helper limits and entrypoint coverage.
- [x] Trace Phase-1 requirements, Phase-3 provider selection and Phase-4/system validation assumptions.
- [x] Reproduce the retained native Protocol regressions without production changes.
- [x] Probe unresolved boundaries, distinguishing current observations from diagnostic repair simulation.
- [x] Produce the bind/compiler impact map and bounded repair recommendation with qualification limits.
- [x] Synchronize findings, artifact links and the story checkpoint for review.

## Required Rereads
1. This task's latest Notes and findings artifact.
2. Parent story Owner Intent/Current Checkpoint and the prior Stage-1 task's Current Owner Correction.
3. Verified src_components slices: Binding Pipeline; DI Descriptors and Contract Sockets;
   SpellCompiler and Validation Pipeline; Meld Resolution Runtime only where the traced edge requires it.
4. Current implementations below. Use the graph index when wiring details are needed; source governs behavior.

## Initial Source And Test Targets
- src/melder/aether/spellbook/bind/bind.py
- src/melder/aether/spellbook/spellbook.py: bind and bind_inactive
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py
- src/melder/aether/spellbook/spell_compiler/validation/validation_system.py
- src/melder/aether/spellbook/spell_compiler/validation/strategies/existing_creation_compatibility_strategy.py
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py
- Phase-3 lookup and downstream compiler nodes selected from the verified component/graph map.
- tests/component/melder/spellbook/test_existing_instance_protocol_admission.py
- tests/unit/melder/spellbook/bind/test_bind.py
- tests/integration/melder/spellbook/test_existing_instance_planning.py

## Deliverables
- artifacts/existing_instance_protocol_20260919/findings.md
- Exact commands, native logs/XML and any isolated diagnostic tests under the same directory.
- Concrete proposed runtime/test/doc boundaries; no claim that a simulated correction is shipped.

## Validation
Fresh native baseline: 4 failed, 14 passed on Python 3.14.7 free-threading. The four failures are the
same missing/non-callable instance-member admission cases. Local source import asserted; no production edits.
Additional baseline: 2 failed/20 passed; staged additions: 2 failed/1 passed. Admission-only process-local
simulation: 39 passed/4 stock observations deselected, including four deliberately preserved checker-limit
characterizations. Ruff F passes; three production source hashes unchanged. Full suite not run.

## Risks / Rollback Notes
- Validating type(instance) can miss shadowed invalid members or reject members supplied on the instance.
- Existing helper checks only a limited declared-member contract; distinguish its intentional limits
  from the instance-family gate that skips it altogether.
- Compiler selection might trust declared frames; follow the actual call path before claiming bind-only scope.
- Diagnostic monkeypatches, if used, must be explicit and isolated from stock baseline and acceptance claims.

## Applicable Anti-Patterns
- [ ] No broader registration or lifetime redesign inferred from this bug.
- [ ] No constructor discovery or invocation added for already-created providers.
- [ ] No compiler modification presumed merely because the invalid object is later injected.
- [ ] No passing characterization or simulation reported as production repair.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/existing_instance_protocol_20260919/findings.md
  - artifacts/existing_instance_protocol_20260919/source_preflight.log
  - artifacts/existing_instance_protocol_20260919/native_baseline.log
  - artifacts/existing_instance_protocol_20260919/native_baseline.xml
  - artifacts/existing_instance_protocol_20260919/test_protocol_paths.py
  - artifacts/existing_instance_protocol_20260919/path_baseline.log
  - artifacts/existing_instance_protocol_20260919/path_baseline.xml
  - artifacts/existing_instance_protocol_20260919/staged_baseline.log
  - artifacts/existing_instance_protocol_20260919/staged_baseline.xml
  - artifacts/existing_instance_protocol_20260919/admission_probe.py
  - artifacts/existing_instance_protocol_20260919/admission_probe.log
  - artifacts/existing_instance_protocol_20260919/admission_probe.xml
  - artifacts/existing_instance_protocol_20260919/source_hashes_before.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain the source/probe evidence for the eventual approved repair.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record the exact next source question in task Notes before proceeding.

## Noting Behavior
Record each completed bind/compiler trace or test result here before another tranche. The story owns
program direction; this task owns the concrete Protocol findings and one immediate next action.

## Notes
- DATETIME: 2026-09-19T10:52:47Z
  TYPE: PLAN
  CLAIM: Owner requests investigation of the Protocol problem and its bind/compiler integration.
    This task isolates that question within the current unique-instance model, preserving earlier
    red regressions and the owner's rejection of an assumed external-registration redesign.
  EVIDENCE:
  - Owner's current request to investigate bind and possible compiler integration.
  - tickets/tasks/completed/2026-09-17_existing_object_bind_representation_design_task.md
  IMPACT: Source trace and diagnostic verification are authorized; production repair remains a later step.
  NEXT: Trace bind admission and the compiler's declared-frame selection/validation path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:00:14Z
  TYPE: FACT
  CLAIM: Phase 3 selects providers by declared frame/name/identity, including both indexed and scan
    paths, then records normal dependency edges. Phase-4 existing-creation validation checks presence,
    unique lifetime, profile and constructor opacity, not Protocol members. Bind's member helper is
    called only for classes and has direct-public-member semantics rather than complete Protocol typing.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:464-490
  - src/melder/aether/spellbook/bind/bind.py:868-912
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-637
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:748-987
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/existing_creation_compatibility_strategy.py:79-163
  IMPACT: The invalid declaration can pass into graph selection. Admission is the initial repair
    candidate; prove it through real compiler/injection paths before deciding that production compiler edits are needed.
  NEXT: Reproduce the existing eighteen Protocol admission cases against the current source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:05:08Z
  TYPE: MEASURE
  CLAIM: Fresh eighteen-case native baseline reproduces four missing TypeError failures for supplied
    instances with missing/non-callable Protocol members, before and after conjure. Fourteen controls pass.
  EVIDENCE:
  - artifacts/existing_instance_protocol_20260919/source_preflight.log
  - artifacts/existing_instance_protocol_20260919/native_baseline.log
  - artifacts/existing_instance_protocol_20260919/native_baseline.xml
  IMPACT: The admission gap is current. Next qualify downstream compiler/injection paths and actual
    instance-versus-class member behavior using isolated diagnostics, not a production patch.
  NEXT: Add native path/instance-member probes and an explicitly labeled process-local admission simulation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:11:26Z
  TYPE: MEASURE
  CLAIM: Four stock path probes inject the same bad reference through annotation, collection,
    SpellMap and linked SpellContract, failing only at actual read() use. Twelve valid path controls
    pass, including instance-only members. Two shadowed-method rejection regressions fail; four
    shared helper-limit characterizations pass. Path baseline: 2 failed, 20 passed.
  EVIDENCE:
  - artifacts/existing_instance_protocol_20260919/test_protocol_paths.py
  - artifacts/existing_instance_protocol_20260919/path_baseline.log
  - artifacts/existing_instance_protocol_20260919/path_baseline.xml
  IMPACT: Compiler participation is real, but the bad provider is already admitted. Qualify actual
    instance-member admission; do not replace it with checking type(instance) or full Protocol typing.
  NEXT: Qualify staged bind and the isolated admission-only simulation against native controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:12:13Z
  TYPE: MEASURE
  CLAIM: Staged admission repeats the same defect before/after conjure: two expected rejection tests
    fail. A valid instance-only member passes staging, public selection and exact-reference meld.
  EVIDENCE:
  - artifacts/existing_instance_protocol_20260919/staged_baseline.log
  - artifacts/existing_instance_protocol_20260919/staged_baseline.xml
  IMPACT: The common Bind admission seam must cover active and inactive registration. No reason to
    add a second compiler registration mechanism follows from these results.
  NEXT: Run the original regressions and new controls with only the process-local admission probe enabled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:15:10Z
  TYPE: MEASURE
  CLAIM: The explicitly enabled process-local admission simulation passes all 39 selected original
    and additional cases; four stock bad-admission observations were deselected. Compiler execution
    remains unchanged. Four selected cases deliberately preserve shared helper limitations.
  EVIDENCE:
  - artifacts/existing_instance_protocol_20260919/admission_probe.py
  - artifacts/existing_instance_protocol_20260919/admission_probe.log
  - artifacts/existing_instance_protocol_20260919/admission_probe.xml
  IMPACT: Strong evidence for actual-instance admission at the shared Bind boundary. This is not a
    shipped patch or full Protocol validation; production placement and custom-profile coverage remain explicit limits.
  NEXT: Verify entrypoint convergence and source integrity, then write the exact bounded repair recommendation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:15:11Z
  TYPE: PLAN
  CLAIM: Investigation supports extending the existing Bind Protocol branch to actual instance/other
    profiles and generalizing the helper's candidate contract. Compiler provider selection remains
    frame/key based; no compiler edit is indicated by the traced paths and diagnostic controls.
  EVIDENCE:
  - artifacts/existing_instance_protocol_20260919/findings.md
  - artifacts/existing_instance_protocol_20260919/admission_probe.xml
  - src/melder/aether/spellbook/spellbinder.py:826-870
  - tests/unit/melder/spellbook/bind/test_bind.py:1091-1102
  IMPACT: Keep the initial repair to admission parity. Inherited Protocol/data-field coverage is a
    separate shared-helper contract decision. Source hashes remain unchanged; this is a proposal, not a repair.
  NEXT: Owner reviews the bounded Bind repair and whether broader Protocol member coverage should be separate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Investigation ready for review. Read findings.md: missing instance admission check -> declared-frame
compiler selection -> same bad reference injected -> failure on read(). Original baseline 4 red/14 controls;
actual-instance/staging additions reproduce further cases. A local admission-only simulation passes 39
selected cases with compiler unchanged. Recommend Bind branch/helper repair, preserving unique-only semantics.
Shared helper limits for inherited Protocol members/data annotations remain a separate decision.
No production changes; preserve the diagnostic-vs-acceptance distinction and original regression evidence.
