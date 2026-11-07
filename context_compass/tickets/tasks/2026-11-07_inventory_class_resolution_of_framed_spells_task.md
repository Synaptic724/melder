

# Task: inventory_class_resolution_of_framed_spells - every path, test, doc and example that reaches a framed spell by its class

## Metadata
- Task ID: TASK-2026-11-07-inventory_class_resolution_of_framed_spells
- Story: none - an epic-level task of EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Status: in_progress
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-11-07T10:03:26Z
- Updated: 2026-11-07T10:22:44Z

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
- from_state: ready
- to_state: in_progress
- transition_reason: melder_0 re-certified by the owner after compaction (chat 2026-11-07); the board routes here.

## Steps / Checklist
- [ ] Read the type-key matchers in full; list every symbol that admits a framed spell by class.
- [ ] Search tests, docs and examples for class annotations of framed providers; open each hit and classify it.
- [ ] Read the structural snapshot and creation-cache rows: do replayed phase 3-4 rows keep a class match?
- [ ] Edge cases with a recommendation each: an existing object bound under a frame; a string naming a class and a
      category; Protocol definitions bound resolvable=False; `list[Class]` with framed members.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
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

## Context / Handoff Summary
- Scope: the blast radius of the strict model, read-only. State: in_progress, melder_0.
- Done: the matchers (Phase 3 only; two predicates plus the SpellMap identity branch), the cache verdict
  (generation 26 by precedent), examples (none affected) and docs (README and src_architecture already state the
  rule). Running: the main suite in both modes (runs/suite_strict_class_match_0_2_8277_*).
- Next: (1) the suite diff - T2's test list; (2) the strict SpellMap probe run; (3) the edge-case
  DECISION_REQUESTs to the owner (existing object under a frame; bare with a binding_name; `SpellMap(spell=X)`).

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
