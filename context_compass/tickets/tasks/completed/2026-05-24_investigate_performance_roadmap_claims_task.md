# Task: Investigate performance roadmap claims

## Metadata
- Task ID: TASK-2026-05-24-investigate-performance-roadmap-claims
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T17:09:44Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Audit the proposed Melder performance roadmap against current source and
available measurements so we can separate real high-value opportunities from
claims that are stale, overstated, or already invalidated by recent changes.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for research on the proposed roadmap.
- EXECUTION_BOUNDARY:
  - roadmap items and local notes in the current thread
  - `src/melder/**` files directly implicated by the top-ranked items
  - existing local benchmark and investigation files already tied to meld,
    pooling, and mediator overhead
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
  - `tickets/tasks/2026-05-24_investigate_transaction_mediator_runtime_overhead_task.md`
- EXIT_GATE: at least the top roadmap claims are classified as
  supported/unsupported/needs-measurement with direct evidence and practical
  next steps.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if honest classification needs a
  broader benchmark campaign than a bounded audit.

## Scope Boundaries
- In scope:
  - top roadmap items, especially 1-5 and 9-10
  - source-backed validation against current runtime shape
  - focused measurement only when source inspection is insufficient
- Out of scope:
  - implementing the optimizations in this task
  - broad new benchmark harness work
  - rewriting the roadmap wholesale without evidence

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested research on the proposed
  performance roadmap.

## Steps / Checklist
- [ ] Classify the highest-priority roadmap items against current source.
- [ ] Reuse existing focused measurements where they already answer the claim.
- [ ] Run one bounded new measurement only if a top claim is still ambiguous.
- [ ] Summarize which items are real, stale, overstated, or already partly done.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one evidence-backed audit of the proposed performance roadmap
- one ranked subset of credible next opportunities

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Possible commands:
  - focused local measurements only where source inspection is insufficient

