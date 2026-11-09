

# Task: inventory_class_resolution_of_framed_spells - every path, test, doc and example that reaches a framed spell by its class

- Completed: 2026-11-07T11:57:30Z
- Summary: The strict rule's blast radius, read-only: Phase 3's two type-key predicates and SpellMap's explicit-spell
  branch are the only src matchers; 106 tests in 20 files change outcome (41 assert the old rule, 65 only reach a
  provider through a spellframe or binding name in their fixtures); examples none; docs mostly already state the rule;
  cache generation 26 by precedent. The owner decided E1-E3 on Autofac's model (a spellframe or a binding name hides
  a class from class lookups) and the spellframe as Melder's interface dict. No src change; no notch.

## Metadata
- Task ID: TASK-2026-11-07-inventory_class_resolution_of_framed_spells
- Story: none - an epic-level task of EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Status: done
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-11-07T10:03:26Z
- Updated: 2026-11-07T11:57:30Z

## Objective
Before any change, know the full blast radius of the strict model: every src path that matches a spell by its type
key whatever its spellframe, every test, system doc, README section and example that resolves a framed spell by
class, and whether replayed caches carry the old matches - each with the source range that decides it.

## Ticket Contract
- ENTRY_GATE: the board routes here; the epic's DECISION note (the owner's choice) is recorded.
- EXECUTION_BOUNDARY: read-only in src, tests, docs and examples; findings in Notes; a probe under
  artifacts/dependency_watchers_20261107 only if a behaviour must be measured.
- DEPENDENCIES: EPIC-2026-11-07-spellframe_hides_the_concrete_class; S1's matrix and interface check.
- EXIT_GATE: the change list (src symbols with ranges), the test/doc/example list, the cache verdict, and a
  DECISION_REQUEST for each edge case, all in Notes; the owner has the edge cases.
- FAILURE_ESCALATION: DECISION_REQUEST for edge cases; BLOCKER if a matcher cannot be found from source.

## Scope Boundaries
- In scope: Phase 3 matching (`CompilerPhase3._spell_keys_for`, `_build_candidate_index`, `_index_buckets_for`,
  `_indexed_annotation_candidates`), any other type-key matcher (structural snapshot annotation refs, Phase 4
  strategies, examiner profiles), tests/, docs/, README.md, system_docs, examples.
- Out of scope: any edit.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: every exit-gate item is in Notes and the owner decided the edge cases (chat 2026-11-07: E1
  "Hide it, like a class"; E2/E3 "fine" on the Autofac reading; the spellframe is the interface dict).

## Steps / Checklist
- [x] Read the type-key matchers in full; list every symbol that admits a framed spell by class.
- [x] Search tests, docs and examples for class annotations of framed providers; open each hit and classify it
      (measured with the strict probe: 103 tests in 17 files; examples and docs none to reverse).
- [x] Read the structural snapshot and creation-cache rows: do replayed phase 3-4 rows keep a class match?
- [x] Edge cases with a recommendation each: an existing object bound under a frame; a string naming a class and a
      category; Protocol definitions bound resolvable=False; `list[Class]` with framed members. (The last three
      follow the rule as decided: a string names a type or a contract, never a category; definitions match through
      their Protocol; `list[Class]` gathers bare spells. Open with the owner: E1-E3, DECISION_REQUEST 10:56:28Z.)
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Notes: the change list, the test/doc/example list, the cache verdict, the edge-case DECISION_REQUESTs.

## Files / Paths Impacted
- none (read-only)

## Validation
- Not run.
- Recommended commands:
  - `.venv_new/Scripts/python.exe -X gil=0 -m pytest tests -q` (the baseline before T2)

