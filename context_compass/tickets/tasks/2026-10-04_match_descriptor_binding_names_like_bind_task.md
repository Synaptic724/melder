# Task: Make SpellMap and SpellContract keep and match binding names the way Bind does

## Metadata
- Task ID: TASK-2026-10-04-match_descriptor_binding_names_like_bind
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-04T21:00:53Z
- Updated: 2026-10-04T21:37:58Z

## Objective
`bind(binding_name="ScanProfile")` and `SpellMap(..., binding_name="ScanProfile")` must name the same
provider: the descriptors keep the caller's text like Bind, Phase 3 resolves a SpellMap default by the same
case-insensitive key bind and meld use, and a regression test pins bind, SpellMap, SpellContract and meld
to one pattern.

## Ticket Contract
- ENTRY_GATE: The owner's chat directives of 2026-10-04 ("I need to make sure spellmap and spellcontract
  behave the way bind does"; "make a regression test for bind/spellmap/spellcontract"). Active board row:
  descriptor_binding_name_case. Patch docs under system_docs/patches/active/spellmap_binding_name_case_2026_10_04/.
- EXECUTION_BOUNDARY: spell_map.py, spell_contract.py, compiler_phase_3.py (`_resolve_spellmap_default`
  and one helper), spellmap_shape_validation_strategy.py (the lowercase warning), structural_snapshot.py
  (the SpellMap binding row), their tests plus a new regression test file, the system docs and graph
  descriptors that state the rule, `__version__` and the running release note, regenerated assets and
  bundles. No commit, push or PR.
- DEPENDENCIES: the CI task of this session shares the final llm_support rebuild:
  tickets/tasks/2026-10-04_use_newest_patch_in_single_version_ci_jobs_task.md.
- EXIT_GATE: mixed-case SpellMap defaults resolve; the regression and touched tiers pass or are reported Not
  run; asset, graph, index and bundle checks print OK; the owner accepts.
- FAILURE_ESCALATION: Record BLOCKER if a tier cannot run on the device VM, or CONFLICT if a test pins a
  behaviour the owner's directive contradicts beyond the two named in Note 2.

## Scope Boundaries
- In scope: descriptor storage, Phase 3 SpellMap matching (binding names and string frames), the retired
  Phase-4 warning, the snapshot row, tests, docs, notch.
- Out of scope: Meld and SpellContract key resolution (already case-insensitive), annotation matching by
  kind, Nexus spell records, constructor signatures.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-04T21:37:58Z) implemented, validated, documented, notched and rebuilt (Notes 5-8); the
  owner's acceptance, commit and push remain; the llm_support rebuild follows this note as the last write.
- previous: draft -> in_progress (2026-10-04T21:00:53Z) on the owner's chat directives (Notes 1-4).

## Steps / Checklist
- [x] Investigate Bind, the descriptors, Phase 3 and every reader of a descriptor's binding name (Notes 1-2).
- [x] Descriptors keep binding_name as given; TypeError for a non-string name.
- [x] Phase 3 matches by normalized binding and string-frame keys.
- [x] Retire SPELLMAP_BINDING_NAME_NOT_NORMALIZED; keep the snapshot row byte-identical.
- [x] Invert the pinned tests (four); add the bind/SpellMap/SpellContract/meld regression tests.
- [x] Run the touched unit, component and integration files and the regression file.
- [x] System docs, graph descriptors, notch 0.2.8226, release note, notch notice.
- [x] Rebuild assets and graph and run every --check; llm_support is rebuilt after this note (result in chat).

## Deliverables
- Descriptor and Phase 3 fix; retired warning; regression tests; docs; version 0.2.8226; rebuilt assets.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/contracts/spell_map.py
- src/melder/aether/conduit/meld/contracts/spell_contract.py
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py
- src/melder/aether/spellbook/spell_compiler/validation/strategies/spellmap_shape_validation_strategy.py
- src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py
- tests (two pinned tests; new regression file)
- context_compass/system_docs (src_components, src_architecture, graph descriptors, indexes)
- src/melder/__version__.py, release_docs/next_version_release.md, generated assets, llm_support/

