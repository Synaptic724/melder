# Story: Deterministic codegen signatures and a pass-hoisted phase-8 pool digest (tranche T1)

## Metadata
- Story ID: STORY-2026-09-26-signature-determinism-phase8-digest
- Epic: EPIC-2026-08-03-comptime-ir-phase-pipeline
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T11:39:16Z

## User Narrative
As the Melder owner, I want the compiler's signature path to be one implementation that is deterministic
across processes, and phase 8 to stop hashing the whole pool per root, so that the creation cache keys
are trustworthy and the cold conjure path loses its only O(spells^2) step - without touching the hot path
or the phases 5-7 schedule.

## Value / MRP Alignment
Owner ruling 2026-09-26 on the improvement plan: candidates C-H and C-A are approved as the first
implementation tranche; C-B (fusing phases 5-7) is deferred because the system-wide check and the
single-spell dependency check must stay separately schedulable. C-H protects today's cache (the epic's
I-0) and is the acceptance test for every later signature-based skip, including the structural snapshot.
C-A removes counted waste in phase 8 with no semantic change. Both are small, compiler-side and
measurable with the existing breakdown harness.

## Ticket Contract
- ENTRY_GATE: Owner approved T1 = C-H + C-A (epic Decision Log 2026-09-26); patch docs exist under
  `system_docs/patches/active/codegen_signature_determinism_2026_09_26/` and are linked here before any
  edit under `src/`; the active board row routes to the current task.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py`
  (serializer, hash, freeze delegations only), `codegen_creation_system/shared_assets/
  codegen_creation_schema_helpers.py` (same three helpers), one new leaf module for the single
  implementation, `spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py` (`analyze`,
  `_build_occurrence_graph_fast_key`, `_build_occurrence_graph_input_signature`, one new pass-cache
  helper), tests under `tests/unit/melder/spellbook/spell_crafter/` and `tests/component/`, the patch
  docs, and the canonical maps at closure. NOT in scope: `phases/compiler_phase_5.py` .. `_7.py`, the
  scheduler, `conduit/meld/**`, `Creations`, `caching_system.py` (no generation bump: see the byte-
  compatibility constraint), the emitters and the door compiler.
  EXTENDED 2026-09-26 (owner option B, task 4): the creation-cache emission seam - two pure helpers on
  `CodegenCreationSchemaHelpers`, `manifest_creation_cache.build_package`,
  `spell_codegen_creation_cache.build_package`, and the `Spellbook._emit_spell_cache` call site (one
  hunk). Row format, manifest schema, hydration and `caching_system.py` stay out of scope.
  EXTENDED 2026-09-26 (owner ruling, task 5): the DI descriptors (`spell_contract.py`, `spell_map.py`), the
  phase-9 contract processor, the step data classes, the row builder and the no-overrides hydration sites
  of the three families; the override emitters and targeting runtime stay out (v2 S3).
- DEPENDENCIES: artifacts/ir_phase_improvement_20260926/candidates.md (C-A, C-H);
  artifacts/ir_phase_survey_20260925/driver.md (hashing hazards); melder_0's live lane on
  `shared_compiler_executions.py` (missing_dependency_sockets) - sequence edits after their hunks land.
- EXIT_GATE: single serializer/hash/freeze implementation with both facades delegating; determinism
  test (two interpreter processes, equal signatures) green owner-run; phase 8 computes the pool digest
  once per pass and the skip check tests the analysis slot first; existing compiler suites green
  owner-run; breakdown harness before/after recorded; patch docs promoted into `src_components.md`
  (IR seams block) with the index regenerated; owner accepts.
- FAILURE_ESCALATION: BLOCKER if a signature input is found that cannot be made cross-process
  deterministic without a persisted-format change; CONFLICT if a file is under concurrent edit by
  melder_0 or updater_1 at patch time; RISK for any change that alters the bytes of a signature that
  was already cross-process deterministic (that would require a cache generation bump).

## Requirements (Functional)
- One implementation of `serialize_codegen_signature_part`, `hash_codegen_signature` and
  `freeze_phase11_schema_value` in a leaf module imported by both `SharedCompilerExecutions` and
  `CodegenCreationSchemaHelpers`; both facades keep their public names.
- Freeze canonicalizes classes, functions and enum members to `module:qualname[:name]` and marks any
  other non-primitive object explicitly (no `repr` of addresses); the serializer refuses raw `set`/
  `frozenset` parts or sorts them canonically (decision recorded in the patch doc).
- Determinism test: the same book built in two interpreter processes yields byte-equal executor
  signatures (no-overrides and overrides lanes) and equal phase-8 input signatures modulo the
  documented process-local part (`id(path_registry)`).
- Phase 8: `analyze` checks `artifact._occurrence_graph_analysis is None` before any key work; the
  pool-wide rows are hashed once per pass into `analysis_pass_cache["phase8_pool_digest"]`; the root
  key and signature combine the root rows with that digest; `_build_root_blueprint_rows` runs once per
  root.

## Requirements (Non-Functional)
- Byte-compatibility constraint: every signature that was cross-process deterministic before this
  story keeps the same bytes (so no `.melc` generation bump and no cache reset); the test corpus proves
  it on the gauntlet book.
- No `getattr`/`hasattr` on owned objects; `Optional`/`Union`; type hints on every function; rich
  docstrings; no `print()`; tests are pytest, unit-first (`typing.md`, `banned_patterns.md`).
- Measurements are owner-run: "Not run." until reported.

## Scope Boundaries
- In scope: the three helper functions and their two facades, the phase-8 strategy's key/signature
  path, tests, patch docs, the component map's IR seams block at closure.
- Out of scope: phases 5-7 (C-B deferred by owner), chunking (C-J), the phase-3 DAG (C-C), the
  structural snapshot (C-G), emitters, hydration, the meld door.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved items 1 and 2 of the improvement plan (2026-09-26); opened by fable_0
  with the patch-doc task routed first per `patch_framework_gating.md`.

## Dependencies / Related Work
- tickets/stories/2026-09-26_phase_pipeline_improvement_plan_story.md (review; source of C-A, C-H)
- tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md (melder_0; touches
  `shared_compiler_executions.py`; cache generation 11 planned there)
- tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md (updater_1; phase-8 proposals
  in review)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-09-26-author-signature-patch-docs - architecture and component patch docs, read-
  order mapping, consumption note tickets/tasks/2026-09-26_author_signature_patch_docs_task.md (review 2026-09-26)
- [ ] Task: TASK-2026-09-26-unify-codegen-signature-serializer - one leaf implementation, canonical
  freeze, determinism test tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md
  (review 2026-09-26; landed in commit 6fc9af345; owner-run suites pending)
- [ ] Task: TASK-2026-09-26-hoist-phase8-pool-digest - None-first check and pass-hoisted digest in the
  occurrence strategy, tests tickets/tasks/2026-09-26_hoist_phase8_pool_digest_task.md
  (review 2026-09-26; owner-run harness before/after pending)
- [ ] Task: TASK-2026-09-26-gate-cache-emission-on-replayable-payloads - refuse creation-cache
  emission for spells whose rows cannot replay their contract payload (owner option B)
  tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md (review 2026-09-26)
- [ ] Task: TASK-2026-09-26-live-contract-override-operands - descriptor rename `spell_override` ->
  `override`; phase-9 refs; ref-only rows; live resolution at hydration; gate retired (owner ruling)
  tickets/tasks/2026-09-26_live_contract_override_operands_task.md (ready 2026-09-26; P1 with the owner)
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery.

## Acceptance Criteria
- One implementation; both facades delegate; no behavioural change for inputs that were deterministic
  (proved by the corpus test); the determinism test exists and passes owner-run.
- Phase 8 hashes the pool-wide rows once per pass; the breakdown harness plan_group busy row at
  workers=1 is recorded before and after (owner-run).
- Patch docs promoted; `src_components.md` IR seams block updated; index regenerated in the same pass.
- Owner accepts.

## Validation / Test Plan
- Unit: freeze canonicalization cases (class, function, enum, dataclass, default-repr object, nested
  dict/list/set), serializer tags, sorted-set handling, facade delegation identity.
- Component: two-process determinism over the gauntlet book (subprocess with a different
  `PYTHONHASHSEED`); phase-8 pass-cache digest reuse and None-first skip.
- Owner-run: `pytest -q tests/unit/melder/spellbook/spell_crafter tests/component/melder/spellbook`,
  `python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py` (before/after). "Not run."
- Full plan with baselines, metrics M1-M8 and reporting rules:
  artifacts/codegen_signature_determinism_20260926/measurement_plan.md

## UX / API / Data Notes
- No public API change. Internal helper surfaces keep their names.

## Risks / Mitigations
- Signature bytes drift for previously deterministic inputs -> cache silently stale on the full-hit
  path (no fresh signature is computed on a full hit). Mitigation: the byte-compatibility corpus test;
  a generation bump is the fallback and would be coordinated with melder_0's generation 11.
- Concurrent edits on `shared_compiler_executions.py` (melder_0). Mitigation: NOTICE sent; edits
  sequenced after their hunks land; `git diff -w` before every patch.
- Phase 8 files are in updater_1's review-stage proposals. Mitigation: NOTICE sent; the change is
  confined to the key path and is trivially rebased.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No implementation before the patch docs exist and are linked.
- [ ] No signature change without the corpus test proving byte-compatibility.

## Open Questions
- None blocking. Canonical rendering for non-primitive payload objects is decided in the component
  patch doc (explicit non-cacheable marker) and can be revisited by the owner there.

## Decision Log
- 2026-09-26 (owner): T1 = C-H + C-A approved; C-B deferred (system-wide check and single-spell
  dependency check must stay separately schedulable).
- 2026-09-26 (fable_0): byte-compatibility constraint adopted so no cache generation bump is needed.
- 2026-09-26 (fable_0): the byte-compatibility oracle is the shipped helper bodies frozen verbatim in
  `tests/mocks/spellbook/codegen_signature_reference.py`, compared against live parts on every run;
  the planned owner-run corpus capture is dropped.
- 2026-09-26 (owner): non-value SpellContract payloads on the cache path - option B chosen ("do the
  recommended send it"): refuse cache emission for spells whose rows would not replay their payload
  faithfully. Task 4 opens under this story; the boundary extends to the emission seam.
- 2026-09-26 (owner): task 3 H1 confirmed in the same message.
- 2026-09-26 (owner): `SpellContract` override values may be anything (not literals only); they must ride
  the same path as meld overrides, not a side table; rename `spell_override` -> `override`; SpellMap to
  be checked for the same treatment. Task 5 opens read-only on the overrides path and the peer designs.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/architecture_patch.md
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/component_patch_spell_compiler.md
  - artifacts/codegen_signature_determinism_20260926/ (measurements and test receipts, created on use)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: durable deltas merged into `src_components.md` at closure; patch folder archived to
  `system_docs/patches/completed/` per the closure gate.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: signature determinism; single serializer; phase-8 pool digest.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T09:05:00Z
  TYPE: PLAN
  CLAIM: Three tasks in order: patch docs (gate), serializer unification with the determinism test,
    phase-8 digest hoist. Each code task starts with a Propose -> Confirm message naming the exact files
    and symbols; nothing under src/ is edited before the owner confirms.
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/candidates.md
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:58-137
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:23-158
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:118-372
  IMPACT: Implementation opens inside the epic's boundary with the gate satisfied first.
  NEXT: Task 1: write the two patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T09:18:25Z
  TYPE: PLAN
  CLAIM: Measurement plan recorded (owner asked how improvement is measured). Baselines first, same day
    and machine: B1 breakdown harness at workers 1 and 5 (caching disabled), B2 cold-cache cProfile
    attribution (the 2026-09-25 dump was a full hit and skipped 8-11), B3 signature corpus fixture, B4
    gauntlet parity. C-H is measured by the two-process determinism test on two fixtures (gauntlet book:
    equal before and after; object-payload book: unequal before, equal after), the corpus check and the
    cross-process cache hit-rate run; it is a correctness change and shows no speed delta on the gauntlet
    book by design. C-A is measured by plan_group busy/wall and per-spell plan_group durations (M5), the
    cProfile call/tottime attribution of the two key builders (M6), and a proposed synthetic scaling run
    at 29/100/300 spells (M7) because the quadratic term may be inside noise at 29. Deltas inside the
    BEFORE noise band are reported as no measurable change.
  EVIDENCE:
  - artifacts/codegen_signature_determinism_20260926/measurement_plan.md:1-66
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:1-40
  - benchmarks/testing_other_di/results/real_world_gauntlet_melder.prof
  IMPACT: Every claim this tranche will make has a named number, a command and a failure condition;
    two owner-run scripts (corpus fixture, scaling book) are needed under the artifact directory.
  NEXT: Owner confirms task 2 U1 (files, symbols, freeze rule) and, if wanted, approves the two owner-run
    scripts; fable_0 then writes the scripts under artifacts/ before the first src edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:04:00Z
  TYPE: RISK
  CLAIM: Task 2 is in review (leaf + delegations + oracle + 15 tests; commit 6fc9af345). Its U3 resolved
    the patch's open UNKNOWN the wrong way round: the frozen payload values in persisted phase-11 rows
    are not only hashed, the cache-load path hydrates plan steps from them and constructs with them,
    while the in-process path uses the raw values. Non-value payloads (objects, callables, and
    already today dicts/lists/enums) construct differently after a cross-process cache hit. The
    determinism change stands and is byte-compatible; the seam needs an owner ruling (A keep and
    document / B refuse cache emission for such spells - recommended / C raise at plan time), and B
    or C is a new task under this story (row-builder flag plus `build_package`/`build_manifest_package`).
    Cross-story: the structural snapshot (epic goal) hydrates value rows too, so its row schema must be
    lossless where this one is not - recorded on the epic.
  EVIDENCE:
  - tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:296-341
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:316-340
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:309-395
  IMPACT: Story exit gate unchanged for task 2; a fourth task may be added on the owner's ruling. Task 3
    opens now (H1) on the current strategy bytes (melder_1's FORWARDREF commit shifted the file by +1).
  NEXT: Owner ruling A/B/C and owner-run suites; fable_0 proceeds to task 3 H1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:30:30Z
  TYPE: FACT
  CLAIM: All four tasks are now in review on this story. Task 3 (phase-8 pool digest, one file + one test
    file) and task 4 (emission gate: three helpers, two package builders returning `Optional`, one call-
    site hunk in `spellbook.py`, 267-line unit file, two component tests) landed after the owner's
    "do the recommended send it"; task 2 was already in review. Cross-task: task 4 reuses task 2's
    linked-contract fixture to prove the gate on a real plan, and task 3's M7 probe lives beside the
    measurement plan. Nothing executed in this lane; the owner-run commands are on each task.
  EVIDENCE:
  - tickets/tasks/2026-09-26_hoist_phase8_pool_digest_task.md
  - tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md
  - artifacts/codegen_signature_determinism_20260926/scaling_conjure_probe.py:1-197
  IMPACT: The story's exit gate now waits only on owner-run results (suites, harness before/after, M7)
    and acceptance; promotion into `src_components.md` follows acceptance.
  NEXT: Owner runs the suites and the harness; fable_0 files results per measurement_plan.md and
    prepares the component-map promotion text.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T10:42:09Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner-run results are in for tasks 2-4 (1784 passed; three failures were the new component
    file's own fixture/assertions, fixed and not yet re-run). The failing fixture exposed that
    manifest-first families bind the frozen row projection of contract payload values in-process as
    well as from the cache, so task 4's gate is the cache half of the fix and the in-process half needs
    an owner choice: (1) fail fast on non-replayable payload values, or (2) a live side table of raw
    values for in-process hydration (recommended; touches the override lanes' hydrator files). Task 3's
    AFTER numbers are filed; its BEFORE is still owed because a stale `.git/index.lock` (from this VM)
    broke the owner's stash - the pre-task-3 file is staged under `build/_fable_stage/`.
  EVIDENCE:
  - tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md
  - tickets/tasks/2026-09-26_hoist_phase8_pool_digest_task.md
  - tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md
  IMPACT: Story exit gate: suites need one re-run of the component file; M5-M7 need the BEFORE runs; a
    fifth task opens on the owner's (1)/(2) choice.
  NEXT: Owner: re-run the component file, run BEFORE, pick (1)/(2).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-26T09:05:00Z: opened; task 1 (patch docs) in progress. Resume from task 1's latest STATE line.
STATE 2026-09-26T09:08:00Z: task 1 in REVIEW (patch docs); task 2 ready, waiting on the owner's U1 confirmation; task 3
ready behind task 2.
STATE 2026-09-26T09:18:25Z: measurement plan filed; still waiting on the owner's U1 confirmation for task 2.
STATE 2026-09-26T10:04:00Z: task 2 in REVIEW (commit 6fc9af345, suites owner-run pending); owner ruling open on
the cache-path payload limit; task 3 opens at H1.
STATE 2026-09-26T10:12:00Z: owner chose B and confirmed H1; task 3 in progress (H2); task 4 to be opened after task 3.
STATE 2026-09-26T10:21:00Z: task 3 in REVIEW; task 4 opened (in_progress, G1 done); boundary extended to the emission seam.
STATE 2026-09-26T10:30:30Z: tasks 2, 3 and 4 in REVIEW; waiting on owner-run suites, harness (M5/M6), M7 probe and acceptance.
STATE 2026-09-26T10:42:09Z: suites run (1784 passed; component fixture fixed, re-run owed); AFTER numbers filed; BEFORE owed;
in-process projection decision (1)/(2) open with the owner.
STATE 2026-09-26T10:48:48Z: BEFORE/AFTER filed (results_2026_09_26.md): M7 -34% at N=300, M5 inside noise; component file
5 passed + 1 xfail (bind-side spell id, melder_1); decision (1)/(2) still open.
STATE 2026-09-26T10:56:37Z: owner picked (2); the overrides emitter literalizes payload values (task 4 CONFLICT note), so the
choice is re-asked: (1) now + (2) as an override-design requirement, or (2) in the emitters now.
STATE 2026-09-26T11:26:43Z: owner rules override values may be anything and must ride the meld-overrides path (rename to
`override`); tasks 2-4 stay in review; task-5 investigation (read-only) opens; design after the reads.
STATE 2026-09-26T11:39:16Z: task 5 created (ready) with the live-operand design; waiting on the owner's P1 confirmation;
tasks 2-4 in review. Task 4's gate is scheduled for retirement by task 5.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
