

# Task: Match annotations by kind - categories never provide, contracts are recorded, concrete-class frames refused

## Metadata
- Task ID: TASK-2026-10-04-repair-annotation-kind-matching
- Story: STORY-2026-10-03-annotation-type-vs-category-matching
- Status: done
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-04T01:25:00Z
- Updated: 2026-10-04T11:55:00Z

- Completed: 2026-10-04T11:55:00Z
- Summary: Landed 2026-10-04 (fable_1) at Melder 0.2.8222 (notched from 0.2.8221): a spellframe is a string
  category or a Protocol contract (concrete classes refused at bind - Breaking), the binding records
  `spellframe_kind` + `implemented_protocols`, Phase 3 matches by kind (one predicate, four index buckets),
  the crystal records the kind (RecordVersion 4.1.0) and the loaders hydrate or degrade with a shortfall; cache
  generation 20; 18 test files swept, regressions added (defect module 14, restore/graft 3, Spell/enum/Bind/
  Phase 3/crystal units). Release-note section led "**Breaking change:**"; README, src_architecture,
  src_components, indexes, graph, assets and bundles current. Closed by owner directive; the four tiers were
  Not run after the final regressions (owner runs them; the earlier mirror run was green except classified
  flakes). Follow-ups opened in tickets/tasks/backlog/ (deeper Protocol check; `implements=`).

