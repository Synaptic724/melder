# Task: Dual instance-door slot - kill the per-warm-meld tuple allocation

## Metadata
- Task ID: TASK-2026-07-02-dual-instance-door-slot
- Story: none (successor to 2026-07-01 compiler lane; owner-approved 2026-07-02 "send it")
- Status: completed (2026-07-03: cut landed + user-validated on 3.14t; specializer
  moved to the instance lane; wrapper self-heal + deopt 3-strike re-pin landed and
  validated [deopt_many2 1.127->1.022]. OPEN POINTERS for a future lane: flag-ON
  gauntlet end-to-end number; owner decision on default-enabling
  generalized_singleton_specialization_enabled)
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-07-02T15:50:00Z
- Updated: 2026-07-02T15:50:00Z

## Objective
Every warm no-hooks meld currently calls the HOOKS-variant door, receives
`(instance, created)`, takes `[0]`, and discards the tuple - one heap allocation +
getitem per warm meld system-wide (shared-allocator pressure under nogil). The door
compiler ALREADY emits instance-only templates (`compile_creation_context_instance_
no_overrides_executor`, `(meld) -> Any`), compiled at module import and unused by
these lanes. Publish an instance-only no-overrides door as a SECOND CreationContext
slot and point the two hot lanes at it.

## Ticket Contract
- ENTRY_GATE: owner approved in chat 2026-07-02; this ticket + the inventory below
  are the resume root; slim onboarding per owner directive.
- EXECUTION_BOUNDARY: exactly the files inventoried below; all-or-nothing - the slot
  contract (creation_context.py:29-41) requires every publisher and both meld doors
  to move in ONE change.
- DEPENDENCIES: compiler-lane ticket 2026-07-01 (evidence notes 2026-07-02T15:30);
  fast-meld-door component suite as the regression bar.
- EXIT_GATE: all publishers publish both doors; both meld doors' no-hooks lanes call
  the instance door (no tuple); component + specialization suites green; user-run
  3.14t probe/gauntlet pair recorded.
- FAILURE_ESCALATION: if any publisher cannot supply the instance door cheaply,
  DECISION_REQUEST before shipping a partial slot.

## COMPLETE PUBLISHER/CONSUMER INVENTORY (read-verified 2026-07-02)
Slot definition:
- src/melder/aether/conduit/meld/creation_context/creation_context.py
  (__slots__, __init__, cleanup, load_cached, docstring door-facing contract :29-41)
Constructor funnel:
- creation_context/creation_context_builder.py:66 (single normal-construction site)
Cold publishes + hot swaps (each needs an instance-variant cold door + swap):
- strategies/generalized/hydration/generalized_hydrator.py:181,:192 (hot swap) +
  cold lazy-door publish + specializer swap (:604 region publishes resolved door)
