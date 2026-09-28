# Task: Meld entry cache keyed by registered name and class - one lookup from `conduit.meld` to the builder

## Metadata
- Completed: 2026-09-27T22:20:17Z
- Summary: Name/class-keyed warm meld entries landed (Meld._fast_input_doors; mint in both door subclasses,
  read by Conduit.meld and SpellSpace.meld) with 20 component tests, docs promoted, VM -23..-47% per warm meld
  by name; notched 0.2.8201 (the tree then read 0.2.8202; writer unknown, not melder_0), section "Melds by name or class take the warm
  lane" in release_docs/next_version_release.md, assets and bundles rebuilt at 0.2.8202 (checks OK). Owner
  ruled the closure ("run the tests"): every shard green on the VM; owner-run gauntlet still Not run.
- Task ID: TASK-2026-09-27-meld-entry-cache-by-name-and-class
- Story: STORY-2026-09-27-pgo-strategy-exploration
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T21:31:39Z
- Updated: 2026-09-27T22:20:17Z

## Objective
Make the calls users write - `conduit.meld("Name")` and `conduit.meld(spell=Cls)` - reach the compiled
builder in one lookup on a warm hit. Today only `meld(spell_id=...)` has the inline fast path in
`Conduit.meld`; name and class melds pay a delegate frame, a second `isinstance`, a name/class -> id
lookup and the forwarding lane before the builder runs (533-536 ns vs 372 ns for a width-1 object, VM).
The fix is a cache: entries keyed by the registered name and by the class, beside the spell-id entries,
carrying the same guards (door epoch, creation-context identity) and cleared by the same events. Users
change nothing. Measured with the prototype over the real runtime objects: -32..-57% per warm creation on
the shapes people write, -71% on a direct singleton meld (story note 2026-09-27T21:00:36Z).

## Ticket Contract
- ENTRY_GATE: `attention_board.md` row `codegen_pgo_strategies` routes here; owner's go recorded in the
  story (2026-09-27, "give it a shot"); patch docs under `system_docs/patches/active/meld_entry_cache_2026_09_27/`
  exist and are linked below before any src edit (meld hot path is system-impacting).
- EXECUTION_BOUNDARY: `src/melder/aether/conduit/conduit.py` (`Conduit.meld`),
  `src/melder/aether/conduit/meld/conduit_meld.py` (`ConduitMeld.meld` mint and read),
  `src/melder/aether/conduit/meld/meld.py` (`Meld._fast_meld_doors` contract and resets),
  `src/melder/aether/conduit/spell_space/spell_space.py` and `src/melder/aether/conduit/meld/spellspace_meld.py`
  (the SpellSpace mirrors); the invalidation sites in `spellbook.py`, `spell.py`,
  `spellbook_creation_system.py` are READ, and edited only if a name/class remap event is found uncovered;
  tests under `tests/unit/melder/aether/conduit/` and `tests/component/`; the experiment
  `tests/experimentation/meld_entry_dispatch_experiment.py` for measurement.
- DEPENDENCIES: the story's dispatch measurement; the warm id lane of 2026-09-26 (`Meld._fast_meld_doors`);
  the door epoch (`Spell._door_epoch`); `special_instructions/agent_contribution_guide.md` (notch, note, rebuild).
- EXIT_GATE: patch docs consumed and mapped in notes; src change landed byte-identically on the device tree;
  unit and differential tests written and green on the VM (3.14t, `-X gil=0`); existing conduit/meld/spell_space
  suites green on the VM; the dispatch experiment re-run against the real change; owner-run suites and gauntlet
  are the acceptance gate ("Not run." until reported); notch/note/rebuild per the guide once the owner answers
  the frozen-window question.
- FAILURE_ESCALATION: BLOCKER if a name/class -> spell remap event has no invalidation that reaches the new
  entries; DECISION_REQUEST on the notch (frozen window) and on any behaviour the cache would change with
  hooks, overrides or validation-required states.

## Scope Boundaries
- In scope: the name/class-keyed entries, their minting on a successful normal meld, their reads in
  `Conduit.meld` and the SpellSpace entry, their invalidation, tests, measurement, docs, patch promotion.
