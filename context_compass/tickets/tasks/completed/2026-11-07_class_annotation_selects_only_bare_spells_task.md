

# Task: class_annotation_selects_only_bare_spells - a spellframe or a binding name hides the class from class lookups, as in the meld door

- Completed: 2026-11-07T15:06:23Z
- Summary: Landed as 0.2.8278 (notched 0.2.8278; release-note section "A class lookup reaches only a spell bound bare",
  Breaking). Phase 3's class lookups - a class annotation, a single string's type part, `list[Class]`,
  `SpellMap(Class)` - reach only a spell with no spellframe and the default binding (`_answers_class_lookup`, scan
  and index alike; Protocol definitions keep their definition key on a name); cache generation 26; 106 measured tests
  rewritten or converted plus C4 and the cache-history pin; docs, system docs, indexes and graph merged from patch
  class_lookup_bare_spells_2026_11_07. Validation: full suite the GIL off and on identical (the 9 standing failures,
  plus the build-asset stamp until the rebuild), S1 matrix with no key-split MISS, examples unchanged. Not
  committed; the rebuild and its checks run last (Notes).

## Metadata
- Task ID: TASK-2026-11-07-class_annotation_selects_only_bare_spells
- Story: none - an epic-level task of EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Status: done
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-11-07T10:03:26Z
- Updated: 2026-11-07T15:06:23Z

## Objective
A class lookup - a class annotation, a string naming a class, `list[Class]` and `SpellMap(spell=Class)` - reaches a
spell only when it is bound bare: no spellframe and no binding name, the class, or an existing object of it, as
itself (Autofac: a declared service hides the component's own type; the owner's rulings E1-E3, 2026-11-07). A spell
bound under a spellframe is reached through the frame - Melder's interface dict: a Protocol annotation,
`list[Protocol]`, `SpellMap(spellframe=..., binding_name=...)`, `meld(spellframe=..., binding_name=...)`; a bare
spell with a binding name through `SpellMap(Class, binding_name=...)` or `meld(Class, binding_name=...)`. Land it as
one change set: source, tests, docs, release note, notch, rebuild.

## Ticket Contract
- ENTRY_GATE: T1 done (completed 2026-11-07T11:57:30Z); its edge cases decided by the owner; the owner's go to
  implement ("discuss this with me before you do it", chat 2026-11-07); a board row routes here.
- EXECUTION_BOUNDARY: compiler_phase_3.py (the two type-key predicates, the SpellMap explicit-spell branch, their
  docstrings); the 106 tests in 20 files T1 measured; docs and docstrings listed in Notes; the creation-cache
  generation; src_architecture/src_components and their indexes; release_docs/next_version_release.md;
  __version__; the asset and llm_support rebuild last.
- DEPENDENCIES: TASK-2026-11-07-inventory_class_resolution_of_framed_spells (completed).
- EXIT_GATE: the rewritten tests assert this contract and the converted ones keep their intent, the full suite
  passing the GIL off and on but for the 9 standing failures of the enum lanes; the S1 matrix and the interface
  check re-run with no key-split MISS; the example suite unchanged; release note (Breaking), notch and both
  `--check` runs green.
- FAILURE_ESCALATION: DECISION_REQUEST when a converted test encodes intent the owner may want kept; CONFLICT if
  another lane holds the files.

## Scope Boundaries
- In scope: type-key matching (class annotation, the type part of a single string annotation, `list[Class]`);
  `SpellMap(spell=X)` without a spellframe; existing objects alike; the creation-cache generation (26).
