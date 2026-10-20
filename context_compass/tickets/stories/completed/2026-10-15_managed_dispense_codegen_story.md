# Story: managed_dispense_codegen - leases through emitted plans, doors and Conduit.managed_spell_meld

- Completed: 2026-10-15T18:15:07Z
- Summary: landed 0.2.8245 - meld and injection lease from the managed pools through the emitted plans (leasing and
  fresh managed sites, the inline pop, the reserve-first miss with recorded children, the widened F9 return), the
  door rows on the many templates, the per-path predicates, the solo decline, the manifest key, the specializer
  decline and `Conduit.managed_spell_meld`. Whole tree green in both GIL modes; every non-managed emitted plan
  byte-identical. Release-note section "`Existence.managed_spell_quantity`: objects leased from a root-owned pool
  and released back" extended.

## Metadata
- Story ID: STORY-2026-10-15-managed_dispense_codegen
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/2026-10-14_managed_spell_quantity_epic.md); story 5 of 7
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T09:29:51Z
- Updated: 2026-10-15T18:15:07Z

## User Narrative
As an agent, I want a meld of a managed spell, or of anything that injects one, to lease a pooled object through the
compiled plan, so that reuse costs a deque pop on the warm path.

## Value / MRP Alignment
The dispense is where the member pays off: an inline pop on the warm path, a reserve-first miss on the cold one,
children recorded with the object, overrides that take no lease, and the failed-construction return - while every
non-managed executor stays byte-identical.

## Ticket Contract
- ENTRY_GATE: S4 closed;
  system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_dispense_codegen.md and
  system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_dispense_codegen.md
  written and linked; U7 and U8 answered from source; a baseline emission capture taken; the mapping note recorded.
- EXECUTION_BOUNDARY: the occurrence instance processor and graph analyzer predicates, the phase 10 solo discovery,
  the generalized manifest (and many_only if its whitelist needs it), site_plan_lowering.py,
  creation_runtime_door_compiler.py, the generalized hydrator (specializer), the planner/compiler existence branches
  found for U8, src/melder/aether/conduit/conduit.py (`managed_spell_meld`),
  src/melder/utilities/caching_system/caching_system.py; their tests.
- DEPENDENCIES: S1-S4.
- EXIT_GATE: its tests green under `-X gil=0` and `-X gil=1`; the touched modules' existing suites green; one notch
  taken from `__version__` at landing with the running release note's managed section extended; the epic's Build
  Specification updated with what this story settled; story closed (completed folder, board sync)
- FAILURE_ESCALATION: DECISION_REQUEST if a change would alter an existing member's behaviour, an existing spell id or
  record, or the frame -> conduit -> Book lock order; CONFLICT when the source contradicts the epic's Build
  Specification (fix the spec first); BLOCKER when a gate cannot be met

## Requirements (Functional)
- B6 (S5 part) and B7 as written: per-path managed sites, solo declines, the managed site kind, the miss, children
  into the object's record, the failed-construction return, overrides, the door, the specializer decline (cache
  generation 21 dropped by the DECISION note of 2026-10-15T16:18:21Z).
- `Conduit.managed_spell_meld(spell=None, *, spell_id=None, spellframe=None, binding_name=None, override=None)` -> a
  ManagedSpellLease on the melded spell's pool.

## Requirements (Non-Functional)
- Every non-managed emitted executor byte-identical (emission diff gate).
- Warm lease cycle well under 1 us inside a plan (measured).