## Risks / Rollback Notes
- A matcher missed here ships a half-strict model; the S1 matrix re-run in T2 is the backstop.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed) - none: read-only task; the doc changes are T2's list
- [x] Validation status recorded - measurements only (probe runs in runs/); no src change to validate
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/dependency_watchers_20261107/probes/strict_class_match_plugin.py
  - artifacts/dependency_watchers_20261107/probes/strict_spellmap_plugin.py
  - artifacts/dependency_watchers_20261107/probes/compare_strict_class_match_runs.py
  - artifacts/dependency_watchers_20261107/probes/run_strict_class_match_suite.sh
  - artifacts/dependency_watchers_20261107/runs/ (suite_strict_class_match_*, examples_*)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: T2 re-runs the plugins as its before/after check; the runs stay beside the 0.2.8277 ones

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - type-key matching of framed spells
- IF_UNKNOWN: none

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
  CLAIM: Start at Phase 3's matching table - `_spell_keys_for` returns the type key for a class annotation whatever
    the spell's frame, and `_build_candidate_index` files every spell under its type key - then widen to the other
    type-key readers and to the tests, docs and examples that rely on them.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:472-519
  IMPACT: The inventory bounds T2's change and the release note's breaking surface.
  NEXT: Read the type-key matchers in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-11-07T10:25:21Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: compiler_phase_3.py read in full (1319 lines, 0.2.8277). Three places admit a framed spell by its class,
    all keyed on `_spell_type_key` (the lowercased `spell_name`, whatever the spellframe): (1) `_spell_keys_for` returns
    the type key for a class annotation, single or `list[...]`, and the type key plus contract keys for a single
    string annotation - the scan path through `_matches_annotation`; (2) `_build_candidate_index` files every spell in
    `by_type`, which `_index_buckets_for` reads for a class annotation and for a single string - the index path,
    which `_build_local_frame_dag` uses whenever the pass has a cache; (3) `_resolve_spellmap_default` with
    `SpellMap(spell=X)` and no spellframe matches by identity (`spell_obj.spell is explicit_spell`) whatever X's
    frame - while `meld(X)` refuses a framed X. Already frame-only: a string collection (`list["greeters"]`) reads
    the label key (spellframe, else own name); Protocol annotations read contract and definition keys. The watcher
    key `_dependency_key_for_dep` is the annotation's own name, so once (1) and (2) admit only bare spells every
    match key equals its provider's address frame. A class annotation with no candidate becomes UNRESOLVED_INPUT
    (`_build_local_frame_dag` 1160-1166) - the point where T3 part (a) must record the framed spells it skipped.
    The class docstring (74-83) still states the superseded 2026-10-03 address-key rule; T2 rewrites it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:66-86
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:260-301
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-445
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:472-626
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:796-926
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1133-1173
  IMPACT: T2's src change is two predicates - the type row of `_spell_keys_for` and `by_type` admit only spells with
    no spellframe - plus the docstrings; `SpellMap(spell=X)` without a frame is an edge case for the owner.
  NEXT: Find any other reader that matches by type key (structural snapshot, Phase 4, examiner, meld), then the cache
    verdict.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T10:27:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Phase 3 is the only src matcher by type key. A search of src for `_spell_type_key`, the candidate-index
    names and `normalize_frame_key(...spell_name)` finds them only in compiler_phase_3.py (and the generated
    components payload); the other `by_type` names are DevOps transaction-type maps. The meld doors key a class by
    its own name and look up that address, so `meld(English)` stays a refusal for a framed English with no change.
    Phase 4's binding-key cycle heuristic maps an annotation to (its name, default binding) and a spell to its
    address, so after T2 a class annotation's edge lands on its bare provider; providers with a binding_name stay
    outside it (S1's P1a, which stays on the dependency-watchers epic). Cache verdict: structural snapshot rows
    replay Phase 3's match results (dependency ids and socket rows) when the key (spell_id, binding hash, annotation
    refs) and the world stamp (pool ids and binding hashes) match - neither moves when the matching rule changes, so
    a same-release bundle would replay pre-T2 matches; every bundle of another release is cold (generation 9's
    exact-release admission), and T2's notch moves the release. Generations 18 and 20 were bumped for the two
    earlier matching-rule changes, so T2 bumps to 26 by that precedent and the owner's codegen rule.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:107-129
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:178-299
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:35-132
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:183-295
  - src/melder/utilities/caching_system/caching_system.py:198-208
  - src/melder/utilities/caching_system/caching_system.py:245-272
  - src/melder/utilities/caching_system/caching_system.py:899-920
  IMPACT: T2's src surface is Phase 3 plus a cache-generation entry; no meld door or Phase 4 strategy changes.
  NEXT: Measure the test blast radius: run the suite with and without a runtime patch of the strict rule (probe
    plugin under artifacts/dependency_watchers_20261107/probes, no src edit), the conjure cache redirected to a temp
    root in both runs so no bundle replays matches across runs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T10:35:36Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Examples and docs. Method: probes/strict_class_match_plugin.py patches `_spell_keys_for` and
    `_build_candidate_index` at runtime (MELDER_PROBE_STRICT=1) and redirects the default conjure cache to a temp
    root in both modes; smoke-checked on the S1 regression file (as shipped 9 passed, 14 xfailed; strict 14
    precondition failures, 9 passed). The handbook example harness (UX_and_AIX_experiences/pytest_examples, 627
    tests, outside the main suite) gives the same outcome in both modes, the GIL off: no example relies on a class
    reaching a framed spell. It fails 10 tests in both modes and without the plugin - pre-existing on 0.2.8277, not
    this epic; one, `test_probe_two_visible_spells_may_not_share_a_name`, asserts the pre-0.2.8206 rule (two
    same-named classes refused despite distinct binding names) and bears on T3 part (b). Docs: README's DI section
    and src_architecture's kind invariant already say a class selects "a class bound bare, or an existing object
    of that class"; no handbook page or agent-ops line shows a class annotation reaching a framed spell. The
    agent-ops table pairs `SpellMap(Store)` with a Store bound under "storage" (the SpellMap edge case only).
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/examples_strict_class_match_0_2_8277_diff_gil0.txt:1-3
  - context_compass/artifacts/dependency_watchers_20261107/runs/examples_noplugin_0_2_8277_gil0.txt:84-94
  - UX_and_AIX_experiences/pytest_examples/test_expert_probes.py:992-1026
  - README.md:458-464
  - context_compass/system_docs/src_architecture.md:2120-2137
  - agents/MELDER_AGENT_OPERATIONS.md:97-121
  IMPACT: T2's doc work is wording (the frame door, the Breaking note), not a reversal; examples need no change.
  NEXT: Read the main suite's two runs (in progress) and list the tests whose outcome differs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T10:47:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The main suite, the GIL off, 16 workers, on the tree committed as c6778e303 (0.2.8277): as shipped 15,648
    tests - 18 failed, 15,572 passed, 32 skipped, 26 xfailed; strict 121 failed, 15,483 passed, 12 xfailed. 103 tests
    in 17 files change outcome (89 passed -> failed, 14 xfailed -> failed): test_compiler_phase_3 15 (the matcher's
    unit contract), the S1 regression file 14 (its xfails), injected_provider_direct_meld 13, notch_refused_at_commit
    11, annotation_category_collision 9, provider_artifact_ownership 7, existing_instance_additional_regressions 6,
    the borrower provider experiment 6, spell_crafter change_control 5, structural_snapshot_parity 4,
    validation_system 3, existing_instance_planning 3, di_shape_compiler_matrix 2, phase5_contracts 2,
    resolution_error_matrix 1, notch_revalidation 1, rebind_after_first_meld 1. The strict failures read
    UnresolvedInputError 47 (a class consumer of a framed provider is now an unresolved input), "DID NOT RAISE" 18
    (a refusal the framed candidate caused no longer happens), the S1 preconditions 14, assertion mismatches 22. The
    18 shipped failures are the same in both modes, so none is in the diff; 8 are the refused-cache-save tests, which
    the probe's cache redirect likely breaks, the other 10 are not yet checked without the probe.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_strict_class_match_0_2_8277_diff_gil0.txt:1-226
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_strict_class_match_0_2_8277_strict0_gil0.txt:1-334
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_strict_class_match_0_2_8277_strict1_gil0.txt:1-817
  IMPACT: T2's test list: 103 tests in 17 files, each to be converted to the strict contract or removed with a
    reason; the breaking surface is real and the release note must say so.
  NEXT: Classify the 17 files (intent kept vs encoded old behaviour), run the strict SpellMap probe, and check the
    18 shipped failures without the probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T10:49:50Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The 18 shipped-run failures, re-run serially without the probe on c6778e303, the GIL off: 9 pass - the
    eight refused-cache-save tests and the Windows held-bundle test, which the probe's cache redirect broke - and 9
    fail anyway, so they predate this epic and are outside it: seven read enum spellings both ways ('BIND' ==
    'bind', 'CLEANED' == 'cleaned' x3, 'TRANSFER_OWNERSHIP' == 'transfer_ownership', 'formation_load' ==
    'FORMATION_LOAD', 'WAIT_TIMEOUT' in a lowercase refusal text) - the 0.2.8276-0.2.8277 enum lanes' tests and code
    disagree; one mediator concurrency test saw a torn participant row 47,154 times
    (test_racing_lifecycle_edges_never_leave_a_torn_row); one policy-reader memo test fails `assert not True`.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/shipped_failures_0_2_8277.txt:1-18
  - context_compass/artifacts/dependency_watchers_20261107/runs/shipped_failures_noplugin_0_2_8277_gil0.txt:1-58
  IMPACT: The strict diff is clean of probe noise; the 9 standing failures go to the owner as their own item.
  NEXT: Classify the 17 files.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T10:49:50Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The 17 files sort two ways. (1) They assert the old rule itself - rewrite each to the strict contract: the
    Phase 3 unit tests (15; e.g. `index["by_type"]` holding framed spells, test_compiler_phase_3.py:477), the S1
    regression file (14 xfails) and annotation_category_collision (9: a class reaching its provider under a
    category, two same-named classes in two categories reported as AMBIGUOUS_PROVIDER). 38 tests in 3 files. (2) Their
    subject is something else and only the fixture reaches a framed provider by class - convert the fixture: 65
    tests in 14 files - injected_provider_direct_meld 13, notch_refused_at_commit 11 (its refusal is built from a
    framed provider; needs another structural failure), provider_artifact_ownership 7, existing_instance
    regressions 6 and planning 3 (an existing object under the Protocol IExistingValue - edge case E1), the
    borrower experiment 6, change_control 5, structural_snapshot_parity 4, validation_system 3, di_shape matrix 2
    and resolution_error_matrix 1 (their cycles run through framed providers), phase5_contracts 2,
    notch_revalidation 1, rebind_after_first_meld 1. Many fixtures bind a class under a category spelled as its own
    name (`spellframe="Alpha"`, `"Engine"`, `BasicService.__name__`, `cls.__name__`, `"Dep"`) - the same address as
    a bare bind, so the conversion is to drop the spellframe; the rest bind under a Protocol or category and switch
    the consumer to the Protocol annotation, a SpellMap or a bare bind.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_strict_class_match_0_2_8277_diff_gil0.txt:4-226
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:419-480
  IMPACT: T2's test work is bounded: 3 files rewritten to the strict contract, 14 fixture conversions. The
    same-named-category idiom goes in the release note's upgrade path (drop the spellframe; the address is the same).
  NEXT: The strict SpellMap probe's diff (running), then the edge-case DECISION_REQUESTs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T10:56:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: probes/strict_spellmap_plugin.py (MELDER_PROBE_STRICT_SPELLMAP=1: `SpellMap(spell=X)` with no spellframe
    matches only an X bound with no spellframe) over the main suite, the GIL off, against the shipped run: 1 test of
    15,648 changes - test_component_spell_crafter_spellmap_default_raises_on_duplicate_explicit_matches, whose two
    pool stubs carry `spellframe=BasicService` (a concrete class as spellframe, refused by bind since 0.2.8222) for
    one object registered twice (refused since 0.2.8257); its "multiple" refusal becomes "could not be resolved".
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_strict_spellmap_0_2_8277_diff_gil0.txt:1-6
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:919-985
  IMPACT: Making SpellMap(spell=X) follow the class rule costs one stub-only test; it is a free choice in tests.
  NEXT: The edge-case DECISION_REQUESTs to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T10:56:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Three edge cases for the owner, each with a recommendation. E1 - an existing object bound under a spellframe
    (an instance under the Protocol IExistingValue): today `value: ExistingValue` finds it; recommend it is hidden
    like a class (one rule; the 9 existing-instance tests switch to the Protocol annotation). E2 - a class bound bare
    with a binding_name: today `greeter: English` injects it (measured 2026-11-07) while `meld(English)` needs the
    binding name; recommend it stays injectable (a binding name is an address slot, not an interface; the rule was
    set for spellframes; its watch key equals its address frame, so no key split). E3 - `SpellMap(spell=X)` with no
    spellframe: today it matches X by identity under any frame (Phase 3 844-856) while `meld(X)` refuses a framed
    X; recommend it follows the class rule - only a bare X, a framed X through `SpellMap(X, spellframe=F)` - which
    the SpellMap docstring already calls type-based ("the spell itself supplies the lookup identity"), which keeps
    its canonical key equal to its provider's address frame, and which costs one stub-only test.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:796-881
  - src/melder/aether/conduit/meld/contracts/spell_map.py:25-35
  - context_compass/artifacts/dependency_watchers_20261107/runs/binding_name_and_spellmap_check_0_2_8277.txt:3-5
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_strict_spellmap_0_2_8277_diff_gil0.txt:1-6
  IMPACT: The answers fix T2's predicate (`spellframe is None` for classes and existing objects; SpellMap's
    explicit-spell branch or not) and its test list (E1: 9 tests; E3: 1 test).
  NEXT: The owner's answers; then T1 closes and T2 starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T11:00:27Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's answers (chat 2026-11-07). E1: "Hide it, like a class" - an existing object bound under a
    spellframe is hidden from its class, as a class is. E2 (a bare class with a binding_name): "I think binding name
    should take prio if you set it what does autofac do can you investgate how they handle this kinda stuff?" - his
    lean is that a set binding name takes priority over the class; he asked for Autofac's behaviour first. E3
    (`SpellMap(spell=X)` without a spellframe): "do what autofac would do and we can discuss this further thats our
    compass" - Autofac is the reference for these resolution rules. E2 and E3 stay open until the Autofac findings
    are discussed.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-11-07_inventory_class_resolution_of_framed_spells_task.md:307-331
  IMPACT: T2's predicate covers existing objects (E1). E2 may widen the rule from spellframes to binding names;
    E3 follows whatever Autofac does when a type is requested that was registered only under another service.
  NEXT: Read Autofac's documentation on default services, As/AsSelf and named/keyed services; report and discuss.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T11:05:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Autofac, from its docs and its develop-branch source (read through a web-fetch subagent). A registration that
    declares no service exposes its own type; declaring any service turns that off - RegistrationData yields the
    default TypedService only while `_defaultServiceOverridden` is false, and AddService sets it for every service but
    AutoActivateService - unless `.AsSelf()` adds it back. `Named`/`Keyed` are `As(new KeyedService(...))`, so
    `RegisterType<English>().Named<English>("v1")` exposes only the keyed service: an unnamed Resolve<English>() and a
    plain constructor parameter of type English get nothing; a parameter reaches it with `[KeyFilter("v1")]` (opt-in
    WithAttributeFiltering) or IIndex<K,V>. Several unkeyed registrations of one service: the last registered is the
    default (PreserveExistingDefaults changes that), IEnumerable<T> returns all, and nothing raises ambiguity. Mapped
    to Melder: a bind with neither spellframe nor binding_name is the default self registration; a spellframe is
    As<Service>; a binding_name is Named/Keyed. The compass therefore reads: a class annotation, `list[Class]`,
    `meld(Class)` and `SpellMap(spell=Class)` reach a class only when it is bound with neither (E2: hide; E3: same),
    and `SpellMap(Class, binding_name=b)` is the KeyFilter. `meld(English)` already needs the binding name; injection
    is the door that does not. Two deliberate differences stand by owner ruling: ambiguity is an error, not
    last-wins (2026-10-04); and one active spell per address, so implementations of one frame carry distinct binding
    names - Protocol annotations and `list[Protocol]` must keep seeing named implementations, or README's
    `list[Handler]` plugin pattern breaks (Autofac's keyed registrations are invisible to unkeyed lookups).
  EVIDENCE:
  - https://autofac.readthedocs.io/en/latest/register/registration.html
  - https://autofac.readthedocs.io/en/latest/advanced/keyed-services.html
  - https://raw.githubusercontent.com/autofac/Autofac/develop/src/Autofac/Builder/RegistrationData.cs
  - https://raw.githubusercontent.com/autofac/Autofac/develop/src/Autofac/Builder/RegistrationBuilder%7BTLimit,TActivatorData,TRegistrationStyle%7D.cs
  - UX_and_AIX_experiences/AGENTS.md:61-63
  - README.md:519-537
  IMPACT: E2 and E3 resolve to "a binding name hides the class too" for class lookups only; frames keep today's
    binding-name semantics. The blast radius of that reading is being measured (probe mode 2).
  NEXT: The mode-2 suite diff, then the discussion with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T11:12:36Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The Autofac reading over the main suite, the GIL off (probe mode 2: a spellframe or a binding name hides a
    spell from class lookups; `SpellMap(spell=X)` with neither frame nor binding name matches only an X bound with
    neither): 124 failed, 15,480 passed; against the shipped run 106 tests in 20 files change outcome - the 103 of the
    spellframe rule plus 3: the SpellMap stub test, `test_b3_spellmap_matches_target_under_any_binding` (it asserts
    the identity-pin behaviour by name) and `test_type_hint_di_ambiguous_concrete_class_raises` (two same-named classes
    bound bare with different binding names were AMBIGUOUS_PROVIDER for a class annotation; under the reading both
    are named, so neither answers). All three encode the behaviour being changed.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_autofac_reading_0_2_8277_diff_gil0.txt:1-235
  - context_compass/artifacts/dependency_watchers_20261107/runs/suite_autofac_reading_vs_strict1_0_2_8277_diff_gil0.txt:1-12
  IMPACT: Following Autofac for class lookups costs 3 tests beyond the spellframe rule; the choice is about meaning,
    not test cost.
  NEXT: The owner's call on the split (Autofac for class lookups, Melder's model for frames).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T11:28:06Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner accepted the Autofac reading for E2 and E3 (chat 2026-11-07: "E2 and E3 are fine I think"), after
    asking to discuss before anything is done ("discuss this with me before you do it") and adding "we are not
    autofac so lets talk more about this like where can we benefit from their style and what are our best
    options here". So: a class lookup - annotation, `list[Class]`, `SpellMap(spell=Class)` - reaches a class only
    when it is bound with neither a spellframe nor a binding name; `SpellMap(Class, binding_name=b)` reaches it
    under its name. Still in discussion, nothing to implement yet: where else Autofac's style helps Melder, an
    AsSelf-style option, and the frame doors.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-11-07_inventory_class_resolution_of_framed_spells_task.md:307-331
  IMPACT: T2's predicate is set (no spellframe and the default binding); T3 part (a)'s error must also name a binding
    name to ask by when the class is bound bare under one.
  NEXT: The design discussion with the owner; T1 closes when it settles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T11:42:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's model, correcting my proposal of `dict[str, Greeter]` injection as Autofac's IIndex (chat
    2026-11-07): "Dict<str, greeter> is our spellframe our spellframe is the interface dict idea thats the point".
    The spellframe is Melder's IIndex: the frame is the dict, the binding name its key -
    `meld(spellframe=Greeter, binding_name="english")` is index["english"], `SpellMap(spellframe=..., binding_name=...)`
    its injected form, `list[Greeter]` its values; handbook example 38 melds a whole frame into {name: instance}. The
    dict-injection idea is dropped. Read the same way, `meld(spellframe=Greeter)` with no key reads the default slot,
    so its KeyError for a frame with only named members is dict behaviour, while `greeter: Greeter` asks the contract
    for its one implementation - option (a) of the frame-door question (keep, document); put to the owner.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/38_meld_a_frame_as_dict.py:1-7
  - UX_and_AIX_experiences/01_beginner/38_meld_a_frame_as_dict.py:28-28
  - UX_and_AIX_experiences/01_beginner/25_frames_as_dict_classification.py:1-12
  IMPACT: No new injection feature; example 25's "frames are NOT dicts" wording contradicts the owner's model and
    belongs in T2's doc pass if he confirms.
  NEXT: The owner's confirmation of option (a) and his go for T2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T11:57:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Gap check before closing (the owner asked "are we missing anything?"). The handbook examples under the agreed
    rule (probe mode 2) change no outcome: 627 tests, the same 10 pre-existing failures. `SpellContract` already
    matches by address - `canonical_key` normalizes (spell, spellframe, binding_name) to (frame_key, binding_key) - so
    `SpellContract(spell=English)` reaches only an English bound bare and unnamed and needs no change. The meld doors
    already need the full address; no record or RecordVersion stores a match result (the structural snapshot in the
    creation cache is the only one, hence generation 26); the frame doors stay as shipped (option (a)), documented
    in T2. Outside this epic: the 9 standing failures of the enum lanes and the 10 failing example tests.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/examples_autofac_reading_0_2_8277_diff_gil0.txt:1-3
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:272-303
  IMPACT: T1's exit gate is met; T2 starts from the change list in its own Notes on the owner's go.
  NEXT: Close T1; T2 to ready.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: the blast radius of the strict model, read-only. State: done (2026-11-07T11:57:30Z), melder_0.
- Outcome: Phase 3's two type-key predicates and SpellMap's explicit-spell branch are the change; 106 tests in 20
  files (runs/suite_autofac_reading_0_2_8277_diff_gil0.txt); examples none; cache generation 26; the owner's rule:
  a spellframe or a binding name hides a class from class lookups (Autofac), the spellframe is the interface dict.
- Successor: TASK-2026-11-07-class_annotation_selects_only_bare_spells (T2) carries the change list.

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