- Out of scope: the frame doors (unchanged - the owner's interface-dict model, option (a), documented only), the meld
  doors (already address lookups), Bind and addresses, SpellContract (already address-based), Protocol/definition
  and label matching, the Phase 4 check (T3), an AsSelf-style option (declined for now, 2026-11-07).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: every step done and validated (Notes 13:59:04Z, 15:02:53Z, 15:06:23Z); the owner's go to turn
  in (chat 2026-11-07, "fix the test and continue those things you said"); the rebuild and its checks follow as the
  contribution guide's last step.
- earlier: ready -> in_progress (the owner settled all 13 points and gave the go, chat 2026-11-07, "ok yes to all
  your statements"; epic Decision Log 2026-11-07T12:08:59Z; melder_0 re-certified after compaction, chat
  2026-11-07T13:46:19Z, and started with the Phase 3 change).
- earlier: draft -> ready (T1 completed and the owner decided E1-E3, chat 2026-11-07).

## Steps / Checklist
- [x] Patch gate: class_lookup_bare_spells_2026_11_07 written, linked, read and mapped (Notes 13:48:07Z).
- [x] Phase 3: `_spell_keys_for` (type row, and the type part of a single name) and `_build_candidate_index`
      (`by_type`) admit a spell only with no spellframe and the default binding - scan and index paths alike.
- [x] Phase 3: `_resolve_spellmap_default`'s explicit-spell branch without a spellframe admits only an X bound with no
      spellframe, and with no binding name given only the default binding.
- [x] Docstrings: the CompilerPhase3 class docstring (still the superseded 2026-10-03 rule), `_spell_keys_for`'s
      table, `_matches_annotation`, `_build_candidate_index`, `_index_buckets_for`, `_resolve_single_by_annotation`,
      `_resolve_spellmap_default`; SpellMap's class docstring (the explicit-spell shape).
- [x] Rewrite the 41 tests that assert the old rule (6 files) to the new contract, the S1 file's 14 xfails included.
- [x] Convert the 65 tests whose fixtures reach a provider through a spellframe or binding name (14 files); C4
      rewritten on the owner's word; three hollowed passing tests and the cache-history pin updated too.
- [x] Creation-cache generation 26 with its history line.
- [x] Docs: README (DI section, SpellMap section, the interface-dict reading of the frame doors), handbook example 25
      ("frames are NOT dicts"), agents/MELDER_AGENT_OPERATIONS.md (the `SpellMap(Store)` row), UX AGENTS.md's address
      law if it states the old class rule [done 13:57:51Z]; src_architecture and src_components entries with their
      indexes, and the source graph [merged by subagent, both index checks OK, graph check 593 ranges].
- [x] Release note section leading with **Breaking change:** and the upgrade paths; notch; rebuild and `--check` last
      [release note and notch done; the rebuild runs after this closure].
- [x] Validate: full suite the GIL off and on; the S1 matrix probe and the interface check re-run; the example suite.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The class-lookup rule in src with tests and docs; the release-note section; the notch; green checks.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py
- src/melder/aether/conduit/meld/contracts/spell_map.py (docstring only)
- src/melder/utilities/caching_system/caching_system.py (generation 26)
- the 20 test files listed in Notes (2026-11-07T11:57:30Z)
- README.md, UX_and_AIX_experiences/01_beginner/25_frames_as_dict_classification.py,
  agents/MELDER_AGENT_OPERATIONS.md, UX_and_AIX_experiences/AGENTS.md (if it states the old class rule)
- context_compass/system_docs/src_architecture.md, src_components.md and their indexes
- release_docs/next_version_release.md, src/melder/__version__.py

## Validation
- Run (0.2.8278 working tree, .venv_new 3.14.7t): full suite the GIL off and on, identical - 15632 passed, 11
  failed (the 9 standing failures of 0.2.8277; C4, since rewritten and passing 19/19 in its file both modes; the
  build-asset stamp, cleared by the rebuild), 12 xfailed, 2 xpassed (both pass on 0.2.8277 too); the S1 matrix (3
  MISS per mode, none a key split); the interface check; the example suite (617 passed, the same 10 standing
  failures); each subagent's files both modes. Runs in context_compass/artifacts/dependency_watchers_20261107/runs/
  (*_0_2_8278*). The post-rebuild run is appended in Notes.
- Recommended commands:
  - `.venv_new/Scripts/python.exe -X gil=0 -m pytest tests -q` and the same with `-X gil=1`
  - `.venv_new/Scripts/python.exe -X gil=0 -m pytest UX_and_AIX_experiences/pytest_examples -q`
  - `bash context_compass/artifacts/dependency_watchers_20261107/probes/run_probe_watcher_announcer_matrix.sh`
  - `python src/melder/_build_assets/_build_asset_runner.py` then `--check`; `python llm_support/_builder.py` then `--check`
- Baseline before the change (c6778e303, the GIL off): 18 failures in the probe runs, 9 of them the probe's cache
  redirect; 9 standing failures of the enum lanes (T1 Notes 10:49:50Z) that this task neither causes nor fixes.

## Risks / Rollback Notes
- Breaking for class consumers of framed or named spells; rollback is the revert of the change set (no record format
  moves; the creation cache goes cold once, as with any release).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/dependency_watchers_20261107/ (the matrix and interface checks to re-run)
  - artifacts/dependency_watchers_20261107/probes/strict_class_match_plugin.py (T1's probe; mode 2 is this rule)
  - artifacts/dependency_watchers_20261107/runs/suite_autofac_reading_0_2_8277_diff_gil0.txt (the test list)
  - system_docs/patches/completed/class_lookup_bare_spells_2026_11_07/architecture_patch.md (moved from active/)
  - system_docs/patches/completed/class_lookup_bare_spells_2026_11_07/component_patch_compiler_phase_3.md
  - system_docs/patches/completed/class_lookup_bare_spells_2026_11_07/component_patch_creation_cache_generation.md
  - artifacts/dependency_watchers_20261107/probes/c4_world_probe.py (C4's world through class and frame)
- DISPOSITION: retain_as_reference (the artifact folder); promote_to_documentation (the patch docs)
- CLEANUP_TRIGGER: the before/after runs land beside the 0.2.8277 ones; the patch docs are merged into
  src_architecture/src_components and moved to system_docs/patches/completed/ at turn-in

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the strict class-resolution contract
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-11-07T10:03:26Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-11-07T10:03:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The change is the type row of Phase 3's matching table - a class annotation compares the spell's type key
    whatever its frame - applied identically in the scan and index paths; the 14 strict xfails in the S1 regression
    file were written for the other option and become assertions that a class consumer stays unresolved.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:545-574
  IMPACT: One rule for injection and the meld door; the key split cannot occur.
  NEXT: Wait for T1's inventory and the owner's edge-case decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-11-07T11:57:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The change list, from T1 (completed) and the owner's rulings. SRC: in Phase 3 a spell answers a class
    lookup only with no spellframe and the default binding - `_spell_keys_for` (the type row; a single name keeps its
    contract keys) and `_build_candidate_index` (`by_type`), scan and index alike; `_resolve_spellmap_default`'s
    explicit-spell branch without a spellframe admits only such an X when no binding name is given and an X bound
    bare under that name when one is; docstrings as listed in Steps; cache generation 26. TESTS, rewrite to the new
    contract (41 in 6 files): test_compiler_phase_3 15, the S1 file 14, annotation_category_collision 9,
    spell_crafter's SpellMap stub 1, resolution_break_matrix b3 1, resolution_contract_more ambiguous-concrete 1.
    TESTS, convert the fixture (65 in 14 files): injected_provider_direct_meld 13, notch_refused_at_commit 11 (needs
    another structural failure), provider_artifact_ownership 7, existing_instance regressions 6 and planning 3,
    the borrower experiment 6, change_control 5, structural_snapshot_parity 4, validation_system 3, di_shape matrix
    2, phase5_contracts 2, resolution_error_matrix 1, notch_revalidation 1, rebind_after_first_meld 1. RELEASE NOTE
    upgrade paths: a class under a Protocol, annotate the Protocol or use `SpellMap(spellframe=P, binding_name=...)`;
    a class under a category spelled as its own name, drop the spellframe (same address); a bare class with a
    binding name, `SpellMap(Class, binding_name=...)` or drop the name; `SpellMap(Class)` for a framed or named
    class, add its spellframe/binding_name; existing objects alike.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-11-07_inventory_class_resolution_of_framed_spells_task.md:144-173
  - context_compass/tickets/tasks/completed/2026-11-07_inventory_class_resolution_of_framed_spells_task.md:274-299
  - context_compass/tickets/tasks/completed/2026-11-07_inventory_class_resolution_of_framed_spells_task.md:390-426
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_autofac_reading_0_2_8277_diff_gil0.txt:1-235
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:472-519
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:796-881
  IMPACT: T2 is bounded and measured; nothing in it waits on a decision.
  NEXT: The owner's go, then the Phase 3 change first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T13:48:07Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch gate (engineer patch_framework_gating: the change updates src_architecture and src_components). Patch
    class_lookup_bare_spells_2026_11_07 is written, linked (Artifact Links) and read in the consumption order:
    architecture patch, then component_patch_compiler_phase_3, then component_patch_creation_cache_generation; no
    code_description_patch (no control-flow, gate-pipeline, error-semantics or concurrency change - stated in the
    architecture patch). Mapping, patch section -> implementation step -> validation step:
    (1) arch "Interface delta 1" + phase-3 "After" (type row, single name's type part, `by_type`) -> one predicate
    `CompilerPhase3._answers_class_lookup` (no spellframe, default binding) read by `_spell_keys_for` and
    `_build_candidate_index` -> test_compiler_phase_3 scan and index cases, the S1 file's 14 cases.
    (2) arch "Interface delta 2" + phase-3 "After" (SpellMap) -> `_resolve_spellmap_default`'s explicit branch
    without a spellframe -> test_compiler_phase_3 SpellMap cases, spell_crafter's SpellMap stub, break-matrix b3.
    (3) arch invariant 4 + phase-3 ordering 1 -> both paths in one edit -> scan/index parity cases.
    (4) cache patch -> generation 26 with its history comment -> caching-system unit tests.
    (5) arch rollout 3-5 -> tests, docs, release note, notch, rebuild -> the full suite the GIL off and on, the S1
    matrix and interface-check re-runs, the example suite, both `--check` runs.
  EVIDENCE:
  - context_compass/system_docs/patches/active/class_lookup_bare_spells_2026_11_07/architecture_patch.md:1-95
  - context_compass/system_docs/patches/active/class_lookup_bare_spells_2026_11_07/component_patch_compiler_phase_3.md:1-78
  - context_compass/system_docs/patches/active/class_lookup_bare_spells_2026_11_07/component_patch_creation_cache_generation.md:1-53
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:472-519
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:796-881
  - context_compass/artifacts/dependency_watchers_20261107/probes/strict_class_match_plugin.py:87-103
  IMPACT: The patch gate is met (docs exist, linked, read, mapped), so the Phase 3 edit can start; the predicate is
    the one T1's probe measured in mode 2 (spellframe, or a non-default binding name, hides the type).
  NEXT: Edit compiler_phase_3.py (predicate, the two type-key sites, the SpellMap branch, docstrings).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T13:51:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Src landed in the working tree (not committed, no notch yet). `CompilerPhase3._answers_class_lookup` (no
    spellframe, binding name normalizing to `__default__`) is read by `_spell_keys_for` (type row empty for a hidden
    spell; a single name keeps only its contract keys), by `_build_candidate_index` (`by_type` holds only answering
    spells) and by `_resolve_spellmap_default`'s explicit branch without a spellframe (a framed X skipped; with no
    binding_name only the default binding). Docstrings updated: the class docstring (it still stated the superseded
    2026-10-03 address-key rule), the table, `_matches_annotation`, `_build_candidate_index`, `_index_buckets_for`,
    `_indexed_annotation_candidates`, both annotation resolvers, `_resolve_spellmap_default`; SpellMap's class and
    `__init__` docstrings name the class lookup; cache generation 26 `class_lookup_bare_spells` with its history
    comment. First run, the GIL off: test_compiler_phase_3.py 15 failed and the S1 file 14 failed (their
    preconditions now read 'raises UnresolvedInputError') - exactly T1's measured cases in those two files.
    UNKNOWN (not this task's to fix): SpellMap's docstring shape `SpellMap(ILogic)` claims frame-based DI, while
    Phase 3's explicit branch matches `spell` by identity, so it reaches only the Protocol's own definition -
    unverified at runtime; left unchanged, raised with the owner.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:293-331
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:401-449
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:538-592
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:877-984
  - src/melder/utilities/caching_system/caching_system.py:245-283
  IMPACT: The rule is in place on both paths; the remaining test failures are the measured 106 to rewrite or convert.
  NEXT: Rewrite/convert the 106 tests (parallel subagents on disjoint files), then review their diffs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T13:57:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: In flight, the owner's subagent licence ("you can use subagents too"; onboarding without them): five
    subagents hold the 106 tests on disjoint files (A: test_compiler_phase_3 + spell_crafter + break_matrix b3 +
    contract_more; B: the S1 file + annotation_category_collision; C: injected_provider_direct_meld +
    notch_refused_at_commit + notch_revalidation + rebind_after_first_meld; D: provider_artifact_ownership + both
    existing_instance files + the borrower experiment; E: change_control + structural_snapshot_parity +
    validation_system + di_shape matrix + phase5_contracts + resolution_error_matrix), each running its files the
    GIL off and on; a sixth merges the patch into src_architecture/src_components and their indexes. Done here:
    test_cache_schema_version_integration's pinned history gains 26 (63 passed with test_caching_system, the GIL
    off); README (spellframe as interface dict, the DI class rule, SpellMap's class lookup), lesson 25's header,
    UX AGENTS.md's design principle, MELDER_AGENT_OPERATIONS' constructor table; the release-note section
    (Breaking, four upgrade paths, header 0.2.8278); the notch 0.2.8277 -> 0.2.8278 (no other agent active).
  EVIDENCE:
  - release_docs/next_version_release.md:1-52
  - src/melder/__version__.py:11-11
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:12-39
  IMPACT: The change set is complete but for the test conversions, the system docs and the validation runs.
  NEXT: Review each subagent's diff and results, then the full suite the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T13:59:04Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: On 0.2.8278 (working tree), the GIL off and on. The S1 matrix (run_probe_watcher_announcer_matrix.sh): MISS
    cells 22 per mode at 0.2.8277 -> 3 per mode; no key-split cell remains - the three left are D3 (cleanup_spell),
    G4 (remove_spell_from_contract) and H1 (transfer), bare-provider cells of S1's other misses, out of this epic
    (the owner: cleanup_spell after-effects are not a defect). E1 and P1a no longer read MISS (their worlds now read
    the same live and fresh). The interface check: `meld(English)` and `greeter: English` now agree - both refuse an
    English under `Greeter` (KeyError at the door, UnresolvedInputError at the meld); `greeter: Greeter`,
    AMBIGUOUS_PROVIDER for two named implementations and the frame melds are unchanged.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_0_2_8278.txt:419-419
  - context_compass/artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_0_2_8278.txt:514-514
  - context_compass/artifacts/dependency_watchers_20261107/runs/probe_watcher_announcer_matrix_0_2_8278.txt:530-530
  - context_compass/artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8278.txt:1-51
  IMPACT: The epic's exit gate "the S1 matrix re-run shows no key-split MISS" holds; the remaining MISS cells stay
    with EPIC-2026-10-25-dependency_watchers_listen_for_names.
  NEXT: Review the subagents' test diffs as they report.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T14:14:49Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: (1) Fixed in this change set: the first cut hid a Protocol definition (bound resolvable=False) under a
    binding name or spellframe from a string naming its Protocol (`x: "IRepo"`) while the Protocol object still found
    it - contrary to settled point 5 (definition matching unchanged) and to a TYPE_CHECKING string resolving as the
    class object does (found by subagent A's rewritten unit tests). A single-socket name now keeps a definition's
    definition key whatever its binding (`_spell_keys_for`), and the index reads `by_definition` for it
    (`_index_buckets_for`); only Protocol definitions carry that key, so no concrete class leaks; the component patch
    is amended first. (2) Subagent reports, each run here the GIL off and on: A (4 files) 201 passed, re-run pending
    for (1); C (4 files) 55 passed + C4 left failing on purpose; D (4 files) 43 passed, conversions checked against
    the reintroduced bugs; E (6 files) 104 passed, plus three passing tests converted that the rule had hollowed out
    (validation_system x2, phase5 x1) and the parity `[notch]` event now staging an edited Engine. B and the docs
    merge still running. (3) Pinned as they stand, consistent with the rulings: `list["Named"]` gathers a bare spell
    under any binding name through its label; `SpellMap(X, spellframe=F)` with no binding name reaches X under F at
    any binding.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:401-459
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:627-667
  - context_compass/system_docs/patches/active/class_lookup_bare_spells_2026_11_07/component_patch_compiler_phase_3.md:23-35
  IMPACT: Definition matching is unchanged for both annotation forms, as settled; the test work is 4 of 5 groups in.
  NEXT: The owner's call on C4 (DECISION_REQUEST below), then B, A's re-run, the docs merge and the full suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T14:14:49Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Two tests covered 0.2.8250's Breaking path "a notch to a version the class annotation does not select makes
    the dependent's next meld raise UnresolvedInputError" - test_conduit_integration_notch_revalidation.py's C4
    (`by_class` arm, left failing) and the structural-snapshot parity `[notch]` event (converted by E to an edited
    Engine of the same name, which the consumer builds). Under this rule plus one binding per index (0.2.8273) that
    path cannot be built with a class or string annotation: every version of a bare index carries the class's name
    and is selected (bind_inactive refuses a renamed or framed version, measured), and no version of a framed index
    is. Options: (a) rewrite C4 to the new invariant - a class consumer builds whatever version a notch makes active
    on a bare index (E's parity change already proves the same) - and note the old path unreachable; (b) cover the
    nearest still-reachable path, `SpellMap(Dep)` by identity after a notch to an edited Dep, which fails at Phase 3
    with RuntimeError "SpellMap default could not be resolved" - a different error and a different thing proved.
    Recommendation: (a), keeping (b) out unless the owner wants that error path pinned.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py:493-578
  - context_compass/system_docs/src_architecture.md:2775-2783
  IMPACT: Decides whether C4 is rewritten or replaced; nothing else waits on it.
  NEXT: Ask the owner with the other closing questions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T15:02:53Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The owner asked whether the change broke how index targeting works (chat 2026-11-07: "did you break how it
    works?"). Measured on C4's own world (Dep under the category "Dep", the renamed subclass Dep2 staged there, notch,
    notch back), the GIL off and on: `SpellMap(spellframe="Dep")` follows the index d1 -> d2 -> d1 and
    `meld(spellframe="Dep")` answers; `dep: Dep` refuses at every step (UnresolvedInputError), consistently. At
    0.2.8277 the class annotation got d1 and then failed after the notch (C4's own assertion), so it never followed
    the index across renamed versions; the frame does, before and after. Full suite on 0.2.8278, the GIL off and on,
    identical: 15632 passed, 11 failed - the 9 standing failures of 0.2.8277 (the same set), C4 (this decision) and
    test_generated_build_assets_are_stamped_for_the_live_version (cleared by the rebuild, which runs last); 12
    xfailed (the S1 file's 14 xfails are now assertions) and 2 xpassed (both also pass on 0.2.8277). Example suite:
    617 passed, the same 10 standing failures. The owner chose to fix the SpellMap(ILogic) docstring now.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/c4_world_probe_0_2_8278.txt:1-7
  - context_compass/artifacts/dependency_watchers_20261107/probes/c4_world_probe.py:1-65
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_0_2_8278_gil0.txt:1-1
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_0_2_8278_gil1.txt:1-1
  - context_compass/artifacts/dependency_watchers_20261107/runs/examples_0_2_8278_gil0.txt:1-1
  IMPACT: Index targeting and notch-following are intact through the frame; only the class annotation's reach
    changed, as settled. C4 can be rewritten to pin exactly this.
  NEXT: The owner's call on C4; then the SpellMap docstring, closure, rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T15:06:23Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner, chat 2026-11-07: "oh yeah fix the test and continue those things you said yeah" - C4 rewritten
    to the new contract and the turn-in authorized (SpellMap docstring, closure, rebuild; commit asked separately).
    Done: C4 is now `test_c4_a_class_annotation_never_reaches_a_framed_index_while_its_frame_follows_every_notch` -
    in C4's world `dep: Dep` raises UnresolvedInputError before the notch, after it and after the notch back, and a
    new frame consumer `PFrame(dep=SpellMap(spellframe="Dep"))` builds d1 -> d2 -> d1; the file passes 19 of 19, the
    GIL off and on. SpellMap's docstrings (shape list, usage example, System Context, AGENT_PURPOSE, `spell` arg) say
    a Protocol passed as `spell` is matched by identity - its own definition, never an implementation - and that an
    implementation under a Protocol is injected with `SpellMap(spellframe=P, binding_name=...)` (the owner's choice
    "Fix docstring now"; no behaviour change). Also: the release note now says a required `list[Class]` left empty
    refuses at conjure in an automatic world (found by the docs merge); the architecture patch's invariant 1 names
    the one edge where the door and injection differ by the settled rule (a category spelled as the class's own
    name holds the bare address: `meld(English)` finds it, `x: English` does not); the collision test's stale
    "injected silently" sentence and EngineAlternative's docstring (unused since this change) are corrected.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py:149-159
  - tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py:592-626
  - src/melder/aether/conduit/meld/contracts/spell_map.py:25-62
  - src/melder/aether/conduit/meld/contracts/spell_map.py:106-131
  - release_docs/next_version_release.md:27-33
  IMPACT: Every measured test is converted or rewritten; the change set is complete for turn-in.
  NEXT: Close T2 (summary, completed/, board and artifact sync), then the rebuild and both `--check` runs last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T15:32:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: After the 0.2.8278 rebuild (build assets `--check` OK; llm_support `--check` OK, both at 0.2.8278), the
    full suite: the GIL off 15634 passed, 9 failed - exactly the 9 standing failures of 0.2.8277 - 33 skipped, 12
    xfailed, 2 xpassed; the GIL on the same plus one failure, test_rows_captured_by_another_process_hydrate_this_one
    ('miss' for 'full_hit'), caused by the license task's notch to 0.2.8279 landing mid-run (its child process read
    the new version, the parent the old; bundles admit only the exact version) - the parity file then passes 7 of 7
    in both modes. T2's exit gate holds. The 0.2.8279 notch (the license task) needs one more rebuild, shared with
    the Dependabot change set; that rebuild re-runs both checks.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_0_2_8278_rebuilt_gil0.txt:1-1
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_0_2_8278_rebuilt_gil1.txt:1-1
  IMPACT: The class-lookup change is validated end to end on the user's machine.
  NEXT: None for T2; the shared 0.2.8279 rebuild belongs to the license and Dependabot tasks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: land the class-lookup rule end to end (Objective). State: done 2026-11-07T15:06:23Z, melder_0, as 0.2.8278;
  not committed (the owner is asked before commit and push).
- Delivered: Notes 13:51:39Z (src), 14:14:49Z (the definition-key amendment), 15:06:23Z (C4, SpellMap docstring);
  validation in the Validation section; the patch merged and moved to patches/completed/.
- Open beyond this task: T3 part (b), then part (a) - which also takes the two misleading messages the docs merge
  found (EmptyCollectionStrategy's advice for `list[Class]`, UnresolvedInputError's "nothing registered provides
  it" for a class registered under a frame or name); GitHub #208 update once committed (the owner's point 13).
- Next: the asset and llm_support rebuild with both `--check` runs, then the full suite once more.

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