## Scope Boundaries
- In scope: everything that compiles or runs a lease.
- Out of scope: transfer (S6), docs (S7).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes, the whole tree green in
  both modes, the emission gate identical and the warm cycle measured; notched 0.2.8245 (delegated routine closure
  under the owner's go-ahead).
- prior: ready -> in_progress (2026-10-15T15:47:49Z): S4 landed and closed (0.2.8244); S5 started with the baseline
  and U7/U8.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S4 lands.

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity Build Specification B6, B7; the codegen FACT note of this epic (2026-10-15).

## Tasks (Implementation Checklist)
- [x] Capture the baseline emission over the certification harness worlds before any edit.
- [x] Read the U7/U8 sites whole; component and code-description patches; mapping note.
- [x] Red tests: lowering shapes, component dispense tests, integration tests.
- [x] Implement; emission diff; green in both GIL modes; the spellbook, conduit and codegen suites.
- [x] Notch, release note, epic spec update, close, board sync.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Direct meld reuses: a release then a meld returns the same object (elastic).
- Injection leases into many and unique holders; overrides behave as B7; a raising consumer returns its lease; a trim
  disposes the object and its recorded children.
- The emission diff shows only managed shapes added.

## Validation / Test Plan
- test_site_plan_lowering.py additions;
  tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py;
  tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py; both GIL modes; the emission
  diff log.

## UX / API / Data Notes
- Public: `Conduit.managed_spell_meld`.

## Risks / Mitigations
- A planner branch assumes two kinds of existence (shared or many) -> U8 reads every branch first.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No `src/` edit before the component patch and the mapping note exist.

## Open Questions
- None. U7 and U8 answered (DECISION note 2026-10-15T15:50:36Z, FACT note 2026-10-15T16:06:32Z); the pre-conjure
  staging gap (FACT note 2026-10-15T16:18:21Z) goes to S6 and the owner.

## Decision Log
- 2026-10-15 (melder_0): per-path sites; F9 return kept; own-parameter overrides unpooled (epic Decision Log).
- 2026-10-15 (melder_0): the dispense design (DECISION note 2026-10-15T16:18:21Z) - door rows on the many
  templates, no cache generation 21, F9 widened to any failure before the consumer exists and to a lost race,
  one consumer per leasing site; `managed_spell_meld` gives a fresh own-override object to the pool on release
  (epic Decision Log, open to the owner's review).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_dispense_codegen.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_dispense_codegen.md
  - artifacts/managed_spell_quantity_20261015/ (this story's runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: patch docs promoted and archived at S7; artifacts retained

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - dispensing managed objects through emitted plans
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, design, implementation and tests of this story;
  created 2026-10-15T09:29:51Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-15T09:29:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened ready behind S4. The seams are read (epic FACT note of 2026-10-15): the lowering 731-1666, the
    predicates 112-118 / 733-737, solo discovery 52-81, the door compiler 1-1229.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:731-1666
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-883
  IMPACT: Sets the first step: the baseline emission capture.
  NEXT: Start after S4 closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T15:47:49Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S5 started on 0.2.8244. The before-image is kept verbatim: the files this story may change (the lowering,
    the door compiler, the override runtime and resolver, the generalized hydrator, manifest and no-overrides
    compiler, the many_only manifest, solo discovery, the two `_is_shared_existence` strategies, the lane plan,
    shared_compiler_executions, caching_system, conduit.py, meld.py; 16 files) copied to baseline_0_2_8244/ with
    SHA256SUMS, so the emission diff loads the old modules beside the new ones (the D4/D5 probe's method). Order: read
    the seams whole (U7, U8), record them, write the S5 patches and the mapping note, capture the baseline emission over
    representative shapes and the certification harness worlds, red tests, implement, emission diff, green.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/baseline_0_2_8244/SHA256SUMS.txt:1-16
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/probes/emission_diff_d45.py:1-137
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:284-314
  IMPACT: The byte-identity gate can be checked against a fixed before-image whatever the edit order.
  NEXT: Read site_plan_lowering.py whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T15:49:48Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: site_plan_lowering.py read whole on 0.2.8244. `SitePlanLowering.emit` keeps the demanded steps (a parameter
    with a winning key demands nothing, so a managed site feeding an overridden parameter is never emitted) and hands
    them to `SitePlanEmission`, which classifies each step shared or not by one list, `_shared = [existence is not
    many]` - a managed step would fall into "shared" today and hit `_route`'s RuntimeError. `_place` homes the root
    and every shared site with a winning key at top level and every other step at the lowest context common to its
    consumers (a shared consumer's context is its own `_miss{i}`), then computes each miss's outer values.
    `_emit_context` emits a context's children: shared -> `_emit_shared_hit` (store route or the S9 owner-store
    constant `c{i}`, `v = c._creations.get(sid)`, P2 when pinned, `_miss{i}` call) and `_emit_miss` (unresolved
    check, children first, then the guard - none for a door-held root - recheck, construction, publication through
    `add_creation` or the dict write, `adopt_children` for its disposal-bearing many children); many ->
    `_emit_many` (construction, then `<store>.register_many(sid, v, dm)` where store is `many_store` at top level
    and `c{i}` in a miss). `_emit_construct` emits a direct call wrapped in `try/except Exception ->
    _raise_meld_construction_error`, or the generic helper with a dict literal, or the supplied-values helper on a
    masked copy. Normal mode drops `ov` everywhere; `_owner_store_constant` is the S9 rule (unique, automatic
    owner, owner store set).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:568-728
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:880-958
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1117-1234
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1513
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1516-1666
  IMPACT: The managed site is a third kind beside shared and many: placed like shared (its own miss, so its children
    build only on a miss) with a pop-or-miss hit; its miss reserves, builds children into a local `kids{i}` list
    instead of `register_many`, constructs, and `abandon`s on failure / `adopt`s on success; with its own winning keys
    it constructs fresh like a many step. Its consumer's construction (and any lease after the first) needs the F9
    put-back on failure. Every non-managed path stays as emitted today if the new kind only adds branches.
  NEXT: Read creation_runtime_door_compiler.py whole (U7: the hooks lane's `created` flag).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T15:50:36Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The door compiler read whole and U7 answered. Doors are template factories compiled once at import, one per
    (route, lane, fast bit): `_build_no_overrides_lines` / `_build_with_overrides_lines` emit each route's body and
    the four `_..._TEMPLATE_BY_ROUTE[...]` tables select them; an unknown route raises "Unsupported CreationContext
    ... route key". The `many` route only calls the plan (`instance = _no_overrides_executor(meld)`, created True;
    with overrides `_execute_with_overrides(meld, overrides)`), and its fast and non-fast bodies are the same lines.
    U7: the hooks lane's `created` flag gates the spell's activation hooks and the `on_meld_activation` meld hook
    (ConduitMeld and SpellSpaceMeld run them only when `created` is True). DECISION: the `managed` route gets the
    `many` bodies under its own route key and source names, so `created` is True on every lease - a lease hands the
    object to a new holder after its resets, so activation hooks run for reused objects too; telling a pop from a
    build would need the plan to report it on the warm path. Template sources are module-level strings compiled by
    `get_or_compile_executor_code`, so adding a route adds entries and changes no existing template's source.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:7-191
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:279-495
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-883
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:1160-1229
  - src/melder/aether/conduit/meld/conduit_meld.py:687-726
  IMPACT: B7's door line is settled (U7 closed): eight new template objects (four lanes x fast bit share the many
    bodies) and table rows for "managed"; no existing template changes.
  NEXT: Read the two `_is_shared_existence` strategies, solo discovery, the generalized manifest and the hydrator.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T16:06:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U8 answered from source (re-read after the compaction). Two predicates decide sharedness by `existence is
    not many`: the instance processor's `_is_shared_existence` (one `(spell_id, None)` key and a canonical occurrence
    per shared spell) and the occurrence analyzer's (collapses a shared spell's occurrences during the walk); both
    must answer False for managed so a managed spell gets one instance key per path. Phase 10: solo claims any model
    with one visible spell and no collection socket, whatever its existence; many_only needs every visible spell
    many, so it never claims a managed model; generalized takes the rest. The generalized manifest's route-key
    whitelist names six families and raises for "managed". The lane plan's other existence branches are metadata the
    site plan never reads: `_build_fast_transient_plan` returns None unless every step is many (a managed root gets
    the non-fast door), `_creation_target_for_existence` falls to OWNER, the lock hint is "creations_lock",
    `_should_register` is True; `SitePlanStep.from_generalized_row` keeps only the existence and the spell-lock hint.
    The phase-11 signature row hashes the existence name. `_register_spell_instance_prebound` raises for any other
    existence, and only the straight-line specializer reaches it (the manifest no-overrides compiler's namespace; the
    hydrator imports only its builder, its two row predicates and the root-key resolver); its capture set is `unique`
    rows and its many-feeds-holder decline does not see managed rows.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:112-119
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:131-203
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:732-737
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:777-916
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py:52-81
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py:52-95
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:72-91
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2463-2660
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2661-2706
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:168-191
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1062-1110
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:400-457
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:59-78
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1123-1207
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:270-362
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:558-645
  IMPACT: S5's edits outside the lowering and the doors: both predicates return False for managed; solo discovery
    declines a model whose existence counts hold managed; the manifest whitelist gains "managed"; a pure row
    predicate beside `rows_feed_many_into_non_many_step` makes `_install_specializing_door` keep the plain door for
    a graph with a managed row. Nothing else in phases 9-11 branches on two kinds of existence, and rows map the
    existence by name, so managed rows hydrate unchanged; existing models take none of the new branches.
  NEXT: Read override_key_resolver.py whole (how winning keys cut a managed site), then the pool's
    reserve/abandon/adopt.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T16:18:21Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: A version staged with `bind_inactive` before conjure is never given an owner. `bind_inactive` needs a
    dynamic posture (so only dynamic worlds hold such versions), conjure's `define_conduit_into_spells` stamps only
    the Book's active spells, and a notch promotes the member through `_reactivate_owned_spell`, which stamps
    nothing - although the bind_inactive comment says pre-conjure inactive spells are wired at conjure. Probed on
    0.2.8244 (dynamic; unique, unique_per_conduit and many): after conjure and a notch the promoted version's owner
    store is None and its first meld raises RuntimeError "Spell has no configured CreationContextFactory." for
    every existence. Pre-existing and not managed-specific; a managed version promoted that way has no pool.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_parked_notch_owner.py:1-55
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_probe_parked_notch_owner_gil1.txt:1-20
  - src/melder/aether/spellbook/spellbook_creation_system.py:1331-1382
  - src/melder/aether/spellbook/spellbook.py:1563-1621
  - src/melder/aether/spellbook/spellbook.py:3826-3966
  - src/melder/aether/spellbook/spellbook.py:5276-5306
  IMPACT: S5 cannot make such a version meld (its context never builds) and does not try. The per-creation pool read
    of a managed site raises a named error instead of AttributeError or KeyError when a consumer's managed dependency
    has no owner store or no pool (a torn-down root's store reads the same way). The structural fix - stamp the
    promoted member at notch with the Book's live conduit, which would also re-point members a transfer migrated
    (U9) - changes behaviour for every existence, so it goes with S6's notch work and to the owner, not into S5.
  NEXT: Record the dispense design as a DECISION, then write the S5 component and code-description patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T16:18:21Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: S5's dispense design, from the U7/U8 reads, the override runtime and resolver and the pool's API.
    (1) Door: route "managed" maps onto the existing `many` template objects in the four route tables - the same
    bodies (`created` True, U7), no new module-level template globals (the synaptic module-scope rule) and no new
    compiled template; this replaces the U7 note's "eight new template objects". (2) Sites: a third kind in
    SitePlanEmission. A leasing managed site (no winning key on its own parameters) has its own `_miss{i}` like a
    shared site and one consumer (per path); a managed site with winning keys on its own parameters is "fresh",
    constructed like a many step and never pooled, counted, registered or adopted. (3) Hit: `h{i}` (the pool) and
    `pp{i}` (its `_idle.pop`) bound as plan constants under S9's rule (automatic owner, owner store set) when the
    pool is present at emission - `_idle` is assigned once and drained, never swapped; otherwise per creation
    `h{i} = spells[i]._owner_creations._managed_quantities[sid{i}]`, whose AttributeError or KeyError becomes a
    named error. Then `try: v = pop() except IndexError: v = _miss(...)`. (4) Placement: each lease is emitted
    right before its one consumer's construction region - for a shared or managed consumer at the end of its miss's
    children, before the guard - so nothing but that consumer's other leases runs between a lease and its use.
    (5) Return (F9, widened to any failure before the consumer exists): from the first lease through the consumer's
    construction (for a shared consumer also its guard, recheck and publication) is one try; an exception puts back
    every lease taken for it (failures become notes on the exception) and re-raises; a shared consumer that loses
    its cold race puts back its unused leases (failures raised as one ExceptionGroup after all were tried).
    (6) Miss: unresolved check, `reserve()` (an object served returns at once), `kids` when disposal-bearing many
    children live inside, then `try:` children, leases and construction `except BaseException: abandon(kids, exc);
    raise`, then `adopt` when kids exist; many children there append `(v, dm)` to `kids`, not `register_many`.
    (7) No cache generation 21: rows and manifests of existing spells do not change, plans are emitted at hydration,
    and every notch already makes the cache cold (generation 9 compares the stamped release with `__version__`);
    the epic's B7 line is corrected. (8) `Conduit.managed_spell_meld`: resolve the target (`Meld._resolve_spell`),
    refuse a non-managed spell before melding, meld it by id, return `ManagedSpellLease(obj, pool)` on its owner
    store's pool.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:56-97
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:1162-1229
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1117-1234
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1513
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:337-405
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/override_key_resolver.py:145-204
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:432-547
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:548-606
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:623-703
  - src/melder/utilities/general_base/abstract_elastic_pool.py:147-250
  - src/melder/utilities/caching_system/caching_system.py:765-857
  - src/melder/aether/conduit/meld/meld.py:1839-1921
  - src/melder/aether/conduit/creations/managed_spell_lease.py:61-77
  IMPACT: Non-managed shapes keep their emission: every new branch keys on a managed step, and the door tables only
    gain rows. Limited and queue pools cannot lose a place to a failed meld or a lost race. The patches restate this
    as the contract the red tests check.
  NEXT: Write component_patch_managed_dispense_codegen.md and code_description_patch_managed_dispense_codegen.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T16:25:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch gate met: component_patch_managed_dispense_codegen.md and
    code_description_patch_managed_dispense_codegen.md written and linked, the architecture patch aligned (no
    generation 21, door rows on the many templates, invariant 11 widened), the emission before-image captured
    (s5_emission_before_0_2_8244.json.gz: 4461 entries - 4414 lowering shapes, 42 door bodies, the five harness
    worlds; two runs identical). Mapping, patch section -> implementation ->
    validation: (1) Sharedness -> both `_is_shared_existence` -> unit: per-path keys and occurrences for managed.
    (2) Discovery -> solo `discover` declines managed counts -> unit: solo declines, generalized claims. (3) Manifest ->
    `_resolve_route_key_from_model` + "managed" -> unit. (4) Door -> "managed" rows on the many templates -> unit:
    selectors return the many templates; component: hooks see created=True. (5) Specializer ->
    `rows_contain_managed_step` + `_install_specializing_door` decline -> unit. (6) Leasing/fresh site, hit, miss,
    placement, return, children (code-description control flow) -> SitePlanEmission (`__init__`, `_place`,
    `_unresolved_check_lines`, `_emit_context`, `_emit_many`, `_emit_miss`, new managed hit/miss/lease-group
    emitters, `_managed_pool_constant`) and three SitePlanRuntimeHelpers -> unit: emitted shapes and runtime on real
    pools (pop, reserve, served, abandon with notes, adopt, F9 and lost-race returns, missing pool). (7)
    `Conduit.managed_spell_meld` -> conduit.py after `meld` -> component. (8) Gate -> the capture rerun equal for
    every non-managed entry. (9) Benchmark -> the warm lease cycle in a plan.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_dispense_codegen.md:1-89
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_dispense_codegen.md:1-107
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:30-108
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s5_emission_capture.py:1-265
  IMPACT: S5 may edit src/ now; any change outside the mapped seams goes back through the patches first.
  NEXT: Write the red unit tests in test_site_plan_lowering.py and the discovery, predicate, manifest, door and
    specializer tests; run them red in both GIL modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T16:52:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red tests written (re-onboarded after the 16:26Z compaction). test_site_plan_lowering_managed.py (51 tests,
    a separate module beside test_site_plan_door_held_root.py, as the door-held work did, with a store that holds
    real ManagedSpellQuantity pools): emitted shapes (constant and per-creation pools, helper binding, lease
    placement, the two-consumer refusal, `ov` through the miss), the root lease (build, reuse, exhaustion, torn-down
    pool, a served object, a queue wait), F9 (many, shared, managed, door-held and unique holders; sibling failure and
    exhaustion; notes; lost race and its ExceptionGroup; the pinned refusal), children (recorded, abandoned, notes),
    overrides (no lease, fresh builds, deeper keys), unresolved inputs, collections and the three helpers:
    49 failed, 2 passed (the no-managed and supplied-parameter guards) under -X gil=1 and -X gil=0.
    test_managed_dispense_seams.py (predicates for every member, route key, door rows, the row predicate): collection
    error (`rows_contain_managed_step` missing). Discovery core +3 (solo decline red; solo other-member and many_only
    guards pass); specializer wrapper +1 (red: the wrapper installs over a managed row).
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py:1-880
  - tests/unit/melder/spellbook/spell_compiler/test_managed_dispense_seams.py:1-101
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_red_lowering_gil1.txt:1-200
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_red_seams_gil1.txt:1-80
  IMPACT: The contract of the code-description patch is executable; implementation starts in mapping order.
  NEXT: Implement the seams (predicates, solo, manifest, door rows, row predicate and decline), then SitePlanEmission.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T17:04:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S5 src implemented in mapping order. Seams: both `_is_shared_existence` answer False for managed; solo
    `discover` declines a model whose existence counts hold managed; the manifest whitelist takes "managed"; the four
    door tables map "managed" (both fast bits) onto the non-fast many templates; `rows_contain_managed_step` and the
    specializer's decline. Lowering: SitePlanEmission classifies shared / many / leasing / fresh in `__init__` and
    binds the three helpers only when a site leases; `_place` uses `_has_miss`, refuses a leasing site without
    exactly one consumer and fills `_leases_by_consumer`; `_emit_context` skips non-root leasing sites (their
    consumer's lease group emits them) and passes `kids{i}` into a leasing miss; `_emit_many` wraps its
    construction in `_emit_leased_region`, records nothing for a fresh site and appends kids in a leasing miss;
    `_emit_miss` builds its body locally and, with leases, runs the guard block inside the group (return from
    inside, `_return_unused_leases` after); new `_emit_leasing_miss`, `_emit_lease`, `_emit_root_lease`,
    `_emit_pool_read`, `_bind_lease_pool`, `_managed_pool_constant`, `_lease_pairs`; SitePlanRuntimeHelpers
    `return_leases`, `return_unused_leases`, `raise_missing_managed_pool`. `Conduit.managed_spell_meld` resolves
    as meld does, refuses non-managed targets, reads the pool first (missing-pool error), melds by id and returns the
    lease. Emitted shapes match the code-description patch (printed for a dynamic shared consumer, a managed root
    with a disposal-bearing child and two leases into one holder). Test fix, not prod: MeldExecutionError's str()
    prefixes "[MELD] Execution failed for spell ...", so the helper test checks containment.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:454-571
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1041-1142
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1348-1540
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1541-1631
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1681-1968
  - src/melder/aether/conduit/conduit.py:5067-5180
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s5_apply_seams.py:1-233
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s5_apply_lowering.py:1-27
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s5_end_to_end.py:1-71
  IMPACT: Green under both GIL modes: the 51 lowering tests, the seams, discovery and specializer files, and the
    whole shared_assets unit folder (223 passed). The probe melds a managed spell directly, reuses a released object
    and injects leases into many and unique holders on a real automatic root.
  NEXT: Component tests (direct meld, holders, overrides, F9, trims, hooks created=True, managed_spell_meld), then
    integration tests, the emission diff and the full tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T17:18:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S5 green under -X gil=1 and -X gil=0 (re-onboarded after the 17:05Z compaction). Component
    (test_conduit_component_managed_spell_quantity.py, 23 passed): direct reuse, by name and by id, many and unique
    holders, a released object injected into the next holder, the limited refusal and the queue wait and timeout
    through meld, the F9 return of a failed holder, both override kinds, a trim disposing the object and its recorded
    children, activation hooks on every lease, managed_spell_meld (with, a raising block, without with, by id, the two
    refusals, exhaustion), lessers and spellspaces leasing from the root's pool, root teardown and the dynamic
    per-creation read. Integration (test_conduit_integration_managed_spell_quantity.py, 7 passed): roots in two frames
    and two binding names in one root keep their own pools (a release by class alone is ambiguous across roots), a
    post-conjure bind in a dynamic world, a notch to a version staged after conjure (the old pool keeps its idle
    object), a borrower leasing from the owner's pool through link and contract, a lesser's managed_spell_meld, and a
    crystallizer restore dispensing from an empty pool. Unit (the shared_assets folder, the seams, discovery and
    specializer files): 223 passed. One test fix, not prod: the lesser test read `pool.out_count`, which is a
    `describe()` key, not an attribute.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py:1-491
  - tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py:1-282
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:790-834
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_green_component_gil1.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_green_component_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_green_integration_gil1.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_green_integration_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_green_unit_gil1.txt:1-5
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_green_unit_gil0.txt:1-5
  IMPACT: Every S5 acceptance criterion except the emission diff is shown on real worlds, and both pool reads dispense:
    the plan constant on automatic roots and the per-creation read on dynamic roots, borrowers and notched versions.
  NEXT: Rerun s5_emission_capture.py on the working tree and diff it against the 0.2.8244 before-image.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T17:20:19Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The emission gate holds: s5_emission_capture.py rerun on the working tree (S5 applied, -X gil=1) gives the same
    4461 entries as the 0.2.8244 before-image, every value equal - 3456 t1, 750 t2, 120 t3, 72 t4 and 16 t5 lowering
    shapes (every non-managed existence mix, store routes, the S9 constant, door-held roots, override key sets,
    collections, positional payloads, generic and unresolved steps), the 42 door bodies of the seven existing routes
    and the normal plans of the five certification harness worlds; the 30 entries that record an emission error carry
    the same error text before and after. No non-managed emitted source or namespace changed.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s5_emission_capture.py:1-265
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_emission_diff.txt:1-7
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_emission_before_0_2_8244.json.gz:1-1
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_emission_after_working_tree.json.gz:1-1
  IMPACT: The story's byte-identity requirement and the epic's EXIT_GATE emission check are met for S5; the managed
    branches add shapes without touching existing ones.
  NEXT: Run the full tree in both GIL modes in shards (unit, component, integration, crystallizer and experiment ids).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T18:09:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The whole tree is green with S5 under -X gil=0 and -X gil=1, with the same skip/xfail/xpass counts as the S4
    baseline plus the new tests: unit aether+spellbook 6951 passed; unit rest 2508 passed, 3 skipped, 7 xfailed;
    component 2387 passed, 23 skipped, 1 xfailed (S4 2364 + the 23 new); integration 2125 passed, 9 xfailed, 2
    xpassed, 2 skipped (S4 2118 + the 7 new; crystallizer, multithreading and live_sim included); experimentation,
    experiments and tests/tests 250 passed, 4 skipped. Warm cycles (200,000 x 7 rounds, the same in both modes, median):
    a managed meld plus its release 320 ns on an automatic root (plan-constant pool read) and 742 ns on a dynamic root
    (per-creation read); a `many` holder whose constructor leases one object, plus the release, 366-372 ns. References
    on the same tree: a `many` meld 214-217 ns, a `unique` meld 167-171 ns, a `many` holder of a `many` 267-274 ns, a
    dynamic `many` meld 611-623 ns. A cycle is about one bound release (~120 ns, S4) above the matching `many` shape,
    and every run left one object in the pool (count 1, idle 1).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s5_validation_index.md:1-51
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s5_validation_index.py:1-67
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s5_warm_lease_cycle.py:1-165
  IMPACT: S5's exit tests and its performance requirement (a warm cycle well under 1 us) are met. The existing shapes'
    before/after A/B stays with the epic's benchmark task at S7; baseline_0_2_8244/ rebuilds the before tree, and
    the emission diff already shows their plans unchanged.
  NEXT: Notch 0.2.8245, extend the release note's managed section, update the epic, close the story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S5 - leases through emitted plans and doors; `Conduit.managed_spell_meld`.
- State: done; landed 0.2.8245 (the FACT, DECISION and MEASURE notes; runs/s5_validation_index.md; the emission diff
  identical over 4461 entries).
- Open for the owner's review: `managed_spell_meld` with own-parameter overrides gives the fresh object to the pool on
  release (epic Decision Log); the pre-conjure staging gap (FACT note 2026-10-15T16:18:21Z) goes to S6 and the owner.
- Next: S6 (STORY-2026-10-15-managed_ownership_transfer) - pools through move, no move, rollback and notch (U9).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