## Validation
- 2026-10-04, device VM, uv CPython 3.14.7t, pytest 9.1.1, -X gil=0 (Notes 6-8):
  - Touched and new files 227 passed; red check on HEAD's code: 8 of 9 regression cases failed.
  - tests/unit/melder 8411 passed; tests/unit outside melder and llm_support 495 passed.
  - Component: spellbook 791, the rest 739 passed. Integration: spellbook 613 (2 unrelated XPASS),
    conduit and component conduit 1038, aether and multithreading 824, live_sim 1 passed.
  - Docs (CPython 3.14.7 GIL build, docs/requirements.txt): unittest OK; build_docs.py check OK (301 pages).
  - Asset runner --check OK x3 (v0.2.8226); index checks OK x4; graph 587 ranges verified.
- Not run: integration crystallizer and mutation_research (no descriptor use there; call cap), the owner's
  Windows tiers, llm_support --check (runs after this note; result in chat).

## Risks / Rollback Notes
- Risk: consumers with mixed-case descriptor binding names get a new spell id once; a recorded crystal maps
  through restore's id translation and caches go cold once (the notch already does that).
- Rollback: patch doc rollback section.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - system_docs/patches/active/spellmap_binding_name_case_2026_10_04/architecture_patch.md
  - system_docs/patches/active/spellmap_binding_name_case_2026_10_04/component_patch_di_descriptors.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: on closure, move the patch folder to system_docs/patches/completed/

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
- DATETIME: 2026-10-04T21:00:53Z
  TYPE: FACT
  CLAIM: Bind stores `binding_name` on the Spell exactly as given and keys it through
    make_spell_key_from_parts, which lowercases both parts. SpellMap and SpellContract instead store
    normalize_binding_name(binding_name), the lowercase key. Phase 3's `_resolve_spellmap_default`
    compares the Spell's raw name with the descriptor's lowercase one (and raw spellframes, so string
    categories are case-sensitive there), so `SpellMap(spellframe="agents", binding_name="ScanProfile")`
    never matches `bind(..., binding_name="ScanProfile")` and raises "SpellMap default could not be
    resolved" (the owner's 0.2.8224 report). SpellContract is resolved by canonical_key (Meld and the
    Phase-4 provider check), so it already matches case-insensitively; only its stored value differs.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:442-442
  - src/melder/aether/spellbook/spell.py:540-546
  - src/melder/utilities/helpers/general_helpers.py:240-274
  - src/melder/utilities/helpers/general_helpers.py:331-359
  - src/melder/aether/conduit/meld/contracts/spell_map.py:188-202
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:182-197
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:770-843
  - src/melder/aether/conduit/meld/meld.py:1303-1308
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:190-193
  IMPACT: The documented remedy for an ambiguous provider (a SpellMap default naming the binding) fails
    for any binding name with a capital letter.
  NEXT: Record the other readers of a descriptor's binding name and the tests that pin lowercasing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T21:00:53Z
  TYPE: FACT
  CLAIM: Only two other code paths read a descriptor's stored binding name: the structural snapshot's
    SpellMap reference row and the Phase-4 SpellMapShapeValidationStrategy, which warns
    SPELLMAP_BINDING_NAME_NOT_NORMALIZED (advising lowercase) whenever the stored value is not lowercase.
    Two tests pin the lowercasing (one asserts it at construction, one mutates the field to trip the
    warning). The bind fingerprint hashes parameter-default text, and a descriptor's repr carries its
    binding name, so a consumer with a mixed-case descriptor name gets a new spell id once.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:200-219
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/spellmap_shape_validation_strategy.py:146-165
  - tests/integration/melder/spellbook/test_spellbook_integration_di_shape_compiler_matrix.py:638-644
  - tests/component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_strategies.py:340-405
  - context_compass/system_docs/src_architecture.md:1179-1185
  IMPACT: Keeping the snapshot row on the normalized value keeps rows and caches byte-identical; the warning
    loses its premise once matching is case-insensitive.
  NEXT: Record the decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T21:00:53Z
  TYPE: DECISION
  CLAIM: The owner's directive is the confirmation; the defaults were told to the owner in chat before any
    edit: both descriptors keep `binding_name` as given (TypeError for a non-string name); Phase 3 compares
    binding names by normalize_binding_name on both sides (None and "" are the default binding, as in the
    key) and string spellframes by normalize_frame_key, class and Protocol frames staying identity matches;
    SPELLMAP_BINDING_NAME_NOT_NORMALIZED is retired; the snapshot row records the normalized name, so rows
    are byte-identical and no cache generation moves; notch 0.2.8226. Patch docs written (system-impacting:
    src_components states the old rule).
  EVIDENCE:
  - context_compass/system_docs/src_components.md:900-901
  - context_compass/system_docs/patches/active/spellmap_binding_name_case_2026_10_04/architecture_patch.md:1-41
  - context_compass/system_docs/patches/active/spellmap_binding_name_case_2026_10_04/component_patch_di_descriptors.md:1-25
  IMPACT: SpellMap selects exactly what bind registered and meld finds; SpellContract keeps its behaviour
    and shows the caller's text.
  NEXT: Record the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T21:00:53Z
  TYPE: PLAN
  CLAIM: Patch mapping: architecture_patch (invariants, interface deltas, migration order) -> descriptors,
    Phase 3, strategy, snapshot -> unit and component tests on those files plus the inverted pinned tests;
    component_patch (before/after, validation) -> a regression file binding providers as
    ("agents", "ScanProfile") and ("artificial_intelligence_tools", "ScanProfile") and proving SpellMap
    (mixed, lower and upper case; frame-only and explicit), SpellContract (canonical key and a linked
    dynamic provider) and meld all select the same provider, with the descriptors keeping the caller's text.
    Then the docs, graph, notch, release note, and last the assets, graph and llm_support rebuild.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spellmap_binding_name_case_2026_10_04/architecture_patch.md:31-33
  - context_compass/system_docs/patches/active/spellmap_binding_name_case_2026_10_04/component_patch_di_descriptors.md:22-25
  IMPACT: Every patch section maps to an edit and a check.
  NEXT: Edit spell_map.py and spell_contract.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T21:09:35Z
  TYPE: FACT
  CLAIM: Applied. Both descriptors keep `binding_name` as written and raise TypeError for a non-string name;
    Phase 3 compares binding names by normalize_binding_name on both sides and frames through the new
    `_spellmap_frame_matches` (string categories by normalize_frame_key, anything else by identity or
    equality); SpellMapShapeValidationStrategy no longer emits SPELLMAP_BINDING_NAME_NOT_NORMALIZED (its now
    unused SpellInputUtils import removed, docstrings say why); the snapshot row records the normalized
    name. Correction to Note 2: four tests pinned the lowercasing, not two - the SpellMap and SpellContract
    unit tests did too; all four are inverted under the same directive (same behaviour, no new conflict).
    New: test_binding_name_case_parity_integration.py (bind/SpellMap/SpellContract/meld share one address;
    five SpellMap spellings; three SpellContract spellings over a conduit link) and four Phase 3 unit tests.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_map.py:197-207
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:191-202
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:770-881
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/spellmap_shape_validation_strategy.py:144-146
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:218-223
  - tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py:1-168
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:1093-1162
  IMPACT: SpellMap selects what bind registered and meld finds; SpellContract keeps working and shows the
    caller's text.
  NEXT: Run the touched files, a red check against HEAD, then the wider tiers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T21:09:35Z
  TYPE: MEASURE
  CLAIM: Device VM, uv CPython 3.14.7t, pytest 9.1.1, -X gil=0, bytecode writes off: the eight touched or new
    test files gave 227 passed. Red check: with HEAD's spell_map.py, spell_contract.py and compiler_phase_3.py
    copied in, the regression file gave 8 failed, 1 passed (every SpellMap case failed with "SpellMap
    default could not be resolved"; the passing case is the lowercase SpellContract, whose resolution was
    already key-based); the three files were restored from byte copies (cmp clean) and it gave 9 passed.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py:104-168
  IMPACT: The regression tests fail on the reported defect and pass on the fix.
  NEXT: Run tests/unit/melder in shards and the spellbook/conduit component and integration folders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T21:23:52Z
  TYPE: MEASURE
  CLAIM: Wider tiers, device VM, uv CPython 3.14.7t, pytest 9.1.1, -X gil=0, bytecode writes off:
    tests/unit/melder 8411 passed, 3 skipped, 7 xfailed (spellbook 2280, aether 4192, the rest 1939);
    tests/component/melder/spellbook 791 passed; the other component folders 739 passed, 23 skipped,
    1 xfailed; tests/integration/melder/spellbook 613 passed, 2 skipped, 2 xpassed; integration conduit plus
    component conduit 1038 passed; integration aether plus multithreading 824 passed; live_sim 1 passed,
    1 xfailed. The two XPASS are the non-strict "Fault B" annotation-guard cases in
    test_spellbook_integration_di_validation_faults.py; they assert annotation-shape codes, not binding names
    (unrelated, not investigated). Not run: tests/integration/melder/crystallizer and mutation_research (no
    file there uses SpellMap or SpellContract; the 172 s call cap stopped them at 21%), the Windows tiers.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_di_validation_faults.py:211-235
  IMPACT: No regression anywhere the descriptors are used; docs, notch and rebuild come next.
  NEXT: Update src_components, src_architecture and the graph descriptor, notch 0.2.8226, release note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T21:37:58Z
  TYPE: MEASURE
  CLAIM: Documented and rebuilt. src_components (DI Descriptors invariant and failure mode, both descriptor
    subcomponents, the Phase-3 SpellMap flow, code-map extents 359 and 351, handoff) and src_architecture
    (an operational invariant, a failure mode, code-map entries, sources, handoff) state the rule; both
    indexes regenerated and all four index checks print OK. Graph: extract --strict wrote 587 descriptors
    (0 skipped); the strategy's prose no longer claims the warning, SpellMap and SpellContract gained the
    rule and lost the stale `spell_override` slot name, CompilerPhase3 gained the matching rule; the six
    nodes whose source I read whole (both descriptor modules and classes, the strategy module and class) are
    accepted and written back in the extractor's indent-1 format (graph_walker writes indent 2);
    CompilerPhase3 stays SEMANTICS_STALE (not read whole); assemble verified 587 ranges. Version 0.2.8226,
    the release-note section "Fixed: a SpellMap or SpellContract binding name matches the way bind and meld
    do" with its packaging line, and the board notch notice. The asset runner wrote three assets at
    v0.2.8226 (462, 622 and 4 entries) and --check prints only OK; unit tests outside melder and llm_support
    495 passed; docs unittest OK and build_docs.py check OK.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:900-910
  - context_compass/system_docs/src_architecture.md:919-933
  - release_docs/next_version_release.md:495-526
  - src/melder/__version__.py:12-12
  IMPACT: Every gate this agent owns is met except the llm_support rebuild, which runs next as the last write.
  NEXT: Rebuild llm_support with --include-untracked and run --check (reported in chat); the owner commits
    everything (the five new files, the deleted artifact .gitignore and the root .gitignore included) and
    pushes, then accepts or redirects; on acceptance, promote the patch docs and close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Done (Notes 5-8): SpellMap and SpellContract keep binding_name as written, Phase 3 matches by the normalized
binding and string-frame keys, the lowercase warning is retired, regression tests pin bind/SpellMap/SpellContract/
meld to one address (red on the old code), docs/graph/notch 0.2.8226/release note/assets are current. Owner-owed:
commit and push everything, acceptance; then promote the patch docs and close. llm_support rebuilt after Note 8.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
