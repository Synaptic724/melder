

# Task: Verify the native store/unique-Spell lock-order inversion and draft writer options

## Metadata
- Completed: 2026-09-25T23:47:39Z
- Summary: Store/Spell lock-order deadlock confirmed and reproduced (0.2.3-0.2.52, GIL and 3.14t); Idea A chosen and
  implemented by the slot-guard task.
- Task ID: TASK-2026-09-25-verify-native-writer-lock-order
- Story: STORY-2026-09-25-verify-override-writer-and-contract
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-25T20:52:31Z
- Updated: 2026-09-25T23:47:39Z

## Objective
Establish from source whether normal-root per-conduit/lineage creation and unique-dependency purge
acquire the same store lock and Spell lock in opposite orders, and draft writer-coordination options.

## Ticket Contract
- ENTRY_GATE: Active attention-board row routes here; story PLAN note recorded.
- EXECUTION_BOUNDARY: Read-only over src/ and artifacts; writes limited to this ticket and
  artifacts/melder_writer_lock_order_20260925/.
- DEPENDENCIES: native_runtime_boundary.md and native_lock_probe.py (updater_0, 2026-09-24).
- EXIT_GATE: Verdict note with full lock-path ranges; options artifact written; status review.
- FAILURE_ESCALATION: CONFLICT if source contradicts the proposal; BLOCKER if probe confirmation
  requires CPython 3.14 and none is obtainable.

## Scope Boundaries
- In scope: Creations store/purge locking, Meld purge doors, the creation runtime door compiler root
  lock emission, generalized unique-dependency steps, the existing lock probe and its results.
- Out of scope: Any src/tests edit; compact-graph and override-planning semantics (melder_1 task).

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted the delivered fix on 2026-09-25 and directed closure.

## Steps / Checklist
- [x] Read Creations store, add_creation and purge locking in full (creations.py, cited 320-579).
- [x] Read ConduitMeld/SpellSpaceMeld purge doors and Meld._resolve_purge_spell.
- [x] Read root door lock emission per Existence (creation_runtime_door_compiler.py, cited 497-871).
- [x] Read generalized unique-dependency Spell-then-store steps (generalized compiler, cited 871-1145).
- [x] Read native_lock_probe.py and native_lock_results.json; reconcile with source.
- [x] Record the verdict and the cycle-forming Existence/scope pairs; leave others UNKNOWN.
- [x] Draft writer options (narrow ordering fix vs full claim protocol) in the task artifact.
- [x] Attempt a CPython 3.14 interpreter via uv for a probe re-run; otherwise record Not run.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Verdict notes with evidence ranges.
- artifacts/melder_writer_lock_order_20260925/writer_options.md

## Files / Paths Impacted
- None in src/ or tests/. Ticket and task artifact only.

## Validation
- Not run.
- Recommended commands (CPython 3.14 only):
  - python artifacts/override_structural_discovery_20260924/native_lock_probe.py