- Out of scope: PGO proper, codegen changes, the spell-id path's behaviour, API changes, dynamic-environment
  melds (they keep the gate path), hook/override/validation-required melds (they keep the slow path).

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Landed, tested on the VM (all shards green), documented, notched and rebuilt; owner directed
  the close-out ("run the tests and keep iterating", 2026-09-27T22:20:17Z).

## Steps / Checklist
- [x] Read `Conduit.meld`, `ConduitMeld.meld`, the SpellSpace mirrors and `Meld`'s fast-door fields whole.
- [x] Find every event that remaps a registered name or class to a different spell (notch, rebind, remove,
      transfer, upgrade, cleanup) and prove each clears or invalidates the new entries.
- [x] Write the patch docs (architecture, component: Meld Resolution Runtime, code description) and link them.
- [x] Implement: mint name/class entries in `ConduitMeld.meld`; read them in `Conduit.meld`'s inline fast path;
      mirror in `SpellSpace.meld` / `SpellSpaceMeld.meld`.
- [x] Tests: unit (keys, guard misses, bypasses), differential (same object by name/class/id), regression suites.
- [x] Re-run `tests/experimentation/meld_entry_dispatch_experiment.py` against the real change (directional).
- [x] Docs: `src_components.md` (Meld Resolution Runtime), `src_architecture.md` (meld sequence), indexes.
- [x] Notch (0.2.8201) and release-note entry on the owner's word; rebuild follows last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Name/class-keyed warm entries in the conduit and SpellSpace meld doors, with tests and measurement.
- Patch docs promoted into the canonical maps at closure.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py
- src/melder/aether/conduit/meld/conduit_meld.py
- src/melder/aether/conduit/meld/meld.py
- src/melder/aether/conduit/spell_space/spell_space.py
- src/melder/aether/conduit/meld/spellspace_meld.py
- tests/unit/melder/aether/conduit/ (new test module), tests/component/ (differential)
- context_compass/system_docs/patches/active/meld_entry_cache_2026_09_27/
- context_compass/system_docs/src_components.md, src_architecture.md and their indexes