## Risks / Rollback Notes
- Risk: some roadmap items may be directionally right but numerically stale.
- Rollback: keep the audit at the claim level and mark uncertain items as
  `UNKNOWN` instead of forcing a verdict.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No treating the pasted roadmap as fact without checking current code.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: claim classification, concrete evidence, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

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
- DATETIME: 2026-05-24T17:09:44Z
  TYPE: PLAN
  CLAIM: The pasted roadmap mixes solid observations, stale numbers, and claims
    that need to be revalidated against current code after pooling and recent
    cleanup changes. The right cut is to audit the highest-value items first
    instead of blindly agreeing or dismissing them.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is a top-item source audit, not implementation.
  NEXT: classify items 1-5 against the current meld path, creation path, and
    mediator findings already on file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T17:29:18Z
  TYPE: FACT
  CLAIM: The first roadmap pass splits the top items into three buckets:
    1. **Supported and still high-value**
       - #1 seal / warm-resolve object cache: not built today; current meld
         only caches spell lookup identity, not resolved live-instance hits
         at the front door.
       - #5 hoist `get_active_spellspace`: real; current generated
         creation-context code still emits repeated
         `caller_creations.get_active_spellspace()` and
         `get_spellspace_creation(...)` lookups on the spellspace route.
       - #4 one lock per executor run instead of per-step: directionally real;
         current generated no-overrides code still emits repeated
         `with caller_creations._lock:` branches inside route-specific bodies.
    2. **Partly true but overstated/stale**
       - #3 lock elision on the warm read path: some direct hit paths already
         avoid locking before checking `caller_creations._creations.get(...)`,
         so the claim is not "not built at all"; the remaining lock traffic is
         more specific than that.
       - #10 lazy/lighter `DevopsIdentity`: lesser conduits still create a
         `DevopsIdentity`, but registry attachment currently happens only for
         normal conduits, so the old claim that every scope churn path is
         fighting framewide registry attach contention is stale.
    3. **Incorrect as phrased for current code**
       - #2 de-scope `TransactionMediator` from scope create/cleanup:
         `TransactionMediator` is not in `Conduit.create_lesser_conduit(...)`
         at all. It is a real cost center for transaction-changing paths, but
         it is not the direct cause of lesser-conduit creation overhead.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:334-369
  - src/melder/aether/conduit/meld/meld.py:494-529
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:568-569
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:758-805
  - src/melder/aether/conduit/conduit.py:1552-1653
  - src/melder/aether/conduit/conduit.py:1946-2183
  - src/melder/aether/spellbook/spellbook.py:2139-2302
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:630-742
  - src/melder/aether/conduit/conduit.py:243-252
  - src/melder/aether/conduit/conduit.py:1473-1478
  - validation_result: focused one-meld and mediator-overhead investigations in linked tasks
  IMPACT: The roadmap is useful, but only part of it survives contact with the
    current code unchanged. The next optimization conversation should focus on
    #1, #4, and #5 first, while rewriting #2 and qualifying #3 and #10.
  NEXT: summarize this first-pass classification to the user and ask whether to
    deepen one of the supported items, most likely #1 or #4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T17:13:59Z
  TYPE: MEASURE
  CLAIM: The new 3-thread real-world gauntlet cProfile dataset strengthens
    three roadmap items and weakens one. It strengthens:
    - #5 `get_active_spellspace` hoisting: current melder run shows
      `spell_space_thread_state.get_active` and `creations.get_active_spellspace`
      at `17,916` calls each in the hot path.
    - #7 pool reset path: `conduit_pool.return_lesser_conduit` and
      `creations.reset_non_spellspace_for_pool` are now visible hot functions,
      confirming reset/return is a real post-pooling cost center rather than a
      speculative one.
    - #1 seal / warm-resolve cache: hot-path counts remain dominated by
      `_get_existing_creation`, `creation.value`, `cleanable.check_cleaned`,
      and repeated no-overrides creation-context calls, which is exactly the
      kind of repeated descend-through-the-stack cost a front-door seal would
      collapse.
    It weakens #2 again: the gauntlet is still dominated by scope/meld/runtime
    churn, not mediator; mediator does not appear in the melder cProfile top
    surfaces at all for this benchmark shape.
  EVIDENCE:
  - user_provided_profile_dataset
  IMPACT: The roadmap should be reordered with higher confidence around #1,
    #5, and #7, while #2 should stay scoped to transaction-changing
    operations instead of being treated as the gauntlet tail culprit.
  NEXT: summarize which roadmap items this dataset directly supports and which
    ones it does not.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T17:50:24Z
  TYPE: DECISION
  CLAIM: The current top-20 ranking should be ordered by expected payoff times
    confidence, not by raw originality. The strongest near-term items are:
    1) front-door warm-hit seal
    2) spellspace active lookup hoist
    3) pool reset/return optimization
    4) executor-side lock consolidation
    5) targeted creations-hit-path cleanup
    After those, the next tier is first-build Phase 11 churn, transaction
    locality narrowing for link, and a more explicit warm-path cache split for
    repeated object/frame resolution. TransactionMediator remains a real
    optimization target for mutation-changing paths, but it should not stay
    ranked as a top gauntlet-path issue because current source and focused
    measurements show it is not in lesser-conduit creation and does not appear
    in the main gauntlet hot surfaces.
  EVIDENCE:
  - linked findings in this task
  - linked findings in `2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
  - linked findings in `2026-05-24_investigate_transaction_mediator_runtime_overhead_task.md`
  IMPACT: The next recommendation to the user should be one concrete execution
    slice focused on #1 and shaped to absorb #4 and #5 where they overlap,
    rather than splitting effort across many medium-confidence ideas.
  NEXT: present the full ranked list and recommend one immediate slice:
    design and land the front-door warm-hit seal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T17:50:24Z
  TYPE: FACT
  CLAIM: The ranking is now promoted into a durable epic:
    `tickets/epics/2026-05-24_melder_runtime_performance_optimization_epic.md`.
    That epic carries the ranked 20 opportunities plus explicit evidence lines
    for the strongest claims instead of leaving the ordering only in chat or in
    this investigation task.
  EVIDENCE:
  - tickets/epics/2026-05-24_melder_runtime_performance_optimization_epic.md:1-200
  IMPACT: The next turn can start from the epic directly and spawn the first
    child execution slice without replaying the ranking work.
  NEXT: hand the epic to the user and recommend the first implementation cut:
    the warm-hit seal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:44:52Z
  TYPE: MEASURE
  CLAIM: The new single-thread `test_melder_gauntlet_cprofile.py` dataset
    tightens the ranking again for the spellspace-heavy path. Once import,
    conjure, and thread-join noise are discounted, the strongest remaining
    runtime signals are:
    - `RLock` enter/exit churn (`39,900` each)
    - `_get_existing_creation` (`7,205`)
    - `cleanable.check_cleaned` (`39,878`)
    - generated no-overrides executor bodies
    - first-build `compiler_phase_8._build_phase8_occurrence_plan_input_signature`
    Spellspace accessor hoisting no longer looks like a top standalone item in
    this dataset, because it does not even appear in the top-25 runtime-heavy
    surfaces here.
  EVIDENCE:
  - user_provided_profile_dataset
  IMPACT: For this exact workload, the correct near-term order is:
    1) warm-hit seal,
    2) creations hit-path / `_get_existing_creation`,
    3) lock churn reduction,
    4) `check_cleaned` bundle,
    5) first-build Phase 8 signature churn.
    Spellspace accessor hoisting should be demoted to a supporting cleanup,
    not treated as a top-level target.
  NEXT: present the corrected ranking explicitly as "for this dataset" instead
    of mixing it with the earlier 3-thread scope-heavy profile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T19:06:30Z
  TYPE: PLAN
  CLAIM: The next investigation tranche is direct competitor reading. The user
    explicitly asked for Dishka’s derived architecture/components docs and the
    installed `dishka` package code so we can compare how its runtime/codegen
    path differs from Melder’s current hot path instead of guessing from
    benchmark numbers alone.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is a bounded read of the two derived docs plus the
    small set of Dishka runtime/codegen files that actually shape warm-hit and
    override behavior.
  NEXT: read the Dishka derived docs and core container/compiler files, then
    summarize what is structurally simpler or flatter than Melder’s path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-24T19:06:30Z
  TYPE: FACT
  CLAIM: Dishka’s core hot path is materially flatter than Melder’s current
    path, but it is also solving a narrower problem. The installed code shows:
    - `Container.get(...)` does not own a large multi-step runtime pipeline; it
      acquires the optional container lock and immediately enters one compiled
      factory callable from the immutable `Registry`.
    - `Registry` lazily compiles and caches per-key factory callables and then
      reuses them.
    - the compiled factory body itself starts with a cache check
      (`return_if_cached`) and then executes the specific creation body.
    - Dishka’s “override” machinery in provider build code is graph-definition
      / activation-time (`override`, `when`) behavior, not Melder-style
      per-meld runtime override payloads.
  EVIDENCE:
  - benchmarks/competitors/dishka/derived_data_documents/architecture/src_architecture.md:95-118
  - .venv_new/Lib/site-packages/dishka/container.py:133-161
  - .venv_new/Lib/site-packages/dishka/registry.py:123-151
  - .venv_new/Lib/site-packages/dishka/code_tools/factory_compiler.py:80-90
  - .venv_new/Lib/site-packages/dishka/code_tools/factory_compiler.py:352-392
  - .venv_new/Lib/site-packages/dishka/provider/make_factory.py:477-525
  - .venv_new/Lib/site-packages/dishka/graph_builder/builder.py:376-398
  IMPACT: The real comparison is not “Dishka has a better version of Melder’s
    runtime overrides.” Dishka is winning by using an immutable registry plus a
    compiled per-key getter path with cache checks inside the compiled callable,
    while Melder still routes warm hits through more generic runtime layers.
  NEXT: use this comparison to keep Melder’s next slice narrow: build a
    hit-only compiled lane for the no-override hot path instead of trying to
    match Dishka with broad override or graph-builder rewrites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T20:45:13Z
  TYPE: PLAN
  CLAIM: The next tranche is lock-shape analysis, not more cache theorizing in
    the abstract. The user wants to know whether Melder is spending too much
    on explicit Python locks now that Python 3.14t already gives builtin
    dict/list/set operations their own C-level locking. The correct cut is to
    inspect the hot-path owners that still add Python `RLock` layers on top of
    those structures and decide which ones are protecting real multi-step
    invariants versus which ones are just layering tax.
  EVIDENCE:
  - user_instruction
  - tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md:152-175
  IMPACT: The next useful output is a concrete lock map for the current
    no-override warm path, not another generic fast-path idea.
  NEXT: read the exact lock sites in `Creations`, `Creation`, `CreationGate`,
    `CounterSwitch`, `cleanable`, and the generated no-override route, then
    classify which locks are probably still semantically necessary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-24T20:45:50Z
  TYPE: FACT
  CLAIM: The current Melder hot path is not paying Python locks for every dict
    read. The no-override generated routes already do lock-free first probes
    against `caller_creations._creations` / `_owner_creations._creations` and
    only enter Python `RLock` blocks for the second-probe-and-create sections.
    The remaining explicit Python lock surfaces in this path are:
    - `caller_creations._lock` / `_owner_creations._lock` in the generated
      no-override and override routes
    - `Creation.value -> check_cleaned()` on every hit
    - `CounterSwitch.selector()` leader election when a spell-owned context is
      not yet published
    - `CreationGate` state transitions / dynamic admission, but not ticket
      append/pop
    By contrast, `Creations.add_creation(...)`, `get_spellspace_creation(...)`,
    and `get_active_spellspace()` themselves are already using builtin dict or
    thread-state operations without extra Python locks on the read path.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:540-618
  - src/melder/aether/conduit/creations/creations.py:307-343
  - src/melder/aether/conduit/creations/creations.py:550-587
  - src/melder/aether/conduit/creations/creation.py:75-97
  - src/melder/utilities/general_base/cleanable.py:64-64
  - src/melder/utilities/synchronization/counter_switch.py:100-160
  - src/melder/utilities/synchronization/creation_gate.py:109-146
  - src/melder/utilities/synchronization/creation_gate.py:209-245
  IMPACT: The next lock-focused work should not start by rewriting builtin
    containers. The better targets are the generated second-probe lock regions,
    the `Creation.value` wrapper/guard layer, and whether shared/owner routes
    really need both `_spell._lock` and `_owner_creations._lock` on misses.
  NEXT: explain this lock split to the user and then decide whether the first
    experiment should be a hit-only lane that bypasses those lock regions or a
    narrower audit of which miss-path locks are still semantically required.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T20:45:50Z
  TYPE: FACT
  CLAIM: The `Creation` wrapper’s own `RLock` does not appear to participate in
    the current warm path. Current source shows the lock is only used by
    `Creation.cleanup()` and the wrapper’s own `__enter__/__exit__` methods.
    The hot-path property reads (`value`, `has_disposal_methods`,
    `disposal_method_names`) now return the stored fields directly, and the repo
    scan did not find runtime callsites using `Creation` as a context manager.
    The remaining live field `_id` is also already dead in current source:
    initialization is commented out and `id` is no longer returned.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creation.py:24-133
  - source_scan: `rg -n "Creation\\(|\\.value\\b|\\.has_disposal_methods\\b|\\.disposal_method_names\\b|\\.id\\b|__enter__\\(|__exit__\\(" src tests benchmarks`
  IMPACT: If we want a safe cleanup-first micro-cut, removing the wrapper lock,
    dead `_id`, and dead `__repr__` surface is much lower risk than rewriting
    the actual creations-route locks. It will not solve the main lock problem,
    but it also does not look like a semantically required hot-path lock today.
  NEXT: tell the user that the real lock tax is in generated creations-route
    second probes, not in the `Creation` wrapper lock, and only remove the
    wrapper lock if they still want that cleanup cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-24T21:03:29Z
  TYPE: FACT
  CLAIM: Disposal metadata is currently spell-owned first and then copied into
    each live `Creation` wrapper at registration time. `Spell` starts with
    empty `disposal_method_names` / `has_disposal_methods`; then
    `SpellbookCreationSystem.define_disposal_metadata_on_spells(...)` matches
    configured disposal method names against class-bound spell profiles and
    writes those fields onto each spell. After that, runtime registration paths
    (`Conduit._register_to_creations(...)` and Phase 12 registration helpers)
    pass the spell’s disposal metadata into `Creations.add_creation(...)`,
    `add_many_creations(...)`, or `register_spellspace_creation(...)`, where
    it is copied into the `Creation` shell and later read back by cleanup and
    extract/restore flows.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:343-344
  - src/melder/aether/spellbook/spellbook_creation_system.py:521-550
  - src/melder/aether/conduit/conduit.py:1055-1059
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1409-1474
  - src/melder/aether/conduit/creations/creations.py:192-214
  - src/melder/aether/conduit/creations/creations.py:307-352
  IMPACT: This means the wrapper is not just random baggage. Right now it is
    the per-live-instance carrier for spell-derived disposal metadata used by
    disposal stacks and transfer extract/restore. Removing the wrapper would
    force a wider redesign of how `Creations` stores per-instance cleanup
    metadata.
  NEXT: explain to the user that the safer simplification is to shrink the
    wrapper (dead `_id`, dead `repr`, likely dead `_lock`) rather than delete
    it outright before the disposal/extract/restore model is redesigned.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T21:35:34Z
  TYPE: FACT
  CLAIM: `Spellbook._spell_id_pool` is already the shared union
    `spell_id -> Spell` map for both owned and contracted spells. Owned spell
    registration writes both `_spells_by_id` and `_spell_id_pool`, and
    contracted registration writes both the per-conduit
    `_contracted_spells_by_id[conduit_id]` map and `_spell_id_pool`. Update
    and unregister paths mirror both maps as well. Because
    `Meld._resolve_spell_by_id(...)` checks `_spell_id_pool` first, the
    conduit-local `_spell_id_resolution_cache` is mostly memoizing a lookup
    over an already-maintained shared map rather than adding new truth.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:231-239
  - src/melder/aether/spellbook/spellbook.py:595-612
  - src/melder/aether/spellbook/spellbook.py:666-677
  - src/melder/aether/spellbook/spellbook.py:766-797
  - src/melder/aether/spellbook/spellbook.py:866-877
  - src/melder/aether/spellbook/spellbook.py:906-934
  - src/melder/aether/conduit/meld/meld.py:1646-1659
  IMPACT: For direct `spell_id` resolution, the current per-`Meld`
    `_spell_id_resolution_cache` looks close to redundant. If we simplify this
    layer later, the better direction is to lean on `Spellbook._spell_id_pool`
    directly and focus caching effort on the more expensive logical lookup
    path.
  NEXT: answer the user directly that, yes, `spell_id_pool` is already doing
    most of the work and the extra conduit-local cache is probably one of the
    weakest caches in the stack.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-25T15:54:45Z
  TYPE: FACT
  CLAIM: The broad claim that `SpellSystemStates._lock` “does nothing” is not
    supported by the current source. The registry lock is protecting real
    multi-structure coherence across `_states_by_index_id`,
    `_states_by_spell_id`, `_dirty_indexes`, `_local_topologies`,
    `_resolution_by_conduit_id`, and the spellbook-scoped collection/contract
    reverse indexes. It is also the gate around creation of shared
    `ConduitResolutionState` buckets. That said, it is still a plausible
    bottleneck because some important paths take the coarse registry lock and
    then do global or semi-global work under it, especially Phase-3 dependency
    publication and the frame-wide adjacency snapshot builder.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:45-132
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:453-511
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:697-737
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:930-1029
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1159-1240
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1243-1285
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_adjacency_builder.py:67-97
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:46-110
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:182-260
  IMPACT: The better diagnosis is “coarse lock plus global scans may be a
    bottleneck,” not “the lock does nothing.” Any optimization should preserve
    correctness for the multi-map mutation paths while targeting lock-free or
    narrower-lock read paths and adjacency-build snapshots.
  NEXT: if we want to optimize this area, classify the methods into
    (1) multi-map writes that really need the coarse lock, (2) getters that
    may be over-locked, and (3) global scans like `SpellSystemAdjacencyBuilder.build(...)`
    that may need snapshotting or sharding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the source-backed audit of the proposed performance roadmap. The
goal is to classify the strongest claims before anyone starts implementing them.

