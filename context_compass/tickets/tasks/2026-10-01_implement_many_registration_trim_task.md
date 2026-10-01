# Task: Implement the many registration trim (S1) - one append per creation, per-key disposal methods

## Metadata
- Task ID: TASK-2026-10-01-implement-many-registration-trim
- Story: STORY-2026-09-27-many-registration-trim
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-01T00:59:42Z
- Updated: 2026-10-01T00:59:42Z

## Objective
A disposal-bearing `many` creation registers with one `list.append` into one per-key bucket; the spell's disposal
method list is recorded once per key (at first use) instead of once per entry; cleanup, clear_all, purge and
extract/restore dispose the same objects in the same (newest-first) order with the same ExceptionGroup shape;
a build finishing after `cleanup()` is still refused and disposed. Trimmed A: the store lock is kept (measured
305-384 -> 103-120 ns standalone, -11..-49% of the plan in the certification harness). The emitted
registration line and the hydrators' constants follow the new store verb; the creation-cache generation is
bumped so executors emitted with the old call are retired.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the owner's split directive (2026-10-01); patch docs under
  `system_docs/patches/active/many_registration_trim_2026_10_01/` (architecture, component Creations and
  SpellSpace, component SpellCompiler codegen, code description of registration/disposal/refusal) written and
  linked here, with a patch-section -> edit -> test mapping note, BEFORE any src edit; the owner's confirmation
  of the exact edit (files and symbols) before it lands.
- EXECUTION_BOUNDARY: `src/melder/aether/conduit/creations/creations.py` (add_many_creations,
  _append_many_locked, the disposal walk, cleanup, clear_all, purge, extract/restore of many buckets, the
  cleaned-store refusal), `.../shared_assets/site_plan_lowering.py` (`_emit_many` registration line and the
  prologue), the generalized/many_only hydrators' namespace constants for `dmN`, `utilities/caching_system/
  caching_system.py` (generation), tests (unit on the store, component on the emitted line through a real
  conjure, differential disposal-order tests, purge/extract/restore), the two canonical system documents and
  their indexes, graph descriptors, `release_docs/next_version_release.md`, `__version__`.
- DEPENDENCIES: the S1 story; the certification table; no mailbox claim on any boundary file (M0-155 released
  melder_0's last claims).
- EXIT_GATE: differential tests green (same objects, same order, same errors under cleanup/clear_all/purge/
  late publish/extract/restore); the touched suites green on the VM copy (sharded, 120 s per call); the harness
  re-run showing the plan delta; patch docs promoted and archived; notch, release-note section, docs, graph,
  assets and LLM bundles with --check OK; owner-run gauntlet requested.
- FAILURE_ESCALATION: DECISION_REQUEST on trimmed A vs B once the refusal race is written down (A is the plan;
  B only with a tested refusal path); BLOCKER if any reader of the many buckets cannot be migrated in the same
  change.

## Scope Boundaries
- In scope: the registry shape for `many` with disposal, the one emitted line, the hydrator constants, the
  generation bump, tests, docs, the notch and the release note.
- Out of scope: unique/per-conduit registration; disposal semantics; the doors; S8 and S2a (their own lanes).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's split (2026-10-01T00:59:42Z); S1 is the first static lane.

## Steps / Checklist
- [x] Re-sync the VM copy from the tree (0.2.8215) before any run.
- [x] Read `creations.py` whole (1189 lines, three chunks) and write one note: the many registration and
      disposal paths, the refusal contract, every reader of the `(object, methods)` tuples.
- [x] Read `_emit_many`, `_many_store_prologue` and the hydrators' `dmN`/`sidN` constants; find every caller of
      `add_many_creations` in src and tests (search, then open each).
- [x] Patch docs (architecture, component x2, code description) and the mapping note; link them here.
- [ ] Propose the exact edit (files, symbols, the new verb's signature, the generation bump) and wait for the
      owner's confirmation.
- [ ] Implement on the VM copy; unit, component and differential tests; run the touched suites sharded.
- [ ] Re-run the certification harness and `commandops_shape_probe.py`; MEASURE note.
- [ ] Land on the tree (CRLF), notch above `__version__` (0.2.8215 now), release-note section, docs, graph
      descriptors; promote and archive the patch docs; rebuild assets and LLM bundles LAST; both checks OK.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The trimmed registry in `creations.py`; the emitted line and hydrator constants; the generation bump.
- Tests: unit (store), component (emitted line), differential (disposal order and errors), purge/extract/restore.
- Patch docs promoted into `src_architecture.md` / `src_components.md`; release-note section; notch.

## Files / Paths Impacted
- src/melder/aether/conduit/creations/creations.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/ (hydrator; to confirm)
- src/melder/utilities/caching_system/caching_system.py
- tests/ (unit, component)
- context_compass/system_docs/patches/active/many_registration_trim_2026_10_01/
- release_docs/next_version_release.md, src/melder/__version__.py

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest tests/unit/melder/aether/conduit/creations -q`
  - `python -X gil=0 -m pytest tests/component -q -k "creations or many or disposal or purge"`
  - `python -X gil=0 tests/experimentation/codegen_strategy_certification.py`