## Risks / Rollback Notes
- Cited ranges may have drifted; re-locate symbols before citing.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_writer_lock_order_20260925/writer_options.md
  - artifacts/melder_writer_lock_order_20260925/native_lock_results_rerun_py314_gil.json
  - artifacts/melder_writer_lock_order_20260925/meld_only_lock_probe.py
  - artifacts/melder_writer_lock_order_20260925/meld_only_lock_results.json
  - artifacts/melder_writer_lock_order_20260925/meld_only_lock_results_py314t.json
  - artifacts/melder_writer_lock_order_20260925/native_lock_results_rerun_py314t.json
  - artifacts/melder_writer_lock_order_20260925/meld_only_standalone_probe.py
  - artifacts/melder_writer_lock_order_20260925/meld_only_standalone_0.2.3_nogil.json
  - artifacts/melder_writer_lock_order_20260925/meld_only_standalone_0.2.52_nogil.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Store lock vs Spell lock acquisition order across creation and purge.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-25T20:54:45Z
  TYPE: FACT
  CLAIM: Purge half of the claimed cycle holds in current source. Creations.purge takes spell._lock
    for Existence.unique, then the store RLock inside _detach_purge_entries; other existences take
    only the store lock. Disposal runs after both locks release. add_creation takes NO lock and relies
    on its caller's writer discipline; add_many_creations takes the store lock.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:429-521
  - src/melder/aether/conduit/creations/creations.py:523-579
  - src/melder/aether/conduit/creations/creations.py:320-352
  - src/melder/aether/conduit/creations/creations.py:354-416
  IMPACT: Spell-then-store order on unique purge is real. The cycle now depends only on whether a
    per-conduit/lineage root door holds that same store while requesting the unique child's Spell lock.
  NEXT: Read the Meld purge door for unique store selection, then the root door lock emission in
    creation_runtime_door_compiler.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T20:55:58Z
  TYPE: FACT
  CLAIM: On a normal root conduit R, one ConduitCreations object is simultaneously the per-conduit
    store, the lineage-root store and every owned unique Spell's _owner_creations. Unique purge is
    authorized only from the owning conduit and runs against that same object. Lessers repoint
    _root_creations to R's store, so a lesser's lineage store is also R's store.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:328-345
  - src/melder/aether/conduit/meld/meld.py:289-301
  - src/melder/aether/spellbook/spell.py:1392-1441
  - src/melder/aether/spellbook/spellbook_creation_system.py:1213-1224
  - src/melder/aether/conduit/meld/conduit_meld.py:204-257
  - src/melder/aether/conduit/conduit.py:383-383
  IMPACT: If a root door holds its store lock while requesting a unique child's Spell lock, the cycle
    with purge closes on ONE lock object. Lineage roots reached from a lesser also use R's store; the
    boundary report says lesser controls do not form the cycle, which may only cover per-conduit.
  NEXT: Read root door lock emission per Existence in creation_runtime_door_compiler.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T20:57:43Z
  TYPE: FACT
  CLAIM: The store/unique-Spell inversion is confirmed from source on the ordinary generalized lane.
    A unique_per_conduit or lineage root door holds its store RLock across the whole inner executor
    (with and without overrides). Inside it, a unique dependency step emits Spell._lock then store
    lock because the planner maps Existence.unique to "spell_lock". Purge of that unique from its
    owner takes Spell._lock then the same store. Opposite orders on one lock pair: deadlock.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:536-564
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:622-652
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:727-753
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:807-835
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:765-816
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:972-1022
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2667-2676
  - src/melder/aether/conduit/creations/creations.py:500-509
  IMPACT: A live correctness defect independent of the optimization. Structurally the lineage door
    reached from a LESSER of R also holds R's store (conduit.py:2215), a case the boundary report
    lists as not forming the cycle. Cluster depends on whether the leader store is R's (UNKNOWN).
    Override-lane dependency emission (generalized_overrides compiler) not yet read.
  NEXT: Check whether validation permits a unique spell to depend on unique_per_conduit/lineage.
    If it does, a meld-only cycle exists: unique root holds Spell._lock, its per-conduit step needs
    the store that a per-conduit root holding that store waits on (HYPOTHESIS, unverified).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T20:58:21Z
  TYPE: HYPOTHESIS
  CLAIM: The meld-only cycle via unique -> unique_per_conduit/lineage/cluster is refuted: phase-6
    ScopeOrderingStrategy emits an ERROR diagnostic for any broader existence depending on a narrower
    one. It explicitly skips `many` dependencies, so unique -> many is allowed. New hypothesis: a
    unique root door holds U._lock across its plan; a disposal-bearing many step registers into the
    caller conduit store under that store lock. Concurrently a unique_per_conduit root on the same
    conduit holds that store and requests U._lock for its unique dependency. Melds only, no purge.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:30-128
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:594-621
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:908-930
  - src/melder/aether/conduit/creations/creations.py:354-416
  IMPACT: If confirmed, the inversion is reachable by ordinary concurrent first resolution, not only
    by purge, which raises its severity and constrains any narrow fix (purge-only reordering fails).
  NEXT: Read _append_step_register_source (generalized no-overrides, from line 1052) to confirm the
    many-register lock and store; confirm ERROR diagnostics block conjure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T20:58:46Z
  TYPE: FACT
  CLAIM: Previous HYPOTHESIS promoted for lock ORDER (reproduction Not run). A disposal-bearing many
    step registers through Creations.add_many_creations, which takes the caller store RLock, while a
    unique root door already holds U._lock. A unique_per_conduit root on the same conduit holds that
    store and takes U._lock for its unique step. Ordinary concurrent melds therefore close the same
    store/Spell cycle without purge when U is not yet created. Also: the emitter comment at the many
    register branch says the append is "lockless"; add_many_creations locks. Stale comment.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1052-1143
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:765-816
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:594-621
  - src/melder/aether/conduit/creations/creations.py:354-416
  IMPACT: Severity rises: first-resolution races deadlock with no purge involved. A purge-only fix
    (reorder purge to store-then-Spell) would NOT close this cycle. Writer options must cover all
    registration paths, as the proposal states. Not reproduced: needs a CPython 3.14 run.
  NEXT: Read the generalized overrides compiler dependency emission (around line 2078) to confirm the
    override lane mirrors the no-overrides lock order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T20:59:55Z
  TYPE: FACT
  CLAIM: The generalized OVERRIDES lane mirrors the ordinary lock order: unique steps take Spell._lock
    then store (construct under Spell._lock, register under store); per-conduit/lineage/cluster steps
    hold the store across construction. Cluster store is the elected leader conduit's _creations, so a
    cluster root closes the cycle when the leader owns the unique spell. Cycle pairings, lock order
    from source, reproduction Not run:
    (1) per-conduit root on R x purge(U owned by R) - closes;
    (2) lineage root on R or on any lesser of R x purge(U) - closes;
    (3) cluster root with leader R x purge(U) - closes; other leaders UNKNOWN;
    (4) per-conduit/lineage/cluster root on R x meld(U root) whose plan registers a disposal-bearing
        many into R's store - closes with melds only;
    (5) SpellSpace store variants need one Space shared across threads - UNKNOWN whether supported.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2000-2230
  - src/melder/aether/conduit/creations/cluster_creations.py:106-188
  - src/melder/aether/conduit/conduit_cluster.py:689-689
  - src/melder/aether/conduit/conduit_cluster.py:767-767
  - src/melder/aether/conduit/conduit.py:2215-2215
  IMPACT: The defect is lane-independent and wider than the 2026-09-24 probe matrix (which qualified
    only per-conduit and lineage on normal roots). Any fix must change the shared lock discipline, not
    one route.
  NEXT: Write artifacts/melder_writer_lock_order_20260925/writer_options.md with narrow vs protocol
    options against pairings 1-4, then register it on the artifact board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:01:44Z
  TYPE: DECISION_REQUEST
  CLAIM: Writer options written. Purge reordering and racing construction are rejected with reasons.
    Recommended: option C, per-entry creation locks with store locks as leaves, shipped as its own
    correctness fix before the override optimization; the compact prelude later reuses those entry
    locks in a total order. Owner decides (1) separate fix vs fold into joint alpha, (2) unique entry
    lock stays Spell._lock or becomes a dedicated lock after the audit.
  EVIDENCE: artifacts/melder_writer_lock_order_20260925/writer_options.md:1-113
  IMPACT: Implementation of either path is blocked on this decision plus the section-4 lock audit and
    patch docs; no code change is authorized by this task.
  NEXT: Attempt a CPython 3.14 interpreter via uv to reproduce rows 1 and 4 with the existing probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:05:24Z
  TYPE: MEASURE
  CLAIM: Re-ran updater_0's native_lock_probe.py unchanged on a VM copy of today's src/tests/benchmarks
    (repo untouched) with CPython 3.14.7 GIL build via uv. Normal-root unique_per_conduit and lineage
    cases report native_purge_would_block True in both lanes; many, unique, space and lesser
    unique_per_conduit do not. Matches the 2026-09-24 free-threaded run. Rows 1-2 (normal root) are
    reproduced. Not exercised: lineage from a lesser, cluster (row 3), meld-only row 4, 3.14t today.
  EVIDENCE:
  - artifacts/melder_writer_lock_order_20260925/native_lock_results_rerun_py314_gil.json:592-1916
  - artifacts/override_structural_discovery_20260924/native_lock_probe.py:133-209
  IMPACT: The purge cycle is live on current source, not a stale finding. Row 4 remains source-derived.
  NEXT: Owner checkpoint; then, if approved, a task-owned probe for row 4 and lesser-lineage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:11:20Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Owner challenge: unique and unique_per_conduit are different lifetimes, so why do they collide?
    Answer: they share one store. A normal root's conduit._creations is handed to every owned spell as
    _owner_creations, and the purge door returns that same object for both unique and per-conduit.
    Different lifetimes, one store lock. Added option E (separate unique store per owning root): closes
    rows 1-3, not row 4. Choice between C and E depends on whether row 4 reproduces.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1216-1219
  - src/melder/aether/conduit/conduit.py:328-330
  - src/melder/aether/conduit/meld/conduit_meld.py:233-242
  - artifacts/melder_writer_lock_order_20260925/writer_options.md:1-132
  IMPACT: Reframes the defect as a storage-sharing problem and offers a smaller candidate fix than C.
  NEXT: Owner approval to run the row-4 probe on the VM source copy; it now decides C vs E.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:19:45Z
  TYPE: MEASURE
  CLAIM: Meld alone deadlocks; reproduced. Task-owned probe meld_only_lock_probe.py on the VM source copy,
    CPython 3.14.7 GIL: thread A melds a unique_per_conduit (or lineage) consumer of a not-yet-built unique;
    A holds the store and requests the unique's Spell lock. Thread C melds the unique directly; C holds its
    Spell lock and its own check/register step requests the same store. cycle_formed True in all four
    cases, INCLUDING the control with no disposal method. Correction to the 20:58 notes: the trigger is
    ordinary unique creation (Spell then store), not a disposal-bearing many. The many-register path is a
    second, still source-derived variant (4b). C's contended request was refused by instrumentation, so no
    process actually hung; without the probe both threads would wait forever.
  EVIDENCE:
  - artifacts/melder_writer_lock_order_20260925/meld_only_lock_results.json:1-540
  - artifacts/melder_writer_lock_order_20260925/meld_only_lock_probe.py:79-146
  IMPACT: Purge is not required. Any concurrent first resolution of a unique and a per-conduit/lineage
    consumer of it can hang. Option E (separate unique store) closes this row; 4b would survive E.
  NEXT: Owner decides C vs E; optionally probe 4b in isolation and repeat on 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-25T21:22:39Z
  TYPE: MEASURE
  CLAIM: Both probes repeated on free-threaded CPython 3.14.7t (sys._is_gil_enabled() False, VM source
    copy). Meld-only: cycle_formed True in all four cases. Purge: per-conduit and lineage block in both
    lanes; many/unique/space/lesser do not. Identical to the GIL runs; the defect is lock order, not GIL.
  EVIDENCE:
  - artifacts/melder_writer_lock_order_20260925/meld_only_lock_results_py314t.json:1-540
  - artifacts/melder_writer_lock_order_20260925/native_lock_results_rerun_py314t.json:592-1916
  IMPACT: Reproduced on the project's target interpreter; no build-specific caveat remains for rows 1, 2, 4.
  NEXT: Owner decides C vs E; optional isolated 4b probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:25:20Z
  TYPE: MEASURE
  CLAIM: The meld-only deadlock is NOT a regression: published melder 0.2.3 (PyPI wheel, VM-only install)
    forms the same cycle. Standalone version-agnostic probe, free-threaded CPython 3.14.7t: cycle_formed
    True for unique_per_conduit and lineage consumers, with and without a disposal method, on 0.2.3 and on
    current source (reports 0.2.52). Negative control (consumer bound many, so no store held) shows no cycle
    on both versions, so the probe discriminates. 0.2.3 has no purge; entries were reset by removing them
    from the store dict after warm-up.
  EVIDENCE:
  - artifacts/melder_writer_lock_order_20260925/meld_only_standalone_0.2.3_nogil.json:1-527
  - artifacts/melder_writer_lock_order_20260925/meld_only_standalone_0.2.52_nogil.json:1-527
  - artifacts/melder_writer_lock_order_20260925/meld_only_standalone_probe.py:1-186
  IMPACT: The defect predates the purge feature and the 0.2.x cache/named/hook work; it has shipped since
    at least 0.2.3. Release notes for the fix should say so.
  NEXT: Owner decides C vs E; optional isolated 4b probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:34:17Z
  TYPE: UNKNOWN
  CLAIM: Owner-directed read of the component map for Meld, ConduitMeld, SpellSpaceMeld, Spell and Conduit
    (index verified current). Two documented claims conflict with what the probes and generated code show:
    (1) "One instance RLock serialising resolution within a Meld" - if held across execution, two melds on
    one conduit could not overlap, yet the cycle forms; (2) lineage/cluster "use spell._owner_creations" -
    the runtime door uses meld._root_creations and the cluster leader store. Both need a source read.
  EVIDENCE:
  - system_docs/src_components.md:2733-3016
  - system_docs/src_components.md:5104-5119
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:622-652
  IMPACT: If the Meld RLock exists but is released before execution, its scope matters for any fix design.
  NEXT: Read meld.py lock usage when the owner turns to the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T21:51:08Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner question: why does Creations lock at all when it only holds dicts? Single dict/list
    operations are already atomic in CPython, GIL and free-threaded alike, so the RLock is not protecting
    the dict. It serves three compound jobs: (1) get-or-create-once for shared lifetimes - the door holds
    it across the whole build, including user constructors and other locks; (2) keeping _creations and
    _disposable_creations paired; (3) making cleanup/purge detach atomic against in-flight registration.
    Jobs 2-3 are short and never call out, so a leaf lock is safe. Job 1 is a construction mutex borrowed
    from the store lock, and it is the sole source of every deadlock in the regression matrix. Direction:
    move once-only construction to a per-entry guard; shrink or remove the store lock.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:43-45
  - src/melder/aether/conduit/creations/creations.py:320-352
  - src/melder/aether/conduit/creations/creations.py:354-416
  - src/melder/aether/conduit/creations/creations.py:523-579
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:536-564
  IMPACT: Reframes the fix: separate "build once" from "keep the registry consistent".
  NEXT: Owner discussion of the once-guard shape (per-entry lock vs pending-future claim).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:58:25Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner constraints: no restriction of composition (validator tightening rejected); SpellSpaces
    are shared across threads. Revised recommendation (writer_options.md section 9): Idea A - per-entry
    build guards for every shared lifetime (unique included, moved off Spell._lock), store locks reduced to
    leaf dict locks, many unguarded. Deadlock-free by the dependency DAG itself, independent of existence
    ranks. Idea B (one creation lock per root tree) only as an emergency stopgap; Idea C (separate
    root/scope stores) optional companion. Owner to choose A, or B then A.
  EVIDENCE: artifacts/melder_writer_lock_order_20260925/writer_options.md:1-208
  IMPACT: Defines the fix direction; implementation still gated on the listed audit and patch docs.
  NEXT: Owner decision; then audit section 9 items and add the unique -> many -> per_conduit test case.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-25T22:10:46Z
  TYPE: MEASURE
  CLAIM: Owner asked whether the deadlock is only a root-based situation. Probe (3.14.7t, VM copy): thread A
    holds a LESSER's or a shared SPELLSPACE's store building a scope consumer and waits for unique U's Spell
    lock; thread C melds U through the same door. In all four cases (U -> many -> scope leaf; U -> disposal
    many; each on lesser and on space) C never requested the scope store and both threads completed. A unique
    build therefore touches only its owner root's store, never the calling lesser's or space's store (mechanism
    in source not yet read). Every reproduced deadlock needs a door holding the ROOT store (per-conduit on the
    root, lineage from root or lessers, cluster with the owner as leader, purge) while waiting on a Spell lock.
  EVIDENCE:
  - artifacts/melder_writer_lock_order_20260925/scope_store_probe_results.json:1-62
  - artifacts/melder_writer_lock_order_20260925/scope_store_probe.py:1-139
  IMPACT: Confirms the owner's framing: the defect is the root store serving both root-based slots and the
    root's own scope while a door holds it across a build. Splitting stores alone still fails (a unique build
    publishes, registers disposal manys and builds many-reached scope leaves in its owner's store).
  NEXT: Owner decides whether slot guards apply to root/leader stores only or uniformly (simpler codegen).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-25T22:38:26Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner idea: take the Spell lock before entering Creations. That is already the unique door's
    shape (Spell._lock, brief store check, build, brief store publish) - i.e. a per-slot build guard.
    The cycle exists because per-conduit/lineage/cluster have no guard of their own and use the store
    RLock as build-once mutex across construction, so they reach the unique's Spell lock while holding
    the store. Consumer-side pre-acquisition of all dependency Spell locks rejected: needs a global lock
    order, serializes warm hits on the unique, misses melds made inside constructors. Owner restated the
    fix as "an intermediary in Spell representing the build": agreed, under three conditions: (1) no
    thread holds the store lock while waiting on any guard (store lock = dict check/publish only);
    (2) guard keyed per (store, spell) - a single per-Spell guard is still deadlock-free (acquisition
    follows the acyclic spell DAG) but serializes every conduit/space building that spell;
    (3) a dedicated lock, not Spell._lock, which also serves meld-time validation (doc intent; the full
    user list is UNKNOWN, section 9 audit). In-dict "building" placeholder rejected: every dict reader,
    including the lock-free warm path and purge, would have to learn to wait on it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:536-564
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:594-621
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:972-1022
  - system_docs/src_architecture.md:663-671
  - artifacts/melder_writer_lock_order_20260925/writer_options.md:138-241
  IMPACT: Same fix as Idea A, now framed as extending the existing unique pattern to every slotted
    lifetime. Placement of the guard map is the remaining design choice.
  NEXT: Owner picks guard placement (Spell-held map keyed by store vs store-held map keyed by spell_id)
    and scope (every store vs root/leader only).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T23:28:41Z
  TYPE: DECISION
  CLAIM: Owner chose Idea A and approved implementation (store-side guards, every store; unique keeps
    Spell._lock). Implemented and validated under TASK-2026-09-25-implement-creation-slot-build-guards.
  EVIDENCE: tickets/tasks/2026-09-25_implement_creation_slot_build_guards_task.md
  IMPACT: This verification lane's DECISION_REQUESTs are resolved.
  NEXT: Close together with the implementation task after owner review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T23:47:39Z
  TYPE: DECISION
  CLAIM: Owner accepted the implemented fix; the verification lane closes. Section-9 audit outcome: Meld
    RLock scope closed (never held across builds); other items were not needed by the chosen design.
  EVIDENCE: tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md
  IMPACT: None further.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Done 2026-09-25T23:47:39Z (owner accepted the implemented fix). State 2026-09-25T22:38:26Z: review, awaiting owner decision on the fix direction.
Facts: store RLock / unique Spell._lock inversion confirmed in source and reproduced (0.2.3 and 0.2.52,
GIL and 3.14t); 7 deadlock shapes and 4 safe shapes pinned in
tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py.
Owner constraints: do not restrict composition; SpellSpaces are shared across threads. Recommended:
writer_options.md section 9, Idea A (per-entry build guards, leaf store locks), framed with the owner as
extending unique's Spell-lock-first pattern to every slotted lifetime (22:38 note). Open: guard placement
(Spell vs store) and scope (all stores vs root/leader). Before code: audit list in section 9, patch docs
under system_docs/patches/active/, add the unique -> many -> per_conduit test.
VM tooling (outside the repo): ~/work/venv314, ~/work/venv314t, source copy ~/work/melder, 0.2.3 wheel at
~/work/melder023.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