- strategies/many_only/hydration/many_only_hydrator.py:146 (+ its cold door)
- strategies/solo/hydration/solo_hydrator.py:133 (+ its cold door)
- strategies/*/steps/*finalize_creation_context_step.py (eager/fallback builders)
Cache loaders:
- codegen_creation/spell_codegen_creation_cache.py:241-298 (compile instance door
  beside the hooks door; same inner executor)
- strategies/generalized/generalized_creation_cache.py:130,:180 (load_cached calls)
Consumers (switch to instance slot):
- conduit/meld/conduit_meld.py:235-245 (fast lane: read new slot, call WITHOUT [0])
  and :334-335 (non-dynamic no-overrides arm)
- conduit/meld/spell_space_meld.py (same two lanes - the slot contract names both
  doors; locate the mirrored reads)
- creation_context.py execute_no_hooks (:224/:248 - may use the instance door and
  drop its [0]s)
Door compiler (no change expected):
- shared_assets/creation_runtime_door_compiler.py:55-95 instance templates exist for
  every route; verify lineage/cluster instance variants are in the compiled matrix.

## Design Rules
- Additive slot (`_no_overrides_instance_executor`); the tuple door stays for the
  hooks lane; slots swap TOGETHER at every publish/swap site (cold->hot->specialized).
- Same self-replacing contract: readers re-read per call; nothing captures either
  executor.
- Both doors wrap the SAME inner executor object per stage - one hydration, two wraps.
- No defensive None fallbacks in the hot lanes: every publisher ships in this change.

## Validation
- Not run. Bar: fast-meld-door component suite + singleton-specialization component/
  integration suites + 45-test lane net + user-run probe (leaf/many absolutes, t5) +
  melder gauntlet pair.

## Notes
- DATETIME: 2026-07-02T15:50:00Z
  TYPE: PLAN
  CLAIM: Staged ready-to-execute with the full inventory above; deferred to a fresh
    window because this session (post-compaction, 7+ mount truncations, one stream
    death) cannot guarantee an uninterrupted all-or-nothing cross-component cut.
    Expected effect: one tuple alloc + getitem removed from EVERY warm no-hooks meld
    (fast lane AND normal lane), all families, both flag postures.
  EVIDENCE:
  - tickets/tasks/2026-07-01_compiler_phase8_11_generalized_call_savings_task.md:1-1
    (2026-07-02T15:30 inventory note)
  IMPACT: Highest remaining warm-path item, fully de-risked for cold-start execution.
  NEXT: Fresh session: slim onboard -> this ticket -> land in one window.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-07-02T16:40:00Z
  TYPE: FACT
  CLAIM: CUT LANDED IN FULL (owner overrode the deferral). Every inventory item
    executed: CreationContext slot + contract; builder (fail-fast + existing-creation
    instance closure); 3 hydrators (cold triples, hot swaps, containers) incl. the
    SPECIALIZER publishing a specialized instance twin; 3 lazy-door steps; 3 family
    caches (lazy+eager); 2 finalize steps (many_only flag mirrors its family rule);
    spell-level cache loader; ConduitMeld + SpellSpaceMeld fast lanes + no-hooks arms;
    execute_no_hooks. One mid-cut mount truncation (generalized hydrator) recovered
    from HEAD + full 11-pair replay. All touched files individually compiled +
    tail-verified; harness 24/24+9/9+4/4+2/2 green. compileall's conduit.py error =
    VM-replica rot on an UNTOUCHED file (user disk verified intact via file tool).
    3.14t: Not run.
  EVIDENCE:
  - system_docs/patches/active/generalized_singleton_specialization_2026_07_01/component_patch_generalized_codegen.md:1-1 (addendum 2026-07-02l)
  IMPACT: One tuple alloc + getitem gone from every warm no-hooks meld system-wide.
  NEXT: USER RUNS (requested): full unit tree (watch for direct HydratedExecutors
    constructions needing the new field + stub SpellCodegenCreation fail-fasts),
    fast-meld-door + specialization component suites, probe pair, melder gauntlet pair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-02T19:55:00Z
  TYPE: FACT
  CLAIM: 18-FAILURE FIX-UP COMPLETE (user-run --last-failed triage, 3 classes).
    (1) REAL REGRESSION: the specializing wrapper rode the HOOKS slot, which the
    no-hooks lanes no longer execute -> specialization silently dead (2 component
    install-detection failures). FIX: wrapper now rides the INSTANCE lane -
    generalized_hydrator.py `_install_specializing_door(plain_instance_door=...)`
    wraps the instance door; `_try_specialize_once` resolves the specialized
    INSTANCE door into resolved_cell and publishes BOTH slots on success
    (`_no_overrides_instance_executor`=specialized instance,
    `_no_overrides_executor`=specialized hooks); 3-attempt decline re-pins ONLY the
    instance slot (hooks already holds plain). Container now carries plain hooks
    door + final instance door. NOTE: post-compaction disk audit showed the earlier
    "rework landed" claim was HALF true - dual-publish was on disk but the lane move
    was not; completed now from disk truth, not from the summary.
    (2) cache-ASSET playground loader left the instance slot None -> TypeError in
    dynamic execute_no_hooks. FIX: `_load_no_overrides_executor_from_asset` returns
    a (tuple-door, instance-door) pair (legacy raw executor already returns the bare
    instance; the twin is a pass-through) and load_cached receives
    `no_overrides_instance_executor` (creation_context_cache_asset_playground.py).
    (3) 15 stub drifts: _CreationContextStub gains `_no_overrides_instance_executor`
    (test_meld.py, test_concrete_meld_subclasses.py); test_creation_context.py
    no-hooks test passes the instance kwarg; builder-test artifact stub gains the
    field (default valid so the existing missing-door raise messages hold) + NEW
    third case pinning the `no_overrides_instance_executor` fail-fast; wrapper unit
    test updated to the instance-lane contract (renamed kwarg, pin test asserts
    instance-slot publish + hooks slot untouched on decline).
  EVIDENCE:
  - src/.../generalized/hydration/generalized_hydrator.py:303-332,549-695
  - tests/experimentation/creation_context_cache_asset_playground.py:280-303,395-427
  - tests/unit/melder/spellbook/spell_compiler/test_generalized_specializer_wrapper.py:95-145,226-249
  IMPACT: Specialization live again end-to-end on the lanes that actually execute;
    dual-door contract now enforced by builder fail-fast test coverage.
  NEXT: MOUNT ROT (3 files pinned truncated in VM replica: hydrator@667,
    playground@732, wrapper-test@305 - HOST VERIFIED INTACT via file tools, do NOT
    "recover" them); harness verified on a /tmp shadow repo with known-good tails:
    24/24 + 9/9 + 4/4 + 2/2 green. USER RUNS: pytest tests --last-failed, then
    component fast-meld-door + specialization suites, probe pair, gauntlet pair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-02T21:45:00Z
  TYPE: FACT
  CLAIM: USER VALIDATION GREEN (full test run passes) + WRAPPER SELF-HEAL LANDED.
    User reported "all tests pass" post fix-up. Follow-up cut: a context REBUILT
    after specialization resolution re-swaps the hydrated container doors and
    re-installs the wrapper in its instance slot permanently (+1 call + cell read
    per warm meld on that context forever). FIX: the wrapper's resolved branch now
    re-publishes the final door(s) into the CURRENT published context before
    delegating (new `resolved_hooks_cell` carries the specialized hooks door
    beyond the attempt; decline-pin leaves the hooks slot untouched). Wrapper
    docstring steady-state contract updated to "self-erasing". New mechanism test:
    test_rebuilt_context_sheds_wrapper_after_resolution. Harness (3.10 shadow):
    24/24 + 10/10 + 4/4 + 2/2 green. 3.14t: Not run. User reported "seems a bit
    slower now" (no numbers) - probe pair + gauntlet pair requested; also staged
    the cache parity probe (see cache epic S1 note) since slowness may be the
    cache-on lane.
  EVIDENCE:
  - src/.../generalized/hydration/generalized_hydrator.py:600-719
  - tests/unit/melder/spellbook/spell_compiler/test_generalized_specializer_wrapper.py:239-277
  IMPACT: No context shape can retain the wrapper for more than one call after
    resolution; rebuilt-context warm melds return to direct-door cost.
  NEXT: user runs: pytest tests --last-failed (should be empty) or the wrapper
    file + component specialization suites; specialization probe pair; gauntlet
    pair; cache parity probe (both postures).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-02T22:35:00Z
  TYPE: MEASURE
  CLAIM: USER-RUN 3.14t VALIDATION GREEN + FIRST FLAG-ON EFFICACY NUMBERS WITH THE
    WRAPPER ACTUALLY EXECUTING (it was silently dead post-dual-cut until the
    instance-lane fix). Wrapper unit 10/10; component specialization 7/7; parity
    probe clean (see cache epic). Efficacy probe (iters=20000, threads=5), on/off:
    leaf 0.9767, many2 0.9637, many4 0.9611, many8 0.9306, cycle_meld1 0.9933,
    spellspace_cycle 1.0286, threads5_many8 0.8822 (contention thesis CONFIRMED:
    the win grows under threads), deopt_many2 1.1274 vs plain many2. The width
    scaling holds (0.96 -> 0.93 with capture count). NOTE the deopt lane: a
    permanently-deopted spell pays ~13% over plain FOREVER because the
    specialized body re-checks guards and falls back per call - candidate
    follow-up: 3-strike deopt re-pin of the plain doors (mirrors the install-side
    decline pin). Not landed - scope approval pending.
  EVIDENCE:
  - chat transcript 2026-07-02 (user-run pytest output, .venv_new 3.14t)
  IMPACT: Specialization is now a measured warm win everywhere it should be and
    flat where the route short-circuits; the dual-door + instance-lane wrapper
    stack is validated end-to-end on 3.14t. Owed: flag-ON GAUNTLET (end-to-end
    claim) and the owner call on default-enabling the flag.
  NEXT: gauntlet pair (also closes the cache epic); owner decisions: (a) deopt
    re-pin follow-up, (b) flag-ON default posture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-03T02:45:00Z
  TYPE: FACT
  CLAIM: DEOPT 3-STRIKE RE-PIN LANDED (owner-approved queue item; fixes the
    efficacy probe's deopt_many2=1.1274 permanent tax). Emitter: specialized
    body's guard-miss branches now tail-call the stable binding
    `_deopt_notify` instead of `_generic_inner` (source stays identity-free;
    ONE factory per shape - the binding resolves per spell).
    `build_specialized_no_overrides_executor` gains optional
    `deopt_notify` kwarg; default binds `_deopt_notify` to the generic inner
    (pre-change behavior). Hydrator: `_install_specializing_door` gains
    `plain_hooks_door` (threaded from hydrate_creation_executors) and builds
    `_deopt_notify` - counts misses, always delegates to the generic inner,
    and at >=3 misses re-pins BOTH published slots to the plain doors and
    resolves the wrapper cells to plain, so the specialized body (and its
    guard cost) leaves every lane permanently. Racy nogil counting benign
    (idempotent publishes). Tests: emission-contract source assertion ->
    `_deopt_notify`; manual-factory deopt test binds `_deopt_notify`; wrapper
    unit `_install` helper passes a hooks-door stub. Shadow harness: 24/24 +
    10/10 + 4/4 + 2/2 green. 3.14t: Not run.
  EVIDENCE:
  - src/.../compilers/generalized_manifest_no_overrides_compiler.py (emitter
    deopt target + kwarg + bindings)
  - src/.../hydration/generalized_hydrator.py (notify closure + threading)
  - tests/unit/.../test_generalized_emission_contracts.py,
    test_generalized_specializer_wrapper.py
  IMPACT: A permanently-invalidated capture graph now pays the deopt tax for
    exactly 3 melds, then returns to plain-door cost; healthy graphs pay
    nothing new (guard-pass path untouched).
  NEXT: user runs the two unit files + component specialization suite +
    efficacy probe (deopt_many2 should collapse toward ~1.00 as the re-pin
    replaces the specialized door with plain after strike 3).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-03T03:05:00Z
  TYPE: MEASURE
  CLAIM: DEOPT RE-PIN VALIDATED (user-run 3.14t): 34 unit + 7 component green;
    efficacy probe deopt_many2 1.1274 -> 1.0216 (permanent deopt tax removed,
    as designed). Noise caveat recorded: this probe run carries machine noise
    (flag-off threads5_many8 2775.7ns vs 1671.6 historical on identical code;
    leaf control 1.14 is by-construction noise - the wrapper never installs on
    the leaf lane, so ON==OFF physically). Stable signals consistent: many4
    0.9711 / many8 0.9437 wins hold; threads5 flag-ON absolute ~1450ns stable
    across runs.
  EVIDENCE:
  - chat transcript 2026-07-03 (user-run probe output)
  IMPACT: Specialization program complete: install (instance lane), success
    (dual publish), decline (3-attempt pin), rebuild (self-heal), permanent
    invalidation (3-strike deopt re-pin) - every terminal state now converges
    to the cheapest correct door. Still owed: flag-ON gauntlet + default-ON
    decision.
  NEXT: queue continues: scope-cycle runtime lane, overrides-lane audit.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
All reads done; design locked; execute top-to-bottom from the inventory. No code has
been changed for this task yet.
