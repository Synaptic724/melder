# Task: Implement the many registration trim (S1) - one append per creation, per-key disposal methods

## Metadata
- Task ID: TASK-2026-10-01-implement-many-registration-trim
- Story: STORY-2026-09-27-many-registration-trim
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-01T00:59:42Z
- Updated: 2026-10-02T18:01:21Z

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
- from_state: in_progress
- to_state: review
- transition_reason: Landed at 0.2.8216 with docs, graph, patch docs, assets and bundles (2026-10-02T18:01:21Z); owner-run suites and
  gauntlet pending.

## Steps / Checklist
- [x] Re-sync the VM copy from the tree (0.2.8215) before any run.
- [x] Read `creations.py` whole (1189 lines, three chunks) and write one note: the many registration and
      disposal paths, the refusal contract, every reader of the `(object, methods)` tuples.
- [x] Read `_emit_many`, `_many_store_prologue` and the hydrators' `dmN`/`sidN` constants; find every caller of
      `add_many_creations` in src and tests (search, then open each).
- [x] Patch docs (architecture, component x2, code description) and the mapping note; link them here.
- [x] Propose the exact edit (files, symbols, the new verb's signature, the generation bump) and wait for the
      owner's confirmation (owner: test it in your space first).
- [x] Implement on the VM copy; unit, component and differential tests; run the touched suites sharded.
- [x] Re-run the certification harness and `commandops_shape_probe.py`; MEASURE note (interleaved A/B).
- [x] Land on the tree (CRLF), notch above `__version__` (0.2.8215 now), release-note section, docs, graph
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
- Working copy (not the tree): unit/component/integration shards green, see the MEASURE note; re-synced from the
  landed tree: creations+caching 125, spell_compiler+component conduit 1269, integration conduit+spellbook 875
  passed; the owner's full-tree suites and the gauntlet: Not run.
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

- DATETIME: 2026-10-02T14:50:45Z
  TYPE: DECISION
  CLAIM: Owner (2026-10-02): "clone it and test it in your space before you proceed". The space is the VM working
    copy `$HOME/work/melder_cc` (a plain copy of src/ and tests/, re-synced from the tree at 0.2.8215; the
    private repo stays on the owner's machine - the cloud sandbox stays off-limits as ruled earlier). This is
    the confirmation to implement S1 there with its tests and measure before any tree landing; the landing
    itself still waits for the owner's word. A1 vs A3 is decided by an in-situ A/B on the real plan (not the
    stand-in): A3 only if it clears the noise band.
  EVIDENCE:
  - tickets/tasks/2026-10-01_implement_many_registration_trim_task.md:1-60
  - system_docs/patches/active/many_registration_trim_2026_10_01/architecture_patch.md:1-90
  IMPACT: The code-edit tranche opens on the working copy; the tree is untouched until "land".
  NEXT: harness "before" run on the 0.2.8215 copy, then the apply script (store, three emitters, generation).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-02T14:51:50Z
  TYPE: FACT
  CLAIM: Mailbox consumed (five blocks, M0-160/163/166/169/172, all NOTICE): melder_0 ran an owner-scheduled docs pass
    (0.2.8208 frame lookups promoted into the system documents, scopes.md, the graph, one release-note bullet)
    and a citation audit (src_architecture/src_components re-cited, bind-guard count 619 at 0.2.8215, the C1
    core set equals the Key Files union); both turned in; assets and LLM bundles current at 0.2.8215 with both
    checks OK; melder_0 holds no melder_private file now. No src change, no notch, so S1 still notches above
    0.2.8215; the system documents are current, so S1's promotion edits them from a fresh base.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-01_audit_remaining_system_document_citations_task.md:1-30
  - src/melder/__version__.py:12-12
  IMPACT: No claim on any file in this lane's boundary; the tree copy at 0.2.8215 is still the base.
  NEXT: the harness "before" run on the working copy, then the apply script.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-02T15:19:38Z
  TYPE: FACT
  CLAIM: S1 implemented on the working copy (`$HOME/work/melder_cc`, tree untouched) by the anchored apply script
    `artifacts/many_registration_trim_20261001/apply_s1.py` (re-runnable against the tree; per-line line endings
    preserved, creations.py is mixed CRLF/LF). Src: `ManyDisposalBucket` (entries = the live bucket aliased,
    methods = the Spell list once) and `Creations.register_many(key, item, disposal_methods)`;
    `_append_many_locked` validates before it appends and refuses a mixed disposal declaration (fail-fast on a
    state the spell id makes impossible); `_dispose_many_creations` takes the record; purge, single purge,
    extract and restore read it (restore refuses mixed rows); the emitted line is
    `many_store.register_many(sidN, vN, dmN)` in the site plan, `many_creations.register_many(spell_id,
    instance, disposal_methods)` in both solo templates, `creations_i.register_many(...)` in the specializer;
    cache generation 16. Tests: a new unit file (19 tests) and a new component file (5 tests through real
    conjures: conduit, solo leaf, SpellSpace exit, single purge); four existing tests re-pinned to the new
    shape (two of them pinned sparse disposal metadata, which the record makes impossible); emitter fakes grew
    `register_many`; the cache-history pin grew 16.
  EVIDENCE:
  - artifacts/many_registration_trim_20261001/apply_s1.py:1-120
  - artifacts/many_registration_trim_20261001/vm_s1_in_situ_ab_gil0_20261002.md:1-60
  IMPACT: The exact edit exists as a script; landing is one run of it on the tree plus the notch, note, docs
    and assets.
  NEXT: MEASURE note, then the owner's go for the landing (and A1 vs A3).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-02T15:19:38Z
  TYPE: MEASURE
  CLAIM: Interleaved A/B on the real emitted plans (pristine 0.2.8215 copy vs the S1 copy, five reps each,
    medians; VM load 0.9-1.4 so single runs are not comparable - paths S1 does not touch moved +8..+12% between
    two runs minutes apart): plan worker 377 -> 249 (-34%), context_root 674 -> 559 (-17%), wide8_unique 682 ->
    527 (-23%), wide8_existing 866 -> 740 (-15%), chain8 804 -> 639 (-21%); whole meld by name worker 536 -> 414
    (-23%), context_root 927 -> 762 (-18%), wide8_unique 962 -> 765 (-20%), wide8_existing 1168 -> 1082 (-7%),
    chain8 882 -> 737 (-16%). A3 (explicit acquire/release) vs A1 (with-statement), same method: plan -2..-12%,
    meld -4..-7% (one +0%), nine of ten rows in A3's favour. Suites green on the working copy (unit minus the
    repository-layout tests the src+tests copy cannot satisfy; component 2257; integration 2009); the A3 copy
    passes the store and component files (175). Not run: the owner's full-tree suites and the gauntlet.
  EVIDENCE:
  - artifacts/many_registration_trim_20261001/vm_s1_in_situ_ab_gil0_20261002.md:1-60
  - artifacts/many_registration_trim_20261001/logs/ab_medians_a1.md:1-12
  - artifacts/many_registration_trim_20261001/logs/ab_medians_a1_vs_a3.md:1-12
  IMPACT: The story's bar (>= 25% off a Worker-shaped many meld on the VM) is met on the plan (-34%) and
    close on the whole meld (-23%, the door is the rest); S1 is ready to land on the owner's word.
  NEXT: owner picks A1 or A3 and says land; then: apply on the tree, notch above 0.2.8215, release note,
    docs, graph descriptors, patch docs promoted, assets last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-02T17:28:23Z
  TYPE: DECISION
  CLAIM: Owner (2026-10-02): "land all that ... give me the recommended" - land S1 with the recommended verb shape,
    A3 (explicit acquire/release; plan -2..-12% and meld -4..-7% over A1 in the interleaved A/B, same
    semantics, the store and component files pass on the A3 copy). Landing order: apply script on the tree
    (--verb a3), notch above 0.2.8215 (read at that moment), release-note section, system documents and
    indexes, graph descriptors, patch docs promoted and archived, NOTICE to the active agents, assets and LLM
    bundles rebuilt last; then the working copy is re-synced from the landed tree and the shards re-run.
  EVIDENCE:
  - artifacts/many_registration_trim_20261001/logs/ab_medians_a1_vs_a3.md:1-12
  - special_instructions/agent_contribution_guide.md:1-97
  IMPACT: First src landing of the static epic; 0.2.8215 -> 0.2.8216 if nobody lands in between (mailbox
    clear at 2026-10-02T17:28:23Z).
  NEXT: apply on the tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-02T17:50:04Z
  TYPE: FACT
  CLAIM: Landed on the tree (owner 2026-10-02: "land all that ... give me the recommended" = A3). `apply_s1.py --root
    <tree> --verb a3` applied its 17 anchored edits plus the two new test files with per-line line endings kept
    (creations.py stays mixed CRLF/LF); `__version__` 0.2.8215 -> 0.2.8216; `release_docs/next_version_release.md`
    header `# Melder 0.2.8216`, the new section "Transient creations with disposal methods register faster" and the
    packaging bullets; `src_components.md` edited (Creations and SpellSpace: dated 0.2.8216 paragraph, the
    Responsibilities bullet, the single-purge sentence, EVIDENCE creations.py:376-468 and the observability
    citations 119-134 / 277-293 / 295-374; Disposal Pipeline data structure + lock note; the SpellCompiler emission
    sentence names `register_many`). CORRECTION: that components edit was written after a context compaction and
    before the REONBOARD (disclosed in the attestation, re-certified 2026-10-02); nothing else was touched then and
    `src_architecture.md` was not written (anchor mismatch). The owner's Codex MCP instruction
    (`special_instructions/codex_mcp.md`, 2026-10-02) retires the file mailbox: this landing's notice goes through
    `codex_bridge` and no mailbox row is written.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/aether/conduit/creations/creations.py:715-857
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1313-1329
  - src/melder/utilities/caching_system/caching_system.py:186-186
  - release_docs/next_version_release.md:1-3
  - special_instructions/codex_mcp.md:1-20
  IMPACT: Src, tests, version, release note and the component map are on the tree; the architecture map, both
    indexes, the graph, the patch-doc promotion, the MCP notice, the asset rebuild and the re-synced shards remain.
  NEXT: `src_architecture.md` (invariant, C1 code map, handoff) and both indexes regenerated with --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-02T18:01:21Z
  TYPE: MEASURE
  CLAIM: Landing validated and finished. Docs: `src_architecture.md` (0.2.8216 invariant, C1 code map creations.py
    1343 / site_plan_lowering.py 1500 / caching_system.py 810 / bind_guard_manifest.py 642, the Entrypoints count
    620, handoff entry) and `src_components.md`; both indexes regenerated, `--check` OK, no `context_compass/`
    path in either. Graph: extracted `--strict`, `ManyDisposalBucket` authored (role, responsibilities,
    owns_state, phases) and the Creations/module prose updated to the record and `register_many`; assembled
    (1212 nodes, 1394 edges) and the three creations nodes accepted after the read. Patch docs moved to
    `system_docs/patches/completed/many_registration_trim_2026_10_01/`; artifact board rows updated. Assets
    rebuilt in a VM mirror (src + system_docs + release_docs; the VM disk was full, 481 MB freed) and copied
    back with CRLF kept: bind guard 619 -> 620 entries (`ManyDisposalBucket`), noted in the release note's
    packaging section; `_build_asset_runner.py --check` and `llm_support/_builder.py --check --include-untracked`
    print only OK; no `.git/index.lock` left. Working copy re-synced from the landed tree: unit creations +
    caching 125 passed, spell_compiler unit + component conduit 1269 passed, integration conduit + spellbook
    875 passed (2 skipped, 2 xpassed). Notice: `codex_bridge.list_threads` shows no chat for melder_0, melder_2
    or muse_0 (the reachable "Muse" threads are MelderOps agents), so no MCP notice was delivered and, per
    `codex_mcp.md`, none was written to the mailbox; this ticket, the board row and the release note carry the
    notch for their re-entry. Not run: the owner's full-tree suites and the gauntlet.
  EVIDENCE:
  - artifacts/many_registration_trim_20261001/logs/landing/shard_unit_creations_caching.log:1-3
  - artifacts/many_registration_trim_20261001/logs/landing/shard_unit_spell_compiler_component_conduit.log:1-3
  - artifacts/many_registration_trim_20261001/logs/landing/shard_integration_conduit_spellbook.log:1-3
  - system_docs/src_architecture_index.md:14-20
  - system_docs/graph/melder/aether/conduit/creations/creations.json:1-60
  - release_docs/next_version_release.md:334-337
  IMPACT: S1 is landed and documented at 0.2.8216; the lane is owner-owed: full suites, the gauntlet, turn-in.
  NEXT: owner runs the full-tree suites and the gauntlet on the tree and turns the task in; then S8 opens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-10-01T00:59:42Z: IN_PROGRESS. Opened; nothing read or edited yet. Resume from the latest note's NEXT.

STATE 2026-10-01T01:08:45Z: IN_PROGRESS. Store and emitters read, verb shapes measured, patch docs and mapping note
written; waiting for the owner's confirmation of the exact edit. No src edit yet. Resume from the latest
note's NEXT.

STATE 2026-10-01T01:25:50Z: IN_PROGRESS (waiting). Owner reviewing the non-PGO catalogue and the recommendation;
the S1 edit is proposed, not implemented. Resume from the latest note's NEXT.

STATE 2026-10-02T15:19:38Z: IN_PROGRESS (ready to land). S1 implemented and measured on the working copy;
waiting for the owner's A1/A3 pick and the landing word. Resume from the latest note's NEXT.

STATE 2026-10-02T18:01:21Z: REVIEW. S1 landed on the tree at 0.2.8216 (A3): src, tests, release note, both system
documents and indexes, graph, patch docs archived, assets and LLM bundles rebuilt with both checks OK; shards
green on the re-synced copy. Owner-owed: full-tree suites, gauntlet, turn-in. Then S8. Resume from the latest
note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