## Objective
Land the owner's 2026-10-03 decision (reproduce task, DECISION 01:00Z): the binding records its spellframe
kind (`none` / `category` / `contract`) and the Protocol it was checked against; bind refuses a spellframe
that is neither a string nor a Protocol; Phase 3 matches a class annotation to its type, a Protocol
annotation to its recorded implementers, a string to type-or-contract by name and never to a category, and a
collection to the group its kind names; the crystallizer records and re-hydrates the frame kind so a restore
resolves as the recorded world did; cache generation 20; regressions red-to-green; test sweep; docs; notch;
release note (Breaking change lead); rebuild last.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the patch lane
  `system_docs/patches/active/annotation_kind_matching_2026_10_04/` (architecture, three component patches,
  one code description) exists and is linked below; the owner's DECISION is on the reproduce task; the
  matcher, Bind, Spell, crystal and loader code was read in full before the lane was written.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/spellframe_kind/` (new), `spell.py`, `bind/bind.py`,
  `spell_compiler/phases/compiler_phase_3.py`, `utilities/helpers/general_helpers.py` (is_protocol_type),
  `crystallizer/crystals/spell_crystal.py`, `crystallizer/crystal_loader_system/{restore_engine,graft_runner}.py`,
  `crystallizer/persistence/record_version.py`, `utilities/caching_system/caching_system.py` (generation 20 -
  fable_0's open lane file; the owner approved and relays), `melder/__init__.py` (export), their tests, the
  28 test files of the plain-class frame sweep, README.md, release note, system docs, graph descriptors.
  Prototype in the VM mirror first; apply to the tree by script.
- DEPENDENCIES: the reproduce task (regression module landed under strict xfail; survey artifacts); fable_0's
  flat_warm_body lane (review/handoff) for `caching_system.py`.
- EXIT_GATE: the four defect cases pass with their markers removed; new unit tests for the predicate per kind,
  index/scan parity, Bind kinds and refusal, Spell fields, crystal fields; restore round-trip of a
  Protocol-framed provider; four tiers green except failures classified pre-existing (fail alone unpatched);
  notch; release note; README + src_architecture + src_components + indexes + graph current; assets and bundles
  rebuilt with both checks OK; patch docs promoted and archived at turn-in.
- FAILURE_ESCALATION: DECISION_REQUEST if the sweep meets a test whose intent cannot be kept under the new
  rule; CONFLICT if `caching_system.py` is being edited by fable_0 at landing time.

## Scope Boundaries
- In scope: the change set above.
- Out of scope (follow-up backlog tickets, owner-approved): the deeper Protocol check (inherited members,
  annotation-only fields, callable arity); an explicit `implements=(...)` bind argument; the watcher and
  Phase 4 cycle heuristic's name keying.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: landed at 0.2.8222; closed by owner directive (2026-10-03 23:34 local) with the tiers owner-owed.

## Steps / Checklist
- [x] Patch-section -> implementation -> validation mapping noted here (consumption mapping).
- [x] Red: the four xfail cases with `--runxfail`, the new bind/Spell/crystal tests, on the unpatched mirror.
- [x] Source in the mirror (apply script), regression module markers removed, unit tests added.
- [x] Test sweep: 18 files converted (the runtime refusals; the other static matches were stubs or dead code
      paths), reviewed per file; `repo: "extra_frame"` -> SpellMap; rebind M2 guard -> Protocol frame.
- [x] Four tiers on the mirror; classify every failure (this change vs pre-existing alone-on-tree).
- [x] Apply to the tree (CRLF-preserving script); re-run the touched tiers from the tree.
- [x] README DI + spellframe paragraphs; src_architecture invariant + failure mode + code map; src_components
      Phase 3, Bind, Spell, crystal entries; indexes; graph descriptors re-authored and accepted; assemble.
- [x] Notch (read `__version__` at landing), release note section (Breaking change lead) + Packaging bullet.
- [x] Closure: reproduce task + this task, story, epic status; boards; patch docs promoted + archived.
- [x] Rebuild assets and bundles last; both `--check` OK; NOTICE fable_0 (owner relay) of the notch and the
      generation 20 edit.
- [x] Open the two follow-up backlog tickets (deeper Protocol check; `implements=`).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The source change at the notched version; regressions; docs; the artifact folder with apply scripts, the
  codemod, red/green and tier logs.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY.

## Validation
- Four tiers after the final regressions: Not run (owner-owed by directive). From the repository root on 3.14t:
  `python -m pytest tests/unit -q -n 4 -p no:cacheprovider`, `python -m pytest tests/component -q -n 4 -p no:cacheprovider`,
  `python -m pytest tests/integration -q -n 4 -p no:cacheprovider`,
  `python -m pytest tests/tests tests/experimentation tests/experiments -q -p no:cacheprovider`.
  Known pre-existing flakes to expect under xdist: three order-dependent spellbook integration tests that pass
  alone (test_spellbook_integration.py::test_bind_conjure_and_meld_existing_creation, two in
  test_spellbook_integration_resolution_contract.py) and, on the VM mount only, test_method_inspector.py.
- Ran green on the tree at landing: the regression module (14), the restore/graft module (3), test_spell.py +
  test_spellframe_kind.py (107); earlier mirror tiers (change set minus the last five regressions): unit 8889,
  component 2293, integration 2038, other 250.
- `python src/melder/_build_assets/_build_asset_runner.py --check` and `python llm_support/_builder.py --check
  --include-untracked`: run at turn-in (see the final note).

## Risks / Rollback Notes
- Breaking bind refusal: external users binding a class as a frame get a TypeError naming the fix; led as a
  Breaking change in the release note.
- Restore fidelity: a Protocol that cannot be imported at restore files a shortfall and the spell is bound as
  a category (documented).
- Rollback: revert the source and the tests together; records at 4.1.0 stay readable; bundles at 20 go cold.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] Never claim a test ran that did not run ("Not run.").
- [ ] A search hit is not a read: every edited function was read in full first.

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
  - artifacts/annotation_category_collision_20261003/ (survey, probes, prototype; this task adds fix/landing)
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/architecture_patch.md
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/component_patch_binding_pipeline.md
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/component_patch_spellcompiler_phase3.md
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/component_patch_crystallizer_frame_kind.md
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/code_description_patch_compiler_phase3.md
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: patch docs promoted and archived at turn-in; artifacts kept with the epic's evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-04T01:25:00Z
  TYPE: PLAN
  CLAIM: Consumption mapping (patch section -> implementation -> validation). architecture_patch "Interface and
  Boundary Deltas" -> enum module + package export + Spell fields + Bind classification/refusal + Phase 3
  predicate/index + crystal fields/loader hydration + generation 20 -> the four tiers and the regression module.
  component_patch_binding_pipeline -> bind.py step 4 and the Spell call, spell.py ctor/docstring -> test_bind
  kinds/refusal, test_spell fields. component_patch_spellcompiler_phase3 + code_description -> `_annotation_kind`,
  the three spell keys, `_matches_annotation(..., collection)`, three-bucket index, two resolvers ->
  test_compiler_phase_3 predicate x kind, parity, layout pin; the integration module. component_patch_crystallizer
  -> spell_crystal fields/describe, restore_engine `_bind_one_active`/`_bind_one_staged`, graft_runner three
  sites via one helper each, RecordVersion 4.1.0 -> crystal describe unit tests, a record/restore round trip.
  Known pre-existing approximations left as they are: `_dependency_key_for_dep` and
  `BindingResolutionCycleStrategy._binding_key_for_requirement` key annotations by name.
  EVIDENCE:
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/architecture_patch.md:1-84
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/component_patch_spellcompiler_phase3.md:1-53
  - system_docs/patches/active/annotation_kind_matching_2026_10_04/component_patch_crystallizer_frame_kind.md:1-49
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:252-298
  IMPACT: the entry gate is met; implementation may start in the mirror.
  NEXT: red run on the unpatched mirror (four cases with --runxfail), then the source apply script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T02:05:00Z
  TYPE: MEASURE
  CLAIM: MIRROR GREEN on all four tiers with the change set applied (fix/landing/apply_kind_matching_src.py +
  apply_kind_matching_tests.py + test_restore_spellframe_kind_integration.py): unit 8889 passed / 3 skipped /
  7 xfailed; component 2293 passed / 23 skipped / 1 xfailed; integration 2038 passed / 2 skipped / 4 xfailed /
  2 xpassed (the xfail/xpass rows are other files' pre-existing markers); tests+experimentation+experiments 250
  passed / 4 skipped. The regression module runs unmarked (9 original cases + 5 new: Protocol contract by object
  and by TYPE_CHECKING string, the bind refusal, a string category annotation as an unresolved input, the three
  collection groups). Red before: the four defect cases, the new Bind/Spell/crystal tests. Sweep performed (all
  runtime refusals, not the static 127): 18 test files - marker classes meant as contracts became Protocols
  (Definition, IMember, Unregistered, ISignatureFrame, _Frame, _TypingFrame, _FutureFrame, _LocalFrame,
  _ServiceFrame/_FrameA/_FrameB/_RootFrame stubs, ReferenceFrame, ServiceFrame, IExistingValue for the existing
  instances, IProduct for the function provider, IProvider for the rebind M2 guard); grouping-only frames became
  labels (RuntimeDefinition, BasicConfig, the shape probe's Config); `Engine` as its own frame is bound bare; the
  eq-risky snapshot case uses a bound object; `test_non_protocol_frames_keep_grouping_semantics[concrete]` became
  the refusal test; `repo: "extra_frame"` became an unresolved-input + SpellMap pair; cache pins carry 20. One
  rule was added during the sweep: a Protocol annotation also matches the Protocol's own definition (bound
  resolvable=False), so the OVERRIDE_REQUIRED socket of a descriptive definition still compiles; the resolvable
  preference picks a recorded implementer over it (fourth index map `by_definition`, unit-tested).
  EVIDENCE:
  - artifacts/annotation_category_collision_20261003/fix/landing/tier_unit_final.txt:1-1
  - artifacts/annotation_category_collision_20261003/fix/landing/tier_component_final.txt:1-1
  - artifacts/annotation_category_collision_20261003/fix/landing/tier_integration_final.txt:1-1
  - artifacts/annotation_category_collision_20261003/fix/landing/tier_other_final.txt:1-1
  - artifacts/annotation_category_collision_20261003/fix/landing/apply_kind_matching_src.py:1-1270
  - artifacts/annotation_category_collision_20261003/fix/landing/apply_kind_matching_tests.py:1-1382
  IMPACT: the change set is ready to land in the tree by script; the docs, notch, note and rebuild follow.
  NEXT: apply both scripts to the tree, copy the restore test, run the touched tiers from the tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T11:30:00Z
  TYPE: MEASURE
  CLAIM: TREE LANDED (01:55-02:12Z): both apply scripts ran end-to-end on the tree and the restore test was copied;
  tree files are byte-identical to the mirror's. Tree tiers (mount, by directory because the mount is ~5x slower):
  unit 8886 passed / 3 failed - the three failures are test_method_inspector.py (Windows path in the traceback,
  source preview None), an environment failure of the mount that passes on the mirror and is unrelated to this
  change; component 2293 passed; tests+experimentation+experiments 250 passed; integration spellbook 601 passed /
  3 failed under xdist (test_spellbook_integration.py::test_bind_conjure_and_meld_existing_creation, two in
  test_spellbook_integration_resolution_contract.py) that pass alone - order-dependent, pre-existing; integration
  aether 772 passed; integration conduit 275 passed. The crystallizer/live_sim/multithreading/mutation_research
  chunk did not finish inside the tool timeout (tree_integration_rest.txt is empty) and is re-run below.
  EVIDENCE:
  - artifacts/annotation_category_collision_20261003/fix/landing/tree_unit.txt:1-4
  - artifacts/annotation_category_collision_20261003/fix/landing/tree_component.txt:1-1
  - artifacts/annotation_category_collision_20261003/fix/landing/tree_other.txt:1-1
  - artifacts/annotation_category_collision_20261003/fix/landing/tree_integration_spellbook.txt:1-5
  - artifacts/annotation_category_collision_20261003/fix/landing/tree_integration_aether.txt:1-2
  - artifacts/annotation_category_collision_20261003/fix/landing/tree_integration_conduit.txt:1-2
  IMPACT: the change set is on the tree; the remaining tree evidence is one chunk; docs, notch, note and rebuild follow.
  NEXT: owner's regression additions (next note), then the remaining chunk from the tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T11:30:00Z
  TYPE: DECISION
  CLAIM: OWNER DIRECTIVE (chat, 2026-10-03 20:09 local, interrupting the last chunk run): "make sure you make
  regression tests as well please just incase". Added on the tree, run green: three Spell field tests (kind
  defaults to `none` with no contracts; kind + contracts pass through the ctor and survive cleanup; a category
  binding records the label and no contract) in test_spell.py; a SpellframeKind enum test module (three members,
  value == name, package-root export); the MelderOps-shaped integration case in the regression module (host
  unique at ("spectrum","Spectrum"), two named existing-object configs, two managers and a function spell in the
  "spectrum" category, CommandCenter `spectrum: Spectrum` bound many at "command_center", melded with
  `override={"spectrum": host}` and without; 14 passed). Still to write: an index-graft round trip of a
  Protocol-framed spell (modelled on test_index_graft_round_trips_into_a_live_host_book), asserting the grafted
  Spell's `spellframe_kind is SpellframeKind.contract` and `implemented_protocols == (IRestoreService,)`.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spell.py:1511-1581
  - tests/unit/melder/spellbook/spellframe_kind/test_spellframe_kind.py:1-26
  - tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py:397-515
  IMPACT: the EXIT_GATE's regression list grows by the Spell fields, the enum and the consumer-shaped case; the
  new files must be copied to fix/landing and the mirror before the tiers are called final.
  NEXT: write and run the graft round trip, copy the new tests to the artifact folder and the mirror, run the
  remaining tree chunk.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T11:55:00Z
  TYPE: MEASURE
  CLAIM: LANDED AT 0.2.8222 (notched from 0.2.8221). Owner-directed close (chat, 2026-10-03 23:34 local: "finish that
  shit on my machine and call it and ask me to run tests"): the full tiers were NOT re-run after the last
  regression additions and the crystallizer/live_sim/multithreading/mutation_research integration chunk was never
  completed from the tree - the owner runs them. What ran green on the tree after landing: the regression module
  (14), the restore/graft module (3: Protocol frame restored as a contract, unimportable Protocol degrades with a
  shortfall, index graft carries the kind into the host book - the source world is torn down first because a live
  member cannot be grafted into a second frame under process-wide ids, EPIC-2026-08-02), test_spell.py +
  test_spellframe_kind.py (107). Docs: README spellframe/DI sections, src_architecture (kind invariant; 0.2.8218
  entry marked superseded; two failure modes; code map; sources; handoff), src_components (Binding Pipeline,
  SpellCompiler, Crystallizer entries; collection DI flow; handoff), both indexes regenerated and checked; graph:
  new spellframe_kind descriptor authored, nine touched nodes re-authored and accepted, assembled and checked
  (586 sections / 1215 nodes). Release note: section led "**Breaking change:**" replacing the 0.2.8218 section;
  Packaging bullets (bind-guard 621 entries at 0.2.8222 - `SpellframeKind` joined; docs). The VM restarted mid-pass
  (/sessions disk full; /tmp lost): the mirror is gone and was not rebuilt, all remaining work ran on the tree.
  EVIDENCE:
  - src/melder/__version__.py:41-41
  - release_docs/next_version_release.md:408-446
  - system_docs/src_architecture.md:919-940
  - system_docs/src_components.md:641-660
  - tests/integration/melder/crystallizer/test_restore_spellframe_kind_integration.py:236-283
  IMPACT: the EXIT_GATE's tier item is owner-owed (commands in the summary); everything else is met.
  NEXT: closures, boards, patch docs archived, follow-up tickets, rebuild last; the owner runs the four tiers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T12:10:00Z
  TYPE: MEASURE
  CLAIM: TURN-IN COMPLETE. Closures: both tasks in tickets/tasks/completed/, story and epic at `review` (owner-owed
  tiers + Actions acceptance), the attention row replaced by `annotation_kind_matching_acceptance` routing to the
  story (NOTICE for fable_0 carried in its detail), two closed anchors added, the five patch docs archived to
  system_docs/patches/completed/annotation_kind_matching_2026_10_04/ and cleared on the artifact board, the
  evidence folder re-pointed to the story, two backlog follow-ups opened. Rebuild last: asset runner WROTE three
  manifests at 0.2.8222 (bind-guard 621 entries) and `--check` printed three OK lines; `llm_support/_builder.py
  --include-untracked` wrote src 578 / tests 1060 / other 385 files and `--check --include-untracked` printed three
  OK lines. Delete permission on the connected folder was re-granted after the VM restart for the payload unlink.
  EVIDENCE:
  - attention_board.md:171-171
  - artifact_board.md:89-96
  - tickets/tasks/backlog/2026-10-04_deepen_protocol_contract_check_task.md:1-20
  - tickets/tasks/backlog/2026-10-04_explicit_implements_bind_argument_task.md:1-20
  IMPACT: nothing is owed by an agent on this lane until the owner reports the tiers and the Actions case.
  NEXT: none (owner).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-10-04T11:55:00Z: DONE (owner directive). Landed at 0.2.8222 with docs, graph, release note, assets and
bundles current; the four tiers after the final regressions are owner-owed (commands in the Validation section).
Follow-ups live in tickets/tasks/backlog/.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
