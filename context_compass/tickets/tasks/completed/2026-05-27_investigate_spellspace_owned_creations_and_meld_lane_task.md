# Task: Investigate spellspace-owned Creations and meld lane
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Task ID: TASK-2026-05-27-investigate-spellspace-owned-creations-and-meld-lane
- Story: none
- Status: done
- Owner: codex
- Agent Name: guard_check_0
- Priority: p0
- Created: 2026-05-27T00:00:00Z
- Updated: 2026-05-30T15:06:13Z

## Objective
Determine what it would actually take for `SpellSpace` to own its own
`Creations` object and possibly its own meld lane, and whether that would
meaningfully reduce contention or just move complexity into runtime ownership
and synchronization.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a bounded investigation of
  spellspace-owned `Creations` / meld-lane design.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/spell_space/spell_space.py`
  - `src/melder/aether/conduit/creations/creations.py`
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - directly required nearby callsites in:
    - `src/melder/aether/conduit/conduit.py`
    - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
  - `tickets/tasks/2026-05-26_implement_plain_ref_creation_storage_for_non_disposable_entries_task.md`
  - `tickets/tasks/2026-05-27_investigate_creations_guard_and_lock_need_task.md`
- EXIT_GATE: the investigation explicitly answers:
  - what ownership edges would move if SpellSpace owned its own `Creations`
  - whether `Meld` would need a second spellspace-specific lane or just a
    different storage target
  - which locks or contention points would actually disappear
  - one bounded recommendation for or against the idea
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a truthful answer requires
  widening into broad compiler or architecture redesign beyond this seam.

## Scope Boundaries
- In scope:
  - spellspace runtime ownership today
  - current spellspace storage and retrieval path
  - current `Meld` and `CreationContext` spellspace route assumptions
  - lock/contention implications of moving spellspace state into its own
    `Creations`
- Out of scope:
  - implementation
  - broad conduit pooling redesign
  - scheduler or transaction redesign

## Steps / Checklist
- [ ] Read SpellSpace, Creations, Meld, CreationContext, and the directly
      implicated conduit/codegen callsites.
- [ ] Map current ownership and route assumptions for spellspace-scoped objects.
- [ ] Determine whether a spellspace-owned `Creations` would require a separate
      meld lane or only a different storage injection point.
- [ ] Summarize contention wins, new complexity, and one bounded recommendation.

## Validation
- Not run.

## Notes
- DATETIME: 2026-05-27T00:00:00Z
  TYPE: PLAN
  CLAIM: The user wants a real investigation of one architectural idea, not a
    generic optimization answer: make `SpellSpace` own its own `Creations`
    object and maybe its own meld lane so spellspace-scoped work is distributed
    better and lock contention is spread out. The first job is to map the
    current ownership and route assumptions before recommending anything.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is source reading only. No implementation should happen
    until the current spellspace ownership/runtime seam is explicit.
  NEXT: read `spell_space.py`, `creations.py`, `meld.py`, and the directly
    implicated conduit/codegen callsites first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T00:00:00Z
  TYPE: FACT
  CLAIM: Current ownership is strictly conduit-centered. `Conduit` owns one
    `SpellSpaceThreadState`, one `Creations`, one `Meld`, and one
    `SpellSpacePool`; each `SpellSpace` is only an explicit scope handle that is
    injected with that same conduit-owned `Meld` and `Creations`. `SpellSpace`
    itself does not currently own storage or execution machinery; it just checks
    that it is the active scope, then delegates to the injected `Meld`, and on
    cleanup it tells the injected `Creations` to clear its spellspace bucket by
    id.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:254-299
  - src/melder/aether/conduit/conduit.py:757-843
  - src/melder/aether/conduit/spell_space/spell_space.py:21-42
  - src/melder/aether/conduit/spell_space/spell_space.py:52-92
  - src/melder/aether/conduit/spell_space/spell_space.py:130-150
  - src/melder/aether/conduit/spell_space/spell_space.py:181-208
  IMPACT: Moving `Creations` ownership into `SpellSpace` is not a local swap.
    It changes a core conduit-owned ownership edge and would need an explicit new
    path for how spellspace meld calls supply their storage target.
  NEXT: inspect the current `Meld` and generated spellspace runtime routes to
    determine whether spellspace-owned storage can be injected into the current
    lane or whether it forces a separate spellspace meld lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T00:00:00Z
  TYPE: FACT
  CLAIM: A spellspace-owned `Creations` object is plausible, but a spellspace-
    owned meld lane is only justified if we want to remove the active-spellspace
    probe from the runtime path. Today the spellspace route already exists in
    generated runtime, but it assumes `caller_creations` is still conduit-owned:
    it reads `caller_creations.get_active_spellspace()` and then
    `caller_creations.get_spellspace_creation(...)` before locking on miss. That
    means giving `SpellSpace` its own `Creations` without changing the lane
    would not really simplify the route. The clean benefit would come from a
    dedicated spellspace lane that binds a fixed spellspace-owned creations
    object and a fixed spellspace id, which would remove the current active-
    spellspace lookup and shard miss-path coordination per spellspace instead of
    per conduit.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:547-578
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:199-236
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:431-559
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:565-596
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:748-821
  - src/melder/aether/conduit/creations/creations.py:421-441
  - src/melder/aether/conduit/creations/creations.py:456-473
  IMPACT: The real design choice is not “give SpellSpace its own `Creations`,
    done.” It is:
    1. shared conduit `Meld` plus injected per-spellspace creations override, or
    2. a dedicated spellspace-owned meld lane that compiles away active-scope
       probing.
    The contention win exists mainly on spellspace miss/create coordination, not
    on every route in the system.
  NEXT: summarize the recommendation: if we pursue this, do it as a spellspace-
    specialized runtime lane, not as a partial ownership split glued onto the
    current conduit-owned route assumptions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-29T22:59:44Z
  TYPE: DECISION
  CLAIM: The next implementation slice is intentionally narrow: add a concrete
    `SpellSpaceCreations` class beside `Creations` with spellspace-local
    storage only, and do not wire runtime callers in the same step. This keeps
    the extraction honest without mixing in compatibility shims or the larger
    spellspace-meld refactor yet.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:1-582
  - src/melder/aether/conduit/spell_space/spell_space.py:21-208
  IMPACT: The new class can define the target ownership model cleanly before
    we start deleting spellspace branches out of conduit `Creations`.
  NEXT: add `src/melder/aether/conduit/creations/spellspace_creations.py`
    with direct spellspace-local storage and disposal mechanics only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-29T23:01:06Z
  TYPE: MEASURE
  CLAIM: The first extraction slice is landed: a new concrete
    `SpellSpaceCreations` class now exists beside `Creations` and defines a
    spellspace-local storage model with no conduit spellspace stack and no
    spellspace-id bucket indirection. It currently carries direct spellspace
    ownership metadata, singleton/many storage, disposal metadata, and
    reusable clear/reset surfaces only.
  EVIDENCE:
  - src/melder/aether/conduit/creations/spellspace_creations.py:1-275
  IMPACT: We now have the target class shape in the tree, so the next step can
    rewire `SpellSpace` and runtime callers onto it instead of extracting
    spellspace logic out of `Creations` abstractly.
  NEXT: decide the next narrow rewiring slice: `SpellSpace` ownership first or
    direct runtime caller migration first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-29T23:01:06Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed for the new class.
    `python -m py_compile
    src/melder/aether/conduit/creations/spellspace_creations.py` completed
    successfully.
  EVIDENCE:
  - src/melder/aether/conduit/creations/spellspace_creations.py:1-275
  IMPACT: The new class parses cleanly. Broader runtime or unit validation has
    not been run in this slice.
  NEXT: keep the next step focused on one rewiring seam instead of widening
    into tests and runtime migration all at once.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-29T23:29:51Z
  TYPE: MEASURE
  CLAIM: The class split now matches the intended object model. `creations.py`
    defines the base scoped `Creations` class with no spellspace stack or
    spellspace-bucket behavior, and `conduit_creations.py` defines
    `ConduitCreations(Creations)` with conduit/root-only extraction and
    restore behavior. All spellspace-specific methods and branches have been
    removed from `ConduitCreations`.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:1-275
  - src/melder/aether/conduit/creations/conduit_creations.py:1-164
  IMPACT: The two class objects now tell the truth even though runtime callers
    have not been rewired yet. `ConduitCreations` no longer carries the mixed
    spellspace ownership model.
  NEXT: choose one runtime rewiring seam next: `SpellSpace` ownership,
    conduit/runtime imports, or transfer/extract behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-29T23:29:51Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed for the two class files.
    `python -m py_compile
    src/melder/aether/conduit/creations/creations.py
    src/melder/aether/conduit/creations/conduit_creations.py`
    completed successfully.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:1-275
  - src/melder/aether/conduit/creations/conduit_creations.py:1-164
  IMPACT: The object-level split parses cleanly. Broader runtime or unit
    validation was intentionally not done in this slice.
  NEXT: keep the next step on the runtime rewiring seam you choose, not on
    these class definitions again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T00:36:41Z
  TYPE: PLAN
  CLAIM: The user explicitly widened the active spellspace/conduit runtime lane
    into a direct reread of the live conduit tree plus compiler phases 6-12 and
    creation-context surfaces. This tranche is source-reading only and is meant
    to rebuild the current ownership/runtime map from the actual checkout
    before any further design claims are made.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is a bounded reread of the current conduit runtime,
    creation-context path, and compiler phases 6-12 so later spellspace-meld
    recommendations are based on the live code paths instead of stale mental
    models.
  NEXT: read the live conduit subtree, creation-context files, and compiler
    phases 6-12 in capped chunks, then record the first concrete ownership or
    route-shape finding before widening further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T00:39:49Z
  TYPE: FACT
  CLAIM: The current spellspace/conduit split is runtime-incomplete. The base
    `Creations` class no longer owns spellspace-specific APIs, but
    `SpellSpace` still calls `clear_spellspace_instances(...)` and
    `get_active_spellspace()`, so the new object model and the active
    spellspace runtime seam currently disagree.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:10-251
  - src/melder/aether/conduit/spell_space/spell_space.py:137-149
  - src/melder/aether/conduit/spell_space/spell_space.py:204-208
  IMPACT: Any serious spellspace-owned-creations or spellspace-meld design
    decision now has to account for the fact that the current split is only
    partial. The next useful reading pass is the main conduit/meld/runtime
    path, not more speculation about the intended class model.
  NEXT: read `conduit.py`, `meld.py`, `creation_context.py`,
    `creation_context_codegen.py`, and the live compiler phases 6-12 to map
    where the runtime still assumes conduit-owned spellspace state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T00:40:44Z
  TYPE: FACT
  CLAIM: The main conduit runtime still boots the old mixed creations shape.
    `conduit.py` imports the base `Creations` type and constructs it with the
    retired `spellspace_stack` argument instead of using `ConduitCreations`,
    while the new `Creations` base now expects `(owner_conduit_id, id)`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:28-28
  - src/melder/aether/conduit/conduit.py:256-258
  - src/melder/aether/conduit/creations/creations.py:45-68
  - src/melder/aether/conduit/creations/conduit_creations.py:9-45
  IMPACT: The current runtime entry path is still anchored to the pre-split
    storage contract, so any further spellspace-meld reading has to be treated
    as an inconsistent in-progress refactor rather than a settled live design.
  NEXT: continue through `meld.py`, `creation_context.py`,
    `creation_context_codegen.py`, and the compiler phases to see which later
    branches still assume conduit-owned spellspace state and which already
    target the new split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T00:42:33Z
  TYPE: FACT
  CLAIM: The spellspace assumption still runs through both the handwritten
    runtime and the generated execution lanes. `Meld` still resolves
    spellspace-scoped reuse through `caller_creations.get_active_spellspace()`
    and `get_spellspace_creation(...)`, and `creation_context_codegen.py`
    emits the same spellspace route directly into the compiled no-overrides and
    overrides executors.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:548-553
  - src/melder/aether/conduit/meld/meld.py:890-903
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:567-580
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:751-798
  IMPACT: A real `SpellSpaceMeld` or spellspace-owned creations lane would
    need to cut through both front-door runtime code and generated executor
    source. This is not just a constructor swap on `Conduit`.
  NEXT: finish the remaining conduit-ward, transfer, and phase-12 executor
    reads so the ownership/route map includes the contract and registration
    side effects too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T00:43:17Z
  TYPE: FACT
  CLAIM: Ownership transfer is still conduit-creations-centric. The transfer
    helper moves and rolls back creation state by calling
    `extract_spell_creations(...)` and `restore_spell_creations(...)` on the
    source and target conduit `_creations`, so a true spellspace-owned storage
    model would also have to decide what transfer even means for spellspace-
    local live state.
  EVIDENCE:
  - src/melder/aether/conduit/creations/conduit_creations.py:48-142
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:958-991
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1409-1464
  IMPACT: Spellspace-owned creations is not just a meld/runtime problem. It
    also changes transfer semantics, rollback surfaces, and what state is
    considered movable between conduit owners.
  NEXT: finish the remaining executor and ward reads, then summarize the
    current live ownership map and the specific places that would need to split
    if SpellSpace becomes a true owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T00:45:02Z
  TYPE: FACT
  CLAIM: The remaining `ConduitCreations` methods are conduit/root lifecycle
    helpers, not spellspace helpers. `extract_spell_creations(...)` and
    `restore_spell_creations(...)` are still used to move or tear down
    conduit-owned creation payloads during ownership transfer, rollback, and
    contract-consumer invalidation; there are no remaining spellspace lookup or
    spellspace storage APIs on `ConduitCreations` itself.
  EVIDENCE:
  - src/melder/aether/conduit/creations/conduit_creations.py:48-142
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:958-991
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1409-1464
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1846-1852
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1875-1883
  IMPACT: `ConduitCreations` no longer needs spellspace features for its own
    responsibilities. The real remaining spellspace contamination lives in the
    runtime callers and generated executor paths, not in the subclass.
  NEXT: answer the user with the concrete purpose of the remaining
    `ConduitCreations` methods and point at the still-stale runtime callers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T10:30:41Z
  TYPE: DECISION
  CLAIM: The front-door split now looks justified, but the right shape is a
    small shared meld core with two concrete hot-path entry classes, not one
    monolithic `Meld` and not a mostly-empty abstract shell. The current code
    already implies this split: `SpellSpace.meld(...)` calls a missing
    `spellspace_meld(...)` front door and passes both spellspace-owned
    creations and owner-conduit creations, while the current concrete
    `Meld` still exposes conduit-oriented `meld(...)`, `meld_existing_spell(...)`,
    and live-creation probes that route spellspace through
    `caller_creations.get_active_spellspace()` instead of a direct spellspace
    runtime owner. At the same time, spell lookup, override normalization,
    structural gating, contract revalidation, and deferred resolution are still
    shared logic that should not be duplicated across two hot-path classes.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:186-209
  - src/melder/aether/conduit/meld/meld.py:259-701
  - src/melder/aether/conduit/meld/meld.py:752-958
  - src/melder/aether/conduit/conduit.py:256-299
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1962-1975
  IMPACT: The clean rework path is to split caller-specific front doors and
    storage routing into `ConduitMeld` and `SpellSpaceMeld`, while preserving
    one shared base for generic lookup, validation, and compiler/runtime cache
    logic. `SpellSpaceMeld` must receive both spellspace-owned creations and
    owner-conduit creations so `unique_per_spell_space` and
    `unique_per_conduit` can diverge correctly at the front door.
  NEXT: answer the user that the split makes sense, but recommend a shared
    base with two concrete front ends rather than turning the entire current
    `Meld` body into an abstract shell.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T10:46:42Z
  TYPE: FACT
  CLAIM: The started split is not structurally real yet. `Meld` is still a
    concrete class with the full old shared+caller-specific state surface,
    while both `ConduitMeld` and `SpellSpaceMeld` currently add no new attrs,
    keep the same constructor shape as the base, and duplicate the old class
    body instead of specializing front-door/runtime differences. The subclass
    `__slots__` are empty extensions over `Meld.__slots__`, so the state split
    we actually need for the rework is still missing:
    `SpellSpaceMeld` does not yet declare spellspace-owned creations plus
    owner-conduit creations as distinct inputs, and `ConduitMeld` does not yet
    shrink to the conduit-only store shape.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:42-140
  - src/melder/aether/conduit/meld/conduit_meld.py:41-112
  - src/melder/aether/conduit/meld/spellspace_meld.py:42-113
  - src/melder/aether/conduit/spell_space/spell_space.py:186-209
  IMPACT: Before deciding whether `Meld` should be an ABC, the first real
    design move is to separate shared-core attrs from caller-specific attrs.
    Right now the subclass files are shape-compatible placeholders, not a
    meaningful runtime split.
  NEXT: answer the user that the current attr layout is not correct yet and
    propose a concrete shared-base vs subclass-owned-state division before more
    code is copied around.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T10:46:42Z
  TYPE: FACT
  CLAIM: The new subclasses are not wired into runtime construction yet.
    `Conduit` still constructs `Meld` directly, and `SpellSpace` /
    `SpellSpacePool` still type and inject the generic `Meld` surface instead
    of `SpellSpaceMeld`. So even if the subclass files exist, the live runtime
    still does not instantiate or benefit from the split at all.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:286-292
  - src/melder/aether/conduit/spell_space/spell_space.py:13-18
  - src/melder/aether/conduit/spell_space/spell_space.py:55-67
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:12-18
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:35-44
  - src/melder/aether/conduit/meld/conduit_meld.py:41-112
  - src/melder/aether/conduit/meld/spellspace_meld.py:42-113
  IMPACT: The first implementation step is not only attr cleanup inside the
    meld files; it also needs runtime construction rewiring so the two front
    doors are real objects instead of dead classes.
  NEXT: answer the user with the exact shared-base attrs and subclass-only
    attrs, then rewire `Conduit` / `SpellSpace` creation once that split is
    explicit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to answer whether spellspace-owned `Creations` and/or a
spellspace-specific meld lane is a real contention win or just a more complex
ownership model.