## Risks / Rollback Notes
- The disposal walk, purge, extract/restore and the lesser transfer read the tuple shape -> every reader
  migrates in one change; the differential tests prove the order and errors; rollback is the old shape with
  the generation left bumped (old executors would then be re-emitted on the next conjure).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the patch docs, the mapping note and the owner's confirmation.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (the certification table; the re-run after landing)
  - artifacts/many_registration_trim_20261001/ (apply scripts, red/green and suite logs; created at implementation)
  - system_docs/patches/active/many_registration_trim_2026_10_01/ (patch docs; created before the edit)
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: patch docs promoted and archived at turn-in; artifacts kept.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - many registration; per-key disposal methods; cleaned-store refusal; cache generation
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-01T00:59:42Z
  TYPE: PLAN
  CLAIM: Trimmed A as sketched at certification: an internal `Creations.register_many(key, item, methods)` that,
    under `_lock`, refuses a cleaned store, gets the key's bucket (first use creates it, aliases the disposable
    mirror to the same list and records `methods` for the key once), then appends the object alone; cleanup,
    clear_all, purge and extract/restore read objects plus the per-key methods instead of per-entry tuples; the
    public `add_many_creations` keeps its signature and writes the new shape; `_emit_many` emits
    `many_store.register_many(sidN, vN, dmN)`; the hydrators keep binding `dmN`; the generation bumps. All of
    this is UNKNOWN against the source until creations.py is read whole - the next step.
  EVIDENCE:
  - tickets/stories/2026-09-27_many_registration_trim_story.md:1-40
  - tickets/tasks/2026-09-30_build_codegen_strategy_certification_harness_task.md:150-222
  IMPACT: Fixes the reading order: the store first, then the emitter and hydrators, then every caller.
  NEXT: re-sync the VM copy and read creations.py whole (three chunks), one note after the whole read.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T01:02:00Z
  TYPE: FACT
  CLAIM: creations.py read whole (1189 lines). The many registration path is `add_many_creations` ->
    `_append_many_locked` under `_lock` (RLock): cleaned check, `_creations.get`, first-use list, isinstance(list),
    append; then for disposal `_disposable_creations.get`, first-use list, isinstance(list), append of
    `(item, methods)`. Every reader of the many disposal shape: `_dispose_disposable_registry` (tuple -> unique, list ->
    many, newest-first via
    `_dispose_many_creations`), `purge` (tuple/list dispatch after `_detach_purge_entries`, which pops both maps
    under `_lock`; many takes only the store lock), `_detach_single_many_creation` (identity search in the live
    list, independent search of the disposable list - "metadata may be sparse"), `extract_spell_creations` (rows
    `scope/disposable/stored/disposal_methods` by index into the disposable list), `restore_spell_creations`
    (rebuilds both lists per row), `cleanup`/`clear_all` (swap both maps under `_lock`, dispose the detached
    disposable map), `reset_for_pool*` (truthiness of `_disposable_creations` only). The refusal after cleanup
    (`_refuse_publish_into_cleaned_store`) runs the methods outside the lock and always raises; `_lock` is the
    documented tombstone. Disposal methods are the Spell-owned list retained by reference; the store never
    matches, reorders or clears it.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:1-11
  - src/melder/aether/conduit/creations/creations.py:166-218
  - src/melder/aether/conduit/creations/creations.py:353-413
  - src/melder/aether/conduit/creations/creations.py:466-520
  - src/melder/aether/conduit/creations/creations.py:597-711
  - src/melder/aether/conduit/creations/creations.py:714-917
  - src/melder/aether/conduit/creations/creations.py:919-1077
  - src/melder/aether/conduit/creations/creations.py:1079-1169
  IMPACT: Trimmed A fits with one new record type: a many key's disposal metadata becomes ONE record holding the
    live bucket (aliased, not mirrored) and the key's method list; registration is lock, cleaned check, one
    dict get, one append (first use: list + record + two dict stores). Sparse metadata becomes impossible
    (the record covers the whole bucket), so the single-object detach needs no second search. The eight readers
    above all change in the same edit; the row shape of extract/restore stays.
  NEXT: read `_emit_many`, the prologue and the hydrators' `dmN` binding; find every caller of
    `add_many_creations`, `extract_spell_creations`, `restore_spell_creations` and `_disposable_creations` in src
    and tests (search, then open).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T01:05:30Z
  TYPE: FACT
  CLAIM: Every src site that registers a disposal-bearing `many` creation: (1) `SitePlanEmission._emit_many`
    emits `many_store.add_many_creations(sidN, vN, has_disposal_methods=True, disposal_methods=dmN)` after the
    `_many_store_prologue` (normal and key-set plans of the generalized and many_only families; `sidN`/`dmN` are
    bound into the plan namespace by the emitter's `_bind`); (2) the solo family's two executor templates emit
    `many_creations.add_many_creations(spell_id, instance, has_disposal_methods=True, disposal_methods=
    disposal_methods)`; (3) the specializer emitter in `generalized_manifest_no_overrides_compiler` (configuration
    flag; `generalized_hydrator` step 5) emits `creations_{i}.add_many_creations(...)` with the same keywords;
    (4) `_register_spell_instance_prebound` (a runtime-library helper exported to emitted namespaces; no emitted
    body calls it today) calls the public verb. Readers of the many disposal shape outside creations.py: none -
    `conduit_ward.py` and `transfer_of_ownership.py` use only `extract_spell_creations`/`restore_spell_creations`
    rows, whose shape stays; `ConduitCreations` only wraps those two. Cache generation is 15
    (`structural_snapshot_rows`); executors emitted with the old line stay correct (the public verb survives)
    but keep the slow call, so a bump to 16 retires them.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1313-1329
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1401-1409
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:98-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:97-118
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:488-556
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:400-450
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1062-1095
  - src/melder/utilities/caching_system/caching_system.py:167-184
  IMPACT: Four emission/helper sites and one store; tests touching `_disposable_creations` directly (eight files,
    17 references) change with the shape.
  NEXT: MEASURE the candidate verb shapes, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T01:05:30Z
  TYPE: MEASURE
  CLAIM: Candidate `register_many` shapes on a stand-in store with the real RLock (VM 3.14.7t, GIL off, GC off,
    200k registrations, best of 7, two rounds): today's path 204-207 ns; A1 (with-lock, cleaned check, one dict
    get, first-use list + record, append) 104-111; A2 (A1 plus a `type(bucket) is not list` check on an existing
    bucket) 115-126; A3 (A1 with explicit acquire/try/finally/release) 99-100. The type check costs 10-15 ns
    (~10%); the explicit lock calls save 5-10 ns.
  EVIDENCE:
  - artifacts/many_registration_trim_20261001/vm_register_many_shapes_gil0_20261001.md:1-16
  - artifacts/many_registration_trim_20261001/register_many_shapes.py:1-110
  IMPACT: Proposal default is A1 (the repository's `with self._lock:` style; no type check on the hot verb -
    the key's Existence is fixed per Spell, so a non-list slot under a many key is impossible by construction;
    the public `add_many_creations` keeps its check). A3 is offered as an option.
  NEXT: write the patch docs under system_docs/patches/active/many_registration_trim_2026_10_01/.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T01:08:45Z
  TYPE: PLAN
  CLAIM: Patch docs written and linked (four files under system_docs/patches/active/many_registration_trim_2026_10_01/).
    Mapping, patch section -> implementation step -> validation step:
    (a) code_description steps 1-2 (register_many, add_many_creations/_append_many_locked) -> creations.py edit 1
    -> unit: shape, first-use record, mixed-declaration ValueError, cleaned-store refusal (existing test);
    (b) steps 3-4 (disposal walk, purge dispatch) -> edit 2 -> the four regression files pass unchanged in
    behaviour (reverse order, all methods, failure aggregation, first-use atomicity) plus a new purge-all test;
    (c) step 5 (single purge) -> edit 3 -> unit: remainder order, both keys removed when empty, the returned
    disposal entry carries the key's methods; component: `test_conduit_component_purge.py`;
    (d) steps 6-7 (extract/restore) -> edit 4 -> unit: round trip keeps order and methods, mixed rows raise;
    `test_transfer_of_ownership*.py` and `test_conduit_ward.py` pass unchanged;
    (e) codegen entry -> `_emit_many`, the two solo templates, the specializer branch -> emitter unit tests
    assert the new line; component: a disposal-bearing many root melded through a conduit and a SpellSpace;
    (f) architecture migration step 3 -> generation 16 -> the caching-system unit tests that pin CURRENT_VERSION.
  EVIDENCE:
  - system_docs/patches/active/many_registration_trim_2026_10_01/architecture_patch.md:1-90
  - system_docs/patches/active/many_registration_trim_2026_10_01/component_patch_creations_and_spellspace.md:1-80
  - system_docs/patches/active/many_registration_trim_2026_10_01/component_patch_spellcompiler_codegen.md:1-70
  - system_docs/patches/active/many_registration_trim_2026_10_01/code_description_patch_many_registration.md:1-80
  IMPACT: The entry gate is satisfied except for the owner's confirmation of the exact edit.
  NEXT: propose the exact edit (files, symbols, verb signature, generation bump, the two options) and wait.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T01:25:50Z
  TYPE: DECISION
  CLAIM: Owner (2026-10-01): no implementation right now; list every non-PGO strategy and recommend. The
    catalogue and the recommendation are in the static epic (S1 first, in the A3 shape, then the flat-warm-body emitter
    lane
    S8/S2a/S9/S11, then the door lane D1-D3 with D5 for dynamic worlds). The S1 proposal of 2026-10-01 stands
    unchanged and waits for the owner's "go"; the four micro-shapes measured for the catalogue are in this
    task's artifact folder.
  EVIDENCE:
  - tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md:200-330
  - artifacts/many_registration_trim_20261001/vm_static_micro_shapes_gil0_20261001.md:1-30
  IMPACT: No src edit; the lane idles at the confirmation gate.
  NEXT: on the owner's "go" (A1 or A3; type check or not), implement on the VM copy with the tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-10-01T00:59:42Z: IN_PROGRESS. Opened; nothing read or edited yet. Resume from the latest note's NEXT.

STATE 2026-10-01T01:08:45Z: IN_PROGRESS. Store and emitters read, verb shapes measured, patch docs and mapping note
written; waiting for the owner's confirmation of the exact edit. No src edit yet. Resume from the latest
note's NEXT.

STATE 2026-10-01T01:25:50Z: IN_PROGRESS (waiting). Owner reviewing the non-PGO catalogue and the recommendation;
the S1 edit is proposed, not implemented. Resume from the latest note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