## Validation
- VM, 3.14.7t `-X gil=0`, `-p no:cacheprovider`, after the notch and rebuild: device tree - unit conduit/
  spellbook/build_assets/package 1445 (1 skipped), component conduit+spellbook 1484, architecture/workflows/
  llm_support 460; worktree copy synced from the tree - component rest 698 (43 skipped, 1 xfail), unit rest 6766
  (2 skipped, 7 xfail), integration conduit/aether/multithreading/mutation_research/live_sim 1113 (1 xfail),
  integration spellbook+crystallizer 841 (2 skipped, 5 xfail, 2 xpass). Asset `--check` and LLM bundle `--check`
  OK at 0.2.8202. Owner-run suites and gauntlet: Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest tests/unit/melder/aether/conduit tests/component -q -p no:cacheprovider`
  - `python -X gil=0 tests/experimentation/meld_entry_dispatch_experiment.py`
  - `python -m pytest benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py -q -s` (owner)

## Risks / Rollback Notes
- A stale name/class entry after a remap would build the wrong spell: every remap event must clear or bump;
  the guard ladder (epoch, context identity) covers the events that already bump today. Rollback: remove the
  two reads and the mint; the id path is untouched.
- Hooks, overrides, validation-required and dynamic environments keep the existing path, so their behaviour
  cannot change; the differential test proves the same object comes back by name, class and id.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No src edit before the patch docs exist and are linked.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner directive; gauntlet Not run)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/meld_entry_cache_2026_09_27/ (written before src edits)
  - artifacts/pgo_strategies_20260927/ (the measurements this task acts on; story-owned)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: patch docs promoted into src_components/src_architecture at closure and archived.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - warm meld entry; fast doors; door epoch; name/class -> spell remap events
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T21:31:39Z
  TYPE: PLAN
  CLAIM: Known from the story's measurement and the reads behind it: `Conduit.meld` has an inline fast path for
    `spell_id=` only (conduit.py:4527-4576); `ConduitMeld.meld` reads `_fast_meld_doors` for ANY str argument
    (id or registered name) and mints `self._fast_meld_doors[fast_door_key]` with `fast_door_key = spell` for
    str arguments, None for class arguments, on a successful normal meld; the class path goes through
    `_input_resolution_cache` keyed `(spell_name, spell, spellframe, binding_name)`; both caches are cleared at
    spellbook.py:6842-6843 (conjure-existing/upgrade) and the door epoch bumps at spell.py:700/719,
    spellbook_creation_system.py:1092 and meld.py:981. UNKNOWN until read: whether notch, rebind, removal and
    transfer clear or bump the name-keyed entries, and how the SpellSpace mirrors mint.
  EVIDENCE:
  - tickets/stories/2026-09-27_pgo_strategy_exploration_story.md:209-231
  - src/melder/aether/conduit/conduit.py:4527-4576
  IMPACT: The change is two reads and one mint plus invalidation proof; the proof is the work.
  NEXT: read `ConduitMeld.meld` and `Meld` whole, then the remap events, and note each.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:38:20Z
  TYPE: FACT
  CLAIM: Read whole: `Conduit.meld`, `ConduitMeld.meld`, `SpellSpace.meld`, `SpellSpaceMeld.meld`, `Meld.__init__`/
    `cleanup`/`_resolve_spell*`, the park/promote helpers, `_apply_notch`, `cleanup_spell`, `cleanup_and_remove_spell`,
    `_destroy_spell_index`, `Spell.cleanup`/`_cleanup_creation_context`/`invalidate_spell`, `LookupContainer`,
    `SpellInputUtils`. (1) CORRECTION of the PLAN note: no name-keyed entry exists today. `Conduit.meld("Name")`
    calls the door as `meld(None, spell_name="Name")`, so the door's str branch (`fast_door_key = spell`, ids only)
    is never taken; names and classes run the else-branch through `_input_resolution_cache`
    ((spell_name, spell, spellframe, binding_name) -> spell id, capped 2048) and `fast_door_key` stays None: nothing
    is minted. (2) A key can only come to resolve to a different spell after the old holder is parked or cleaned:
    `bind` claims the framewide signature and `LookupContainer.claim` raises for a different spell id; notch is
    the only caller of `_deactivate_owned_spell` and follows it with `outgoing._cleanup_creation_context()`
    (epoch bump, context None); `cleanup_and_remove_spell` pops every map, releases the signature and calls
    `Spell.cleanup()` (deletes `_creation_context`, so the guard read raises AttributeError = miss);
    `_destroy_spell_index` runs only for an emptied index (no active member to have minted). (3) Entries mint only
    when `target_spell._creation_gate is None`, i.e. automatic worlds: link, sever, transfer and upgrade never see a
    minted entry, and upgrade clears both caches anyway (spellbook.py:6842-6843). (4) Hooks, overrides,
    validation-required and resolution-required states are covered exactly as for the id lane: the live
    `_meld_hooks` and `_spellbook_validation_required` reads plus the epoch bumps at spell.py:700/719, meld.py:981
    and spellbook_creation_system.py:1092. (5) `normalize_spell_name` keys instances by their class name, so an
    instance passed as `spell` must not become a cache key (unbounded, keeps objects alive): mint only for `str`
    names and classes (`isinstance(spell, type)`); callables/instances keep the door path.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4527-4640
  - src/melder/aether/conduit/meld/conduit_meld.py:259-640
  - src/melder/aether/conduit/meld/meld.py:60-130
  - src/melder/aether/conduit/meld/meld.py:240-372
  - src/melder/aether/conduit/meld/meld.py:1698-1900
  - src/melder/aether/conduit/spell_space/spell_space.py:455-568
  - src/melder/aether/conduit/meld/spellspace_meld.py:440-600
  - src/melder/aether/spellbook/spellbook.py:600-700
  - src/melder/aether/spellbook/spellbook.py:1459-1580
  - src/melder/aether/spellbook/spellbook.py:3695-3833
  - src/melder/aether/spellbook/spellbook.py:3964-4004
  - src/melder/aether/spellbook/spellbook.py:4130-4241
  - src/melder/aether/spellbook/spellbook.py:5318-5360
  - src/melder/aether/spellbook/spellbook.py:6818-6850
  - src/melder/aether/spellbook/spell.py:533-632
  - src/melder/aether/spellbook/spell.py:680-731
  - src/melder/aether/spellbook/spell.py:1353-1420
  - src/melder/aether/aetheric_frame/lookup_container.py:1-40
  - src/melder/utilities/helpers/general_helpers.py:241-428
  IMPACT: The name/class entry can carry exactly the id entry's guards (epoch, context identity, live hooks and
    validation flags) and inherits no new staleness class; a separate dict keeps a registered name that happens to
    equal another spell's 64-hex id from ever aliasing the id lane.
  NEXT: write the patch docs (architecture, component Meld Resolution Runtime, code description), then implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T21:40:22Z
  TYPE: PLAN
  CLAIM: Patch docs written and consumed in the required order (architecture -> component -> code description);
    the mapping patch section -> implementation -> validation is the architecture patch's Ticket Coverage Matrix
    (I1-I5). Exact edits, in order: (1) `meld.py`: `Meld.__slots__` + `__init__` gain `_fast_input_doors: Dict[Any,
    Tuple[Spell, CreationContext, int, bool]] = {}`, `cleanup` deletes it, the class docstring's registry
    paragraph describes both registries and their readers. (2) `conduit_meld.py` and `spellspace_meld.py`
    `meld`: the else-branch computes `fast_input_key` (name: `spell is None`, `type(spell_name) is str`,
    `spellframe is None`, `binding_name is None`; class: `spell_name is None`, `isinstance(spell, type)`,
    `spellframe is None`, `binding_name is None`) and both success arms write the entry under it when
    `fast_door_key is None`; docstring Contract gains the sentence. (3) `conduit.py` `Conduit.meld` and
    `spell_space.py` `SpellSpace.meld`: the warm block becomes one lane fed by either registry (id shape from
    `_fast_meld_doors`, name/class shape from `_fast_input_doors` with a TypeError-as-miss around the get), the
    ladder and arms unchanged, the id miss tail unchanged; docstrings gain the lane. (4) `spellbook.py:6843`:
    `runtime._fast_input_doors.clear()` beside the two clears. Tests: a new
    `tests/unit/melder/aether/conduit/test_meld_input_fast_door.py` and a differential component test.
  EVIDENCE:
  - system_docs/patches/active/meld_entry_cache_2026_09_27/architecture_patch.md:1-80
  - system_docs/patches/active/meld_entry_cache_2026_09_27/component_patch_meld_resolution_runtime.md:1-70
  - system_docs/patches/active/meld_entry_cache_2026_09_27/code_description_patch_input_door.md:1-60
  IMPACT: Entry gate satisfied (patch docs exist, linked, mapped); the owner's go covers these edits.
  NEXT: implement on the VM worktree copy, then apply byte-identically to the device tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:59:03Z
  TYPE: MEASURE
  CLAIM: Landed on the device tree byte-identically (six src files, whitespace-insensitive diff vs HEAD: +160/-26, all
    CRLF) plus `tests/component/melder/aether/conduit/test_conduit_component_input_fast_door.py` (20 tests) and the
    experiment's mint check. VM runs on 3.14.7t `-X gil=0`, `-p no:cacheprovider`: the new module 20/20; from the
    worktree copy: component conduit 708, unit conduit+spellbook 1185, component spellbook+aether 1303 (+1 xfail),
    remaining component + unit aether 3099 (43 skipped), unit spellbook/utilities/crystallizer/mutation_research/
    build_assets 3951 (2 build_assets failures are environmental - the copy has no context_compass/; both pass from
    the device root), integration conduit+aether 1004, spellbook+crystallizer 841, the rest 244; from the device
    tree: component conduit 708 and unit conduit/spellbook/build_assets/architecture/llm_support/workflows 1760.
    Dispatch experiment after the change (before -> after, ns per `conduit.meld("Name")`, py/C calls 5/4 -> 4/1-2):
    solo 453 -> 269 (-41%), w1_singleton 537 -> 350 (-35%), w2_mixed 683 -> 498 (-27%), w4_mixed 888 -> 687
    (-23%), wide8_singleton 957 -> 748 (-22%), stored singleton melded directly 333 -> 177 (-47%); by class the
    same within noise (294/370/514/691/744/183); by id unchanged (282/365/511/701/764/183). Name, class and id are
    now at parity: the remaining gap to the 195 ns prototype is `Conduit.meld`'s own frame and its three shape
    checks. Owner-run suites and gauntlet: Not run.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_meld_entry_dispatch_after_change_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/vm_meld_entry_dispatch_run_gil0_20260927.md
  - src/melder/aether/conduit/conduit.py:4531-4600
  - src/melder/aether/conduit/meld/conduit_meld.py:456-470
  - src/melder/aether/conduit/meld/meld.py:302-348
  - tests/component/melder/aether/conduit/test_conduit_component_input_fast_door.py:1-783
  IMPACT: The measured proposal is in the tree with its guards proven by tests; acceptance is the owner's run.
  NEXT: canonical docs (src_components Meld Resolution Runtime, src_architecture meld sequence) and indexes; the
    owner's answer on the notch (frozen window) decides `__version__`, the release-note entry and the rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:02:05Z
  TYPE: DECISION_REQUEST
  CLAIM: Canonical docs promoted (src_components: "Warm lane for melds by registered name and by class", the meld
    flow; src_architecture: the meld sequence and both handoff summaries) and both indexes regenerated (--check OK).
    Versioning: 0.2.82 is CUT (`release_docs/0.2.82.md` at 19:15Z, `next_version_release.md` empty) and not yet
    committed, tagged or published, so the guide's frozen window is open and this src change is not notched. The
    tree now carries the change, so the owner picks: (A) fold it into 0.2.82 - on the owner's word the section
    below is appended to `release_docs/0.2.82.md` (the never-edit-a-cut rule waived once, nothing is published)
    and the assets rebuild at 0.2.82; (B) keep 0.2.82 as cut - after the publish, notch 0.2.8201, put the section
    in `next_version_release.md`, rebuild. Recommendation: A (one release, nothing shipped in between). Either
    way the asset check is STALE until the rebuild that follows the decision (source keys moved).
    Draft section (user-facing): "## Melds by name or class take the warm lane / `conduit.meld("Service")` and
    `conduit.meld(spell=Service)` now reach the compiled builder in one lookup once the spell has been built once
    through that call - the warm lane `meld(spell_id=...)` already had; `SpellSpace.meld` the same. Nothing
    changes in what you call or get back: the same object for a stored lifetime, a fresh one per call for `many`,
    the same errors, overrides and existing-object behaviour. Melds with `spellframe` or `binding_name`,
    instances or callables passed as `spell`, dynamic worlds, hooks and non-dict overrides keep their current
    path. Directional (2-core VM, 3.14t free-threaded): a warm meld by name 453 -> 269 ns for a dependency-free
    class, 537 -> 350 with one singleton dependency, 333 -> 177 for a stored singleton melded directly."
  EVIDENCE:
  - special_instructions/agent_contribution_guide.md:20-45
  - system_docs/src_components.md:3051-3085
  - system_docs/src_architecture.md:698-704
  IMPACT: The change is complete and documented; only the release bookkeeping waits on the owner's word.
  NEXT: owner answers A or B; then the note entry, (notch,) rebuild, closure with patch promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:06:50Z
  TYPE: DECISION
  CLAIM: Owner ruled (2026-09-27T22:06:50Z): notch the version now despite the cut 0.2.82 being unpublished,
    run the tests, keep iterating, and put the entry in `release_docs/next_version_release.md`. Done: `__version__`
    0.2.82 -> 0.2.8201
    (the first 0.0001 notch), the running note opened with header `# Melder 0.2.8201`, `**Unreleased**`, the
    section "Melds by name or class take the warm lane" and a "Packaging and documentation" section naming the
    regenerated packaged docs and the 0.2.8201 rebuild; NOTICE F0-1..F0-4 sent to melder_0, melder_1, melder_2
    and muse_0 with alert lines ("notch above 0.2.8201 if you land after").
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-28
  - mailbox_board.md:100-140
  IMPACT: Release bookkeeping settled by the owner; the rebuild and the re-run of the suites follow, then closure.
  NEXT: rebuild assets and LLM bundles at 0.2.8201 with both --check runs, then re-run the suites from the tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:09:37Z
  TYPE: CONFLICT
  CLAIM: Mailbox M0-63 (melder_0, 21:49:53Z) consumed late: melder_0 claimed sole-writer status on conduit.py and
    spell_space/ (plus conduit_ward.py, cleanable.py, aetheric_frame.py) for the scope-exit lane and asked to be
    told before edits. My landing at 21:54:42Z edited `Conduit.meld` (conduit.py:4531-4600) and `SpellSpace.meld`
    (spell_space.py:496-562) without reading it - the mailbox was last checked at 21:30Z, before the message.
    Both files are unchanged on the tree since my landing (cmp against my copies). melder_0 has since taken
    0.2.8202 (22:06:38Z); my asset rebuild ran after that and is stamped 0.2.8202. Sent F0-5 (ACK requested)
    with the exact ranges and the re-sync ask; the running note header is set to 0.2.8202.
  EVIDENCE:
  - mailbox_board.md:250-270
  - src/melder/aether/conduit/conduit.py:4531-4600
  - src/melder/aether/conduit/spell_space/spell_space.py:496-562
  IMPACT: If melder_0 applies whole-file copies over the tree, `Conduit.meld`/`SpellSpace.meld` lose the lane;
    the component test would go red and my apply scripts re-land it. Process fix for me: read the mailbox at
    every lane switch and before every landing, as the protocol says.
  NEXT: finish the rebuild checks and LLM bundles, re-run the suites, then close; watch for melder_0's ACK.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:20:17Z
  TYPE: FACT
  CLAIM: Close-out. Owner ruled the collision fine ("notch this as you want"); `__version__` stays at melder_0's
    0.2.8202 and the running note header says 0.2.8202. Rebuilt assets (460/619/4 entries) and LLM bundles (src 576,
    tests 1025, other 379) at 0.2.8202; both `--check` OK. Suites re-run after the rebuild: all shards green (see
    Validation). Patch docs promoted (src_components, src_architecture) and archived to
    system_docs/patches/completed/meld_entry_cache_2026_09_27/. No ACK from melder_0 yet on F0-5.
  EVIDENCE:
  - release_docs/next_version_release.md:1-28
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:1-20
  - llm_support/manifest.json:1-20
  IMPACT: Ticket closes; the next iteration (executor held in the entry) opens under the story and lands only after
    melder_0's scope-exit change, since it touches the same two front-door files.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T23:07:32Z
  TYPE: FACT
  CLAIM: Correction (melder_0 ACK M0-66, 22:56:25Z): melder_0 did not write `__version__` 0.2.8202 - it made no
    device source write in its session. The two notes above that attribute 0.2.8202 to melder_0 are wrong on
    that point; the writer is UNKNOWN (the owner ruled the 8201 -> 8202 move fine). The tree reads 0.2.8202 and
    the assets and the running note header are stamped at it, unchanged. melder_0 notches above it at landing.
  EVIDENCE:
  - mailbox_board.md:285-294
  - src/melder/__version__.py:12-12
  IMPACT: Attribution only; no version, asset or note content changes.
  NEXT: none (closed ticket).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE 2026-09-27T21:31:39Z: IN_PROGRESS. Opened on the owner's go. Next: read the meld doors and the remap events whole,
write the patch docs, then implement. Resume from the latest note's NEXT.
STATE 2026-09-27T21:59:03Z: IN_PROGRESS. Landed with tests and measurement; docs and the notch decision remain.
Resume from the latest note's NEXT.
STATE 2026-09-27T22:02:05Z: REVIEW. Docs promoted; waiting on the owner's A/B on the release bookkeeping and
the owner-run suites. Resume from the latest note's NEXT.
STATE 2026-09-27T22:20:17Z: DONE. Landed, tested, documented, notched, rebuilt; closed on the owner's directive.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
