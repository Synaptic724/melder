# Task: Certify S9/S11 in the harness, then emit site and store constants and live key objects

- Completed: 2026-10-04T00:13:33Z
- Summary: S9 landed at 0.2.8221: a unique site owned by an automatic conduit reads its owner store as a plan
  constant (no alias line; dynamic, unowned and meld.<store> sites unchanged; misses byte-identical;
  no generation bump); red on the tree's lowering, green with 4 unit + 3 component tests, every shard
  green on the landed copy; plan -7..-17% on roots with unique providers on the VM; S11 retired as
  already true; docs, graph, assets and bundles current; patch docs archived. Closed by the owner's
  directive; full-tree suites and gauntlet Not run.

## Metadata
- Task ID: TASK-2026-10-03-certify-and-implement-site-store-constants
- Story: STORY-2026-10-03-flat-warm-body-constants
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-03T21:31:58Z
- Updated: 2026-10-04T00:13:33Z

## Objective
The certification harness gains S9 (site Spell and, in automatic posture, owner-store namespace constants) and
S11 (live `spell_id` key objects) columns and measures them on the five shapes; when the table shows a win above
noise, the lowering stops emitting `cI = spells[i]._owner_creations` on the warm path (binding `sI` and, in
automatic posture, `cI` at hydration) and every plan namespace, cache-restored ones included, binds `sidI` to the
live Spell's `spell_id` object. Same objects, same errors; a dynamic transfer still repoints the read.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the owner's word (2026-10-03); the harness table BEFORE the patch
  docs; patch docs under `system_docs/patches/active/flat_warm_body_2026_10_03/` linked here with the mapping
  note BEFORE any src edit.
