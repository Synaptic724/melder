<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Deep-map phases 8-11, Meld, Creations, and Existence ahead of bug fixes

## Metadata
- Task ID: TASK-2026-06-22-deep-map-phase8-11-meld-creations-existence
- Story: UNKNOWN (bug-fix stories to be opened once concrete bugs are named)
- Status: in_progress
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p1
- Created: 2026-06-22T10:01:14Z
- Updated: 2026-06-22T10:01:14Z

## Objective
Build an evidence-backed mental model of the constructed-spell resolution path
(SpellCompiler phases 8-11), the runtime Meld path, the Creations/SpellSpace
storage model, and the Existence lifetime model, so the upcoming bug fixes are
diagnosed against real source contracts rather than the system_docs summaries.

## Ticket Contract
- ENTRY_GATE: active board row routing optimizer_0 to this task; this ticket
  read before investigation continues.
- EXECUTION_BOUNDARY: READ-ONLY discovery. No code edits in this task. Allowed
  reads: src/melder/aether/spellbook/existence/**, resolution_style_matrix.py,
  spell_types/**, aether/conduit/creations/**, aether/conduit/spell_space/**,
  aether/conduit/meld/**, aether/spellbook/spell_compiler/phases/**,
  spell_compiler.py, spell_compiler_system.py, spell_compiler_artifact.py,
  and the phase-8-11 collaborators (spell_analyzer, artifact_processor,
  codegen_planner, codegen_creation_system) at entry-point depth.
- DEPENDENCIES: related compiler context lives in
  tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md and
  tickets/stories/2026-06-06_phase10_solo_and_many_only_discovery_story.md
  (owned by other agents; referenced, not modified).
- EXIT_GATE: a deep synthesis recorded in Notes + Handoff Summary covering the
  four areas, and the concrete bug list obtained from the user so successor
  implementation tickets can be opened.
- FAILURE_ESCALATION: if a documented contract conflicts with source, record a
  CONFLICT note; if scope must expand past the named files, record a DECISION
  and confirm with the user (expansion gate).

## Scope Boundaries
- In scope: read + understand phases 8-11, Meld, Creations, Existence; capture
  contracts, invariants, ownership, and failure modes with evidence pointers.
- Out of scope: any code edit; reading every codegen-family leaf (solo /
  many_only / generalized compilers + hydrators) before a bug points there.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user directed a deep-understanding pass on these four
  subsystems ahead of a bug-fix lane; discovery is starting now.

## Steps / Checklist
- [ ] Slice 1: Existence model (existence.py, spell_types.py,
      resolution_style_matrix.py) + Creations storage (creations.py,
      conduit_creations.py, cluster_creations.py, spell_space*). Document.
- [ ] Slice 2: Runtime Meld path (meld.py, conduit_meld.py, spellspace_meld.py,
      creation_context*, spell_overrider.py). Document.
- [ ] Slice 3: Compile path (compiler_phase_8/9/10/11, spell_compiler_artifact,
      spell_compiler, spell_compiler_system, shared_compiler_executions) +
      collaborator entry points. Document.
- [ ] Synthesize a cross-subsystem model; obtain the concrete bug list.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Evidence-backed Notes covering Existence, Creations, Meld, and phases 8-11.
- A Handoff Summary that a successor can resume bug diagnosis from.

## Files / Paths Impacted
- None (read-only discovery task).

## Validation
- Not run.
- Recommended commands (user-run, later, against the bug-fix work):
  - pytest tests/unit/melder/aether/conduit -q
  - pytest tests/integration/melder/aether -q

## Risks / Rollback Notes
- Risk: reading the full codegen subtree blind would burn context budget; bound
  the deep leaf reads to whichever family the actual bugs touch.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= minimum_note_score)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: n/a
- CLEANUP_TRIGGER: n/a

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - phases 8-11 occurrence/model/plan/creation handoff
  - meld reuse-vs-construct routing by Existence
  - creations storage + disposal contract
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-22T10:01:14Z
  TYPE: PLAN
  CLAIM: Discovery lane opened. Read the four subsystems in three bounded
    slices (Existence+Creations, Meld runtime, Compile phases 8-11), logging an
    evidence-backed finding per slice, then obtain the concrete bug list before
    opening implementation tickets.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1-1480
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-122
  - src/melder/aether/conduit/creations/creations.py:1-516
  IMPACT: Keeps the bug-fix work grounded in source contracts and resumable
    after compaction.
  NEXT: Read Slice 1 (Existence + Creations) and append a FACT note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-22T10:20:00Z
  TYPE: FACT
  CLAIM: Existence + Creations storage model mapped. Existence has 6 modes;
    `class_based` SpellTypes support all 6, while `callable_based` and
    `existing_object_based` support `unique` only (BINDING_FAMILY_POLICY is
    canonical, MATRIX_BY_SPELL_TYPE is derived). `Creations` is a PURE scoped
    live store: `_creations` is authoritative (unique=id->obj, many=id->list),
    `_disposable_creations` is cleanup-only metadata, and it holds NO pointer to
    any other store -- the meld front door is handed the target store at
    runtime. Broad-lived existences route OUT of the caller store: lineage ->
    owner conduit `_root_creations`; cluster -> elected-leader store via the
    `ClusterCreations` facade (raises if no leader). SpellSpace owns its own
    `Creations` + `SpellSpaceMeld`; a spellspace is neither lineage root nor
    cluster member, so those existences resolve into the owner conduit's
    root/cluster stores, not the spellspace store.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/existence.py:24-80
  - src/melder/aether/spellbook/resolution_style_matrix.py:99-149
  - src/melder/aether/conduit/creations/creations.py:80-92
  - src/melder/aether/conduit/creations/creations.py:193-268
  - src/melder/aether/conduit/creations/cluster_creations.py:128-161
  - src/melder/aether/conduit/spell_space/spell_space.py:120-157
  IMPACT: Any reuse-vs-construct or disposal bug must be triaged against which
    store the meld door selects per Existence, not against `Creations` alone;
    cluster melds hard-error without an elected leader.
  NEXT: Read the Meld shared core (meld.py) + CreationContext execution lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-22T10:35:00Z
  TYPE: FACT
  CLAIM: Meld shared core (abstract) mapped; concrete `meld()` lives in
    ConduitMeld/SpellSpaceMeld. Pre-instance validity ladder:
    `_gated_validation_required` (structural valid/unknown/gated + change-control
    `is_root_dirty` -> MeldExecutionError) -> `run_structural_phases` under
    `spell._lock` -> `_check_contracts_and_force_revalidation` (SpellContract
    defaults force resolution to `gated`) -> `_ensure_resolution_resolvable`
    (per-conduit ConduitResolutionState reruns resolution phases under lock).
    Deferred 8-11 via `_ensure_runtime_resolution_ready` ->
    `_run_deferred_resolution_phases_for_target_spell`; on failure bumps
    `spell._door_epoch` to invalidate warm doors. Warm lane: `_fast_meld_doors`
    spell_id -> (spell, captured_context, creations_store, captured_epoch); the
    executor is re-read per hit off `context._no_overrides_executor` because
    phase-11 hydration HOT-SWAPS that slot in place (cold delegating door -> hot
    executor) on first execute. `CreationContext.execute` only enters
    CreationGate ticket admission in dynamic mode; non-dynamic calls
    `executor(caller_creations)` directly, returning `(instance, created)`.
    Builder: constructed spells need
    `artifact._spell_codegen_creation.{no_overrides,overrides}_executor`;
    existing-creation returns `(spell.user_created_object, False)` and rejects
    overrides with MeldExecutionError. Factory.get_or_build uses
    `spell._creation_context_switch` (CounterSwitch) one-leader election.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:518-566
  - src/melder/aether/conduit/meld/meld.py:683-816
  - src/melder/aether/conduit/meld/meld.py:584-636
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:164-252
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:40-73
  IMPACT: reuse-vs-construct, per-Existence store selection, and the warm
    fast-lane guard ladder all live in the two front doors; the executor
    hot-swap means any reader that caches an executor reference across calls
    pins the cold door -- a likely bug shape.
  NEXT: read ConduitMeld + SpellSpaceMeld (the meld() impls + storage routing).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-22T10:55:00Z
  TYPE: FACT
  CLAIM: Both meld front doors mapped; they are near-parallel. ConduitMeld.meld
    store selection: lineage -> `self._root_creations`; cluster ->
    `self._cluster_creations.resolved_store()` (hard-errors with no leader);
    ELSE (unique, unique_per_conduit, many) -> `self._creations`. SpellSpaceMeld:
    spellspace -> `_spellspace_creations`; lineage -> `_root_creations`;
    cluster -> facade; ELSE -> `_owner_conduit_creations`. The front door ONLY
    selects which store object is passed as `caller_creations`; the actual
    reuse-check + construct + store WRITE happens INSIDE the phase-11-emitted
    `_no_overrides_executor`/`_overrides_executor` (called `executor(creations)[0]`).
    No-hooks/non-dynamic memoizes the warm fast door; hooks or dynamic go through
    `execute()/execute_no_hooks` with CreationGate admission.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:336-435
  - src/melder/aether/conduit/meld/conduit_meld.py:556-586
  - src/melder/aether/conduit/meld/spellspace_meld.py:336-410
  IMPACT: any wrong-instance-reused / duplicate-construction / wrong-scope bug is
    in the phase-11 executor store logic, not the front door.
  NEXT: read phases 8-11 + SpellCompilerArtifact for the analyzer->processor->
    planner->creation handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-22T10:55:30Z
  TYPE: UNKNOWN
  CLAIM: For `Existence.unique`, `meld()` passes `self._creations` (the conduit
    store) as `caller_creations`, but `meld_existing_spell()` reads
    `target_spell._owner_creations` for `unique`. So the store the `unique`
    instance is actually written to / reused from is decided inside the phase-11
    executor (hypothesis: the executor reads `spell._owner_creations` for the
    unique target and uses `caller_creations` only for per-conduit dependency
    scope). Unverified until the phase-11 codegen (solo/generalized compilers)
    is read.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:344-349
  - src/melder/aether/conduit/meld/conduit_meld.py:564-586
  IMPACT: This is the most likely home for reuse/construct/scope bugs; resolve it
    before trusting any construct-path bug diagnosis.
  NEXT: confirm against phase-11 executor source once the bug area is known.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-22T11:05:00Z
  TYPE: FACT
  CLAIM: Phases 8-11 are thin lazy facades that fit artifacts in sequence onto
    the spell-owned `SpellCompilerArtifact`: P8 `SpellAnalyzer` ->
    `_occurrence_graph_analysis`; P9 `SpellArtifactProcessor` ->
    `_spell_codegen_model`; P10 `SpellCodegenPlanner` -> `_spell_codegen_plan`;
    P11 `CodegenCreationSystem` -> `_spell_codegen_creation` (which holds the
    final `no_overrides_executor`/`overrides_executor`). P10/P11 lazy-import
    their subtrees (planner ~11ms; codegen_creation_system ~28ms/77 modules) so
    cache-full-hit conjures skip them. `CreationContextBuilder` reads
    `artifact._spell_codegen_creation.{no_overrides,overrides}_executor`. The
    reuse-vs-construct + per-Existence store WRITE is EMITTED as generated
    source by P11's CodegenCreationSystem -> discovery (solo/many_only/
    generalized) -> family compilers; that codegen layer is the unread depth
    where construct/reuse/scope bugs live.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:76-122
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:81-129
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:71-101
  IMPACT: the executor store logic (the actual bug surface) is in
    `codegen_creation_system/strategies/{solo,many_only,generalized}`; a bounded
    read of the matching family is deferred until the concrete bug names it.
  NEXT: get the concrete bug list from the user; then read the matching codegen
    family (and analyzer/processor/planner) as needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-22T11:40:00Z
  TYPE: FACT
  CLAIM: BUG #1 = lineage-dependency store-routing regression. Tests in
    test_conduit_integration_lineage_isolation.py are CORRECT: they assert the
    documented `unique_per_conduit_lineage` contract (all descendants of a
    lineage share one instance; distinct across roots), and the file docstring
    explicitly labels this "the creation-store routing path that regressed". The
    defect: the inlined no-overrides executor routes a lineage OWNER step to the
    door-threaded `owner_creations` param, but the meld front doors invoke the
    executor with ONLY `caller_creations` (no lineage-root store threaded). So a
    direct lineage meld works (front door passes the lineage-root store AS
    caller_creations), but a lineage spell resolved as a DEPENDENCY of a
    non-lineage parent melded on a LESSER does not reach the shared lineage-root
    store and builds a fresh per-conduit instance. The `_passing_ cross-root
    isolation test confirms direct melds are fine.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_lineage_isolation.py:1-15
  - tests/integration/melder/conduit/test_conduit_integration_lineage_isolation.py:109-127
  - src/melder/aether/spellbook/existence/existence.py:63-70
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:806-820
  - src/melder/aether/conduit/meld/conduit_meld.py:344-377
  - src/melder/aether/conduit/conduit.py:1623-1626
  IMPACT: lineage sharing is silently broken on the dependency path; the fix is
    threading the lineage-root store into the executor calls (runtime side).
  NEXT: pin the exact runtime `owner_creations` value at the front-door no-
    overrides call before patching (see UNKNOWN below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-22T11:40:30Z
  TYPE: UNKNOWN
  CLAIM: One inconsistency to resolve before patching: the inlined no-overrides
    executor signature defaults `owner_creations=None`, and the front door calls
    `_no_overrides_executor(creations)` (one positional, conduit_meld.py:377), so
    `owner_creations` is None at that call -> a lineage step `creations_i =
    owner_creations` would be `None.get_creation(...)` (AttributeError), yet the
    test shows a WRONG INSTANCE, not an error. So there is a hydration/cold->hot
    door wrapper or an argument-binding I have not read that supplies a (wrong,
    per-conduit) store. Also: the dict-path OWNER selector
    (`_select_creations_for_target_kind`, line 1253-1261) returns
    `spell._owner_creations` and does NOT special-case lineage, diverging from
    the inlined path -- a second latent inconsistency.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:709-820
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1253-1261
  - src/melder/aether/conduit/meld/conduit_meld.py:357-399
  IMPACT: must be pinned so the fix targets the real runtime store-threading
    point and covers overrides + the fast-door warm lane + SpellSpaceMeld +
    solo/many_only families, not just one emit site.
  NEXT: read the cold->hot hydration door + the exact executor invocation; then
    open an implementation ticket under the patch-framework gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-22T12:05:00Z
  TYPE: FACT
  CLAIM: Mechanism confirmed (resolves the prior UNKNOWN). The phase-11 doors set
    the lineage/cluster OWNER store = `caller_creations`
    (creation_runtime_door_compiler.py:965/991 `root_creations = caller_creations`;
    inlined no-overrides executor signature `owner_creations=None`, lineage/
    cluster step emits `creations_i = owner_creations`). For a TOP-LEVEL lineage/
    cluster spell this is correct because the front door already selected the
    lineage-root / leader store AS `caller_creations`. For a lineage/cluster
    spell resolved as a DEPENDENCY of a non-lineage parent, `caller_creations` is
    the parent's caller store (the resolving conduit's), so the dependency lands
    in the wrong per-conduit store -> the regression. User hypothesis CONFIRMED:
    the front door does not thread the lineage-root and cluster-leader stores
    into the executor for nested deps. Two sharpenings: (1) lineage and cluster
    are DISTINCT stores conflated into one `owner_creations` param -- a parent
    depending on BOTH is a latent second defect; the fix needs separate
    root_creations (lineage) + cluster_creations (leader) params plus codegen
    routing. (2) CreationContext is SPELL-owned and shared across conduits (one
    per spell, reused by root + all lessers), so the stores MUST be passed
    PER-CALL through execute(), never stored on the context. The front door
    already holds both correct stores (`self._root_creations`,
    `self._cluster_creations`); it just never forwards them.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:959-989
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:709-731
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:806-820
  - src/melder/aether/conduit/conduit.py:1623-1631
  IMPACT: fix = thread root+cluster stores from both meld front doors through
    CreationContext.execute/execute_no_hooks into the executors as distinct
    per-call args; codegen routes lineage->root, cluster->cluster. Must cover the
    no-overrides lane, overrides lane, the warm fast-door, the hooks lane,
    SpellSpaceMeld, and the solo/many_only families. System-impacting -> patch
    gate.
  NEXT: open implementation epic/story + patch artifacts; get user go-ahead.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-27T18:14:52Z
  TYPE: FACT
  CLAIM: Re-onboarded optimizer_0 (post-compaction) and re-read the phase 9-11 +
    solo + many + door + front-door chain in CURRENT state. Phases 9/10/11 are
    thin lazy facades -> SpellArtifactProcessor / SpellCodegenPlanner /
    CodegenCreationSystem (publishes _spell_codegen_model/_plan/_creation).
    CodegenCreationSystem.build -> discovery -> family strategy (solo/many_only/
    generalized). SOLO family = manifest + lazy-door; first meld hydrates:
    compile inner solo no-overrides+overrides executors, then WRAP both in the
    shared CreationContext door (compile_creation_context_hooks_*). The DOOR owns
    get-or-create + per-route store selection; the inner executor owns
    create+add. Door per-route store (creation_runtime_door_compiler
    _build_no_overrides_lines): unique -> _spell._owner_creations (602, SAFE,
    caller-independent); upc -> caller_creations (544, SAFE); many -> no store
    (528-541, SAFE); spellspace -> get-or-create on caller_creations (573);
    lineage -> root_creations = caller_creations (636); cluster ->
    leader_creations = caller_creations (672). The inner solo OVERRIDES executor
    already takes root_creations/leader_creations as a door-supplied 4th
    positional (solo_overrides compiler 311-350) -> the store-selection layer is
    the DOOR, not the inner executor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:503-703
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/hydration/solo_hydrator.py:156-219
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:269-350
  IMPACT: confirms the bug is the door's caller==scope-store assumption for
    lineage/cluster/spellspace; the inner executor contract already supports a
    door-supplied store, so the fix is upstream of the inner create+add.
  NEXT: confirm fix strategy with user (front-door reselect vs meld-threaded).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-27T18:14:52Z
  TYPE: FACT
  CLAIM: CURRENT runtime-flow state verified (my pre-compaction substitution is
    STILL in place and is the live broken-intermediate). Both meld front doors
    compute the correct per-existence store into local `creations`
    (conduit_meld 318-322: lineage->_root_creations, cluster->resolved_store(),
    else->_conduit_creations; spellspace_meld 328-343 adds spellspace->
    _spellspace_creations) BUT then pass `self` (the MELD) to the executors, not
    `creations`: `_no_overrides_executor(self)[0]`, `_overrides_executor(self,
    override_map)[0]`, `execute(self, override_map)`, `execute_no_hooks(self,
    override_map)`. `creations` is now used ONLY in the fast-door memo tuple
    (conduit_meld:362-367 / spellspace_meld:385-390). creation_context.py
    likewise passes `meld` through. The door, however, still expects
    `caller_creations` (a store) and calls `caller_creations.get_creation(...)`,
    so handing it the meld AttributeErrors -> the direct path that used to work
    is now broken (expected per "break it"). meld_existing_spell (conduit_meld
    498-565) was NOT substituted and still selects the correct per-existence
    store, so the no-create probe path is intact.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:318-372
  - src/melder/aether/conduit/meld/spellspace_meld.py:328-395
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:164-252
  IMPACT: two coherent fix strategies, DECISION_REQUEST: (A) MINIMAL -- revert
    the meld->executor substitution so the front door passes the pre-selected
    `creations` store for the ROOT (restores the working direct path), then fix
    ONLY the generalized + many_only DEPENDENCY-step store routing to re-select
    each dep's scope store by existence (the dep path is the real defect; solo
    direct never had it). (B) MELD-THREADED -- pass the meld everywhere and have
    the door + every family compiler pull its own store by existence (1 check at
    the top per the user's spellspace idea). (A) changes least code and keeps the
    hot path param-direct; (B) is uniform but touches the door + all compilers.
  NEXT: get the user's strategy choice, then patch-gate (architecture_patch +
    component_patch under a patch_id, ticket-linked) before any src edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Discovery task for optimizer_0. The spine is mapped and logged across three
slices: (1) Existence model + Creations/SpellSpace storage; (2) Meld runtime
(abstract core + ConduitMeld/SpellSpaceMeld front doors, validity gating ladder,
deferred 8-11 rerun, warm fast-door, per-Existence store selection, Creation
Context/builder/factory/overrider); (3) phase 8-11 handoff + SpellCompilerArtifact.
Key model: the meld front door only SELECTS which `Creations` store is passed as
`caller_creations`; the actual reuse-check + construct + store-write is emitted
generated source inside the phase-11 executors. Deliberately UNREAD (bounded by
the expansion gate, pending the concrete bug): the phase-11 codegen executor
subtree (`codegen_creation_system`, 77 modules) and the analyzer/processor/
planner fitting internals. One open UNKNOWN: where `Existence.unique` actually
writes/reads its instance (front door passes the conduit store, but
`meld_existing_spell` reads `spell._owner_creations`) -- resolve in the phase-11
codegen. NEXT: user names the concrete bugs; then read the matching codegen
family and open implementation tickets (patch-framework gate applies to any
system-impacting fix).