- EXECUTION_BOUNDARY: `tests/experimentation/codegen_strategy_certification.py`,
  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py`,
  `.../site_plan_override_runtime.py`, the hydrators under `.../strategies/*/hydration/` and the manifest cache
  loader (`manifest_creation_cache.py`) where the namespace is rebuilt, `caching_system.py` (generation), tests,
  the two canonical system documents and indexes, graph descriptors, release note, `__version__`.
- DEPENDENCIES: S8 (0.2.8217) and the matcher (0.2.8218) landed; the structural/executor cache (0.2.8220).
- EXIT_GATE: harness table recorded; red-to-green emitter unit tests; component tests in both postures (incl. a
  dynamic transfer and a cache full hit); the suites green on the VM copy (sharded); landed with notch, release
  note, docs, graph, assets and bundles with --check OK; owner-run suites requested.
- FAILURE_ESCALATION: DECISION_REQUEST if S9 is within noise on every shape; BLOCKER if the cache-restored
  namespace cannot carry live key objects without a manifest format change.

## Scope Boundaries
- In scope: the harness columns, the emitter and hydrator edits, the generation bump, tests, docs, notch, note.
- Out of scope: S2a (parked), S10, S12, the doors.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's word (2026-10-03T21:31:58Z).
- from_state: in_progress
- to_state: review
- transition_reason: Landed at 0.2.8221 with docs, graph, assets and bundles current (2026-10-04T00:02:11Z); the owner-run
  suites and gauntlet remain.
- from_state: review
- to_state: done
- transition_reason: Owner's turn-in directive (2026-10-04T00:13:33Z); notch 0.2.8221, note entry and rebuild
  recorded at landing.

## Steps / Checklist
- [x] Read the shared-site emission and the plan namespace in `site_plan_lowering.py` (render, _place,
      _emit_context, _emit_shared_hit, _emit_miss, the namespace build) and the hydrators' namespace binding on
      the live and cache-restored paths; verify in source whether an automatic-world path can repoint an owner
      store after hydration; one FACT note.
- [x] Harness: S9 and S11 transforms (and S9+S11), measured on the five shapes, interleaved; MEASURE note.
- [x] Patch docs and the mapping note (only when the table says ship).
- [x] Implement on the VM copy; emitter unit tests; component tests (both postures, transfer, full hit); shards.
- [x] Land on the tree (CRLF), notch above `__version__`, release-note section, docs, graph; patch docs promoted
      and archived; assets and LLM bundles LAST; both checks OK; post-landing shards.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The harness table with S9/S11; the emitter and hydrator changes; tests; docs; release-note entry; notch.

## Files / Paths Impacted
- tests/experimentation/codegen_strategy_certification.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/ (hydrators, manifest cache loader)
- src/melder/utilities/caching_system/caching_system.py
- tests/ (unit, component)
- context_compass/system_docs/patches/active/flat_warm_body_2026_10_03/
- release_docs/next_version_release.md, src/melder/__version__.py

## Validation
- Run on the VM (3.14.7t, GIL off): the lowering unit file and the component file (53 passed), six shards on
  the working copy and five on a fresh copy of the landed tree (all green; counts in `## Notes`), the harness
  on the shipped body (interleaved, run 1).
- Not run: the full-tree suites and the persistent gauntlet (owner-run).
- Recommended commands:
  - `python -X gil=0 tests/experimentation/codegen_strategy_certification.py`
  - `python -X gil=0 -m pytest tests/unit/melder/spellbook/spell_compiler tests/component/melder/aether/conduit -q`

## Risks / Rollback Notes
- A transfer in dynamic posture repoints the owner store -> the constant is emitted for automatic posture only.
- Rollback: re-emit the per-creation read; keep the generation bumped.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [x] No src edit before the harness verdict, the patch docs and the mapping note.
- [x] No perf claim from agent-side runs; ranking numbers are owner-run.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/flat_warm_body_20261003/ (harness runs, apply scripts, logs)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: patch docs promoted and archived at landing; artifacts kept.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - shared-site emission; plan namespace; hydration constants; key identity
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-03T21:31:58Z
  TYPE: PLAN
  CLAIM: Lane opened. Everything about the shared-site emission and the hydrators is UNKNOWN until read; the
    harness measures before any design is written down as a patch.
  EVIDENCE:
  - tickets/stories/2026-10-03_flat_warm_body_constants_story.md:1-40
  IMPACT: Reading order fixed: lowering first, hydrators second, harness third.
  NEXT: read the shared-site emission and the namespace build in `site_plan_lowering.py` whole (chunks).
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-03T21:40:58Z
  TYPE: FACT
  CLAIM: Emission and hydration read whole where the shared-site read lives. `SitePlanEmission.__init__` seeds the
    plan namespace (helpers, `root_spell_id`, `root_spell_name`, `spells` = the kept steps' live Spell objects);
    `_emit_shared_hit` emits, per shared site, `c{i} = <route>` then `v{i} = c{i}._creations.get(sid{i})` and the
    miss call `_miss{i}(meld, c{i}, v...)`; `_route` is `spells[i]._owner_creations` for `Existence.unique` and a
    `meld.<store>` attribute (or the cluster's resolved store) for the other shared existences; `sid{i}` is bound
    by `_bind` to `step.spell.spell_id` - the live Spell's attribute - in every plan, because plans are emitted at
    hydration from rows whose `spell` is resolved live (`_hydrate_steps_from_rows` + `SitePlanStep.
    from_generalized_row` / `from_many_only_row`; `_build_site_plan_runtime` -> `SitePlanOverrideRuntime` ->
    `SitePlanLowering.emit`). The manifest package persists rows only (`steps_rows`, `transient_schema`,
    `executor_signature`), never emitted plan source, so a lowering change retires no cached payload. Ownership:
    `define_conduit_into_spells` calls `Spell._add_owned_conduit(conduit._id, name, conduit._creations,
    dynamic_environment=conduit.__dynamic_environment__, ...)` for every owned spell at conjure, which sets
    `_owner_creations` and `_dynamic_environment` under the spell lock; the only other writer is the same method
    (ownership transfer, dynamic posture only). `_owner_creations` is initialised None and `_dynamic_environment`
    False before ownership. The test stub `_spell` in the lowering unit tests carries `_owner_creations` but no
    `_dynamic_environment`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:847-926
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1084-1120
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1443
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:93-220
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:269-425
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:39-130
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py:1-96
  - src/melder/aether/spellbook/spellbook_creation_system.py:1303-1382
  - src/melder/aether/spellbook/spell.py:1440-1470
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py:35-120
  IMPACT: S11 is already the case (the key object is the live `spell_id`); S9 applies to `unique` sites only (the
    other routes are one attribute read on the `meld` parameter) and can be gated per site on the provider's
    `_dynamic_environment`; no cache generation bump is needed for an emission-only change.
  NEXT: MEASURE note (harness and the interleaved A/B).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T21:40:58Z
  TYPE: MEASURE
  CLAIM: Harness extended with an S9 variant (drop every `c{i} = spells[i]._owner_creations` line, bind `c{i}` in
    the namespace) and an S11 identity report. Three sequential harness runs showed S9 at -10..-17% on every shape,
    but a sequential table penalises its first variant on this VM (worker plain 203 there vs 166 interleaved), so
    the shipped numbers are the interleaved A/B (plain vs S9 alternating 40k-call batches, 7 rounds, three runs,
    medians; VM load 1.1-2.2): worker (1 unique site) 166/160/159 -> 160/146/148 ns, -7%; context_root (5 unique
    sites) 326/308/316 -> 290/277/264, -11%; wide8_unique (8) 447/448/429 -> 374/374/366, -16%; wide8_existing (8)
    454/444/444 -> 370/367/368, -17%; chain8_transient (1 site over a many chain) 449/427/432 -> 437/428/419, -3%.
    Micro-benchmark on the same interpreter: the alias line costs 8 ns per site (37.1 -> 28.9 ns for one read
    group), matching ~8-10 ns per unique site in the plans. S11: every `sid{i}` constant IS the store's key object
    on every shape ("identical"), so there is nothing to ship. S2a (data only, parked): -30..-38% on the two
    existing-object shapes in the sequential table.
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_medians.md:1-8
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_run1.md:1-8
  - artifacts/flat_warm_body_20261003/logs/harness_s9_run1.md:1-60
  - artifacts/flat_warm_body_20261003/logs/micro_owner_store_read.md:1-6
  - artifacts/flat_warm_body_20261003/harness_s9.py:1-80
  IMPACT: S9 is above noise on every shape with unique providers and scales per site; it is the cheapest emitter
    change left (one line per site, no store change, no guard).
  NEXT: DECISION note, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T21:40:58Z
  TYPE: DECISION
  CLAIM: Ship S9 as: in `_emit_shared_hit`, a `unique` site whose provider Spell is owned by an automatic conduit
    (`not step.spell._dynamic_environment`) and has an owner store binds `c{i}` = `step.spell._owner_creations`
    in the plan namespace and emits no alias line; every other site (the `meld.<store>` routes, a dynamic
    provider, an unowned one) emits today's line. The miss keeps its `c{i}` parameter (the call passes the
    global). Rationale: the owner store of an owned spell changes only through `_add_owned_conduit`, which in a
    live world runs again only for ownership transfer (dynamic posture); a notch or late bind re-gates and
    recompiles the plan, which re-emits the constant. No generation bump: plans are emitted at hydration from
    rows. S11 is retired as already true (FACT above). S2a stays parked (owner: rare).
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1440-1470
  - src/melder/aether/spellbook/spellbook_creation_system.py:1356-1382
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_medians.md:1-8
  IMPACT: One method and one docstring in the lowering; the `_spell` test stub gains `_dynamic_environment`.
  NEXT: patch docs (architecture, component SpellCompiler codegen, code description) and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T21:42:10Z
  TYPE: PLAN
  CLAIM: Patch docs written and indexed under system_docs/patches/active/flat_warm_body_2026_10_03/ (architecture,
    component SpellCompiler codegen, code description; ENTRY markers; --check OK). Mapping, patch section ->
    implementation step -> validation step: (a) code description steps 1-2 (the eligible-site branch in
    `_emit_shared_hit`, the class-contract bullet) -> lowering edit -> emitter unit tests: automatic unique site
    emits no alias line and binds `c{i}` to the owner store (instance published there and reused), dynamic unique
    site keeps the line and binds nothing, unowned provider keeps the line, per-conduit site unchanged;
    (b) architecture migration step 1 (the `_spell` stub) -> test stub gains `_dynamic_environment=False`;
    (c) component validation expectations -> a new component file (automatic: same Service across two melds and
    the captured normal plan has no `spells[i]._owner_creations` line; dynamic: the line is present; a cache
    full hit world behaves the same); (d) harness re-run on the shipped body at landing.
  EVIDENCE:
  - system_docs/patches/active/flat_warm_body_2026_10_03/architecture_patch.md:1-50
  - system_docs/patches/active/flat_warm_body_2026_10_03/component_patch_spellcompiler_codegen.md:1-40
  - system_docs/patches/active/flat_warm_body_2026_10_03/code_description_patch_site_plan_lowering.md:1-35
  IMPACT: Entry gate satisfied for the working-copy implementation.
  NEXT: the anchored apply script (lowering, stub, unit tests, component test) on `$HOME/work/melder_cc`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-03T22:08:45Z
  TYPE: FACT
  CLAIM: A second fake-spell stub reads the new slot: `logging_spell` in the door-held-root unit tests builds a
    `SimpleNamespace` with `_owner_creations` and no `_dynamic_environment`, so `_owner_store_constant` raised
    AttributeError on its `unique` root case in the first shard run. The live Spell always carries the slot (False
    before ownership), so the stub gains `_dynamic_environment=False` like `_spell`; the lowering keeps the direct
    read (no `getattr` on an owned attribute). The other `_owner_creations=` stubs in `tests/` never reach the
    site-plan emitter. The component file gained the cache full-hit case the mapping note named: a repeat world
    hydrated from an untouched bundle binds `c0` to ITS Service spell's store and builds its own Service.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py:132-150
  - src/melder/aether/spellbook/spell.py:1440-1470
  - artifacts/flat_warm_body_20261003/apply_s9.py:1-80
  IMPACT: One more test file in the apply script; the emitter contract is unchanged.
  NEXT: MEASURE note (red/green and the shards).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-03T22:08:45Z
  TYPE: MEASURE
  CLAIM: Red on the tree's lowering (`$HOME/work/melder_tree`, the new tests copied in): the three automatic-world
    cases fail on exactly the alias line (`spells[0]._owner_creations` in the captured plan) and the three
    unchanged-behaviour cases (dynamic, unowned, per-conduit) pass. Green on `$HOME/work/melder_cc` with
    `apply_s9.py` applied: lowering unit file 50 + component 3 = 53 passed; shards: unit spellbook+utilities+root
    3197 passed / 2 skipped / 7 xfailed (12.8 s), unit aether+crystallizer+MR+build_assets 5171 passed / 1 skipped
    (19.0 s), component 2293 passed / 23 skipped / 1 xfailed (22.5 s), integration spellbook+conduit 878 passed /
    2 skipped / 2 xpassed (8.5 s), integration multithreading+live_sim 51 passed / 1 xfailed (5.7 s), integration
    aether+crystallizer+MR 1093 passed / 3 xfailed (102.8 s). CPython 3.14.7t, `-X gil=0`. Full-tree suites and
    the gauntlet: Not run (owner-run).
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/red_on_tree_lowering.log:1-25
  - artifacts/flat_warm_body_20261003/logs/green_unit_component.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_unit_spellbook_utilities_root.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_unit_aether_crystallizer_mr.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_component.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_integration_spellbook_conduit.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_integration_multithreading_live_sim.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_integration_aether_crystallizer_mr.log:1-3
  IMPACT: The working copy is green; the landing applies the same script to the tree.
  NEXT: land on the tree: `apply_s9.py --root <tree>`, notch 0.2.8221, release-note section, docs, graph,
    patch docs archived, assets and bundles last, post-landing shards, harness re-run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T00:02:11Z
  TYPE: FACT
  CLAIM: Landed on the tree at 0.2.8221 (notched above 0.2.8220 at landing): `apply_s9.py` applied to the tree
    (the lowering, the two stubs, four unit tests, the component file; CRLF kept, the door-held test file stays
    LF as it was); release-note section "Shared singleton sites read their store as a constant" plus a packaging
    bullet; `src_architecture.md` (operational invariant, the lowering's code-map extent 1588, handoff) and
    `src_components.md` (SpellCompiler emission bullet, the lowering's code-map extent - stale since 2026-09-26 -
    and handoff) with both indexes rebuilt and checked; the graph re-extracted (--strict), the SitePlanEmission
    descriptor gains the owner-store-constant responsibility, accepted and reassembled (27595 lines, index
    verified); patch docs archived to `system_docs/patches/completed/flat_warm_body_2026_10_03/` (Status
    "promoted and archived"); assets rebuilt in the mirror and copied back (three manifests at v0.2.8221, --check
    OK on the tree); LLM bundles rebuilt and --check OK; no `.git/index.lock` left behind. No cache generation
    moved (plans are emitted from rows). The codex bridge lists no chat for melder_2 or muse_0 in this repository
    (command_0-2 and cc_astra_0 are other repositories' agents), so the notch notice is carried by this ticket,
    the board row and the release note, as for 0.2.8217-0.2.8220.
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/apply_tree.log:1-4
  - artifacts/flat_warm_body_20261003/logs/land_docs.log:1-1
  - artifacts/flat_warm_body_20261003/logs/graph_assemble.log:1-5
  - artifacts/flat_warm_body_20261003/logs/assets_check_tree.log:1-3
  - artifacts/flat_warm_body_20261003/logs/llm_bundles_check.log:1-3
  - release_docs/next_version_release.md:425-441
  - system_docs/patches/completed/flat_warm_body_2026_10_03/architecture_patch.md:1-8
  IMPACT: The change set is complete on the tree; nothing else of this lane is in flight.
  NEXT: MEASURE note (post-landing shards and the harness on the shipped body), then the task goes to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T00:02:11Z
  TYPE: MEASURE
  CLAIM: Post-landing shards on a fresh copy of the tree (`$HOME/work/melder_tree`, 3.14.7t, `-X gil=0`): unit
    spellbook+utilities+root 3257 passed / 2 skipped / 7 xfailed (17.0 s), unit aether+crystallizer+MR+
    build_assets 5171 passed / 1 skipped (22.3 s), component 2293 passed / 23 skipped / 1 xfailed (27.7 s),
    integration spellbook+conduit+multithreading+live_sim 929 passed / 2 skipped / 1 xfailed / 2 xpassed
    (19.0 s), integration aether+crystallizer+MR 1098 passed / 7 xfailed (79.5 s). Harness on the shipped body
    (interleaved plain vs the S9 transform, which is now a no-op): plain medians worker 148 ns (pre-landing plain
    160), context_root 260 (316), wide8_unique 359 (447), wide8_existing 368 (444), chain8_transient 404 (432);
    the transform column is within +-3% of plain on every shape, so the shipped emitter already carries the
    S9 shape. Full-tree suites and the gauntlet: Not run (owner-run).
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/post_landing_unit_spellbook_utilities_root.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_unit_aether_crystallizer_mr.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_component.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_integration_spellbook_conduit_mt_livesim.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_integration_aether_crystallizer_mr.log:1-2
  - artifacts/flat_warm_body_20261003/logs/interleaved_shipped_body_run1.md:1-7
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_medians.md:1-8
  IMPACT: The lane's exit gate is met except the owner-run suites and gauntlet; the task is in review.
  NEXT: owner turn-in (full-tree suites and the gauntlet on 0.2.8221; on green the task and story close); then
    the door lane story opens with its epoch audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-10-03T21:31:58Z: IN_PROGRESS. Opened; nothing read or edited yet. Resume from the latest note's NEXT.

STATE 2026-10-03T21:40:58Z: IN_PROGRESS. S9 certified (-7..-17% of the plan on shapes with unique providers), S11 retired as
already true, S2a parked; patch docs next, then the lowering edit. Resume from the latest note's NEXT.

STATE 2026-10-03T22:08:45Z: IN_PROGRESS. S9 implemented and green on the working copy (red on the tree's lowering); landing next: apply, notch 0.2.8221,
release note, docs, graph, patch docs archived, assets and bundles last. Resume from the latest note's NEXT.

STATE 2026-10-04T00:02:11Z: REVIEW. S9 landed at 0.2.8221 (docs, graph, assets, bundles current; post-landing shards green;
harness re-run on the shipped body). Owner-owed: full-tree suites and gauntlet, then turn-in. Nothing in flight.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
