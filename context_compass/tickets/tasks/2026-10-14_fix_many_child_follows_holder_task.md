# Task: Register a slotted holder's `many` children with the holder's owner, and keep the specializer from building them

## Metadata
- Task ID: TASK-2026-10-14-fix_many_child_follows_holder
- Story: none - directly under EPIC-2026-10-14-many_child_follows_holder
- Status: review
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T15:29:53Z
- Updated: 2026-10-14T18:27:59Z

## Objective
Implement the owner's rule: a slotted holder's `many` children are recorded in, and disposed with, the store that
owns the holder (spell-owning root for `unique`, that conduit for `unique_per_conduit`, that spellspace for
`unique_per_spell_space`, lineage root, cluster leader). Tests prove it first (red on 0.2.8234), then the fix makes
them green; the opt-in singleton specializer stops building children its holders do not need. Land as one notch.

## Ticket Contract
- ENTRY_GATE: board row `many_child_registration` routes here; the owner's directive is in the epic Decision Log;
  patch docs exist, are linked, and their mapping is in Notes before any `src/` edit.
- EXECUTION_BOUNDARY: `site_plan_lowering.py` (`SitePlanEmission` many registration and docstrings),
  `generalized_hydrator.py` and `generalized_manifest_no_overrides_compiler.py` (specializer eligibility), the
  regression, ownership and specializer tests and any test pinning the old target, `system_docs` (architecture,
  components, indexes, graph), the running release note, `__version__`, assets and llm_support; patch docs.
- DEPENDENCIES: TASK-2026-10-14-prove_many_child_registration_bug (the red tests and route map).
- EXIT_GATE: new tests red on 0.2.8234 and green on the fix; the 5 controls green; the full tree green GIL off and on
  (or every failure shown pre-existing); warm-path emission unchanged; docs, graph, note, notch, assets current; the
  owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST when purge semantics, a persisted format, a cache generation or a warm path
  would change; CONFLICT when an existing test pins the old target as a contract; BLOCKER on unexplained failures.

## Scope Boundaries
- In scope: the registration target of `many` steps inside a shared site's first build; specializer eligibility;
  tests; docs; graph; release note; notch; rebuild.
- Out of scope: purge semantics, ownership transfer of children, managed pools, public API.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the fix (chat 2026-10-14) after reviewing the red tests.
- from_state: in_progress
- to_state: review
- transition_reason: 0.2.8235 landed (src, tests, docs, graph, release note, notch, assets and bundles; full tree
  green GIL off and on on the VM, 2026-10-14T17:18:57Z); acceptance, commit and push are the owner's.

## Steps / Checklist
- [x] Strengthen the regression tests to prove ownership (recorded in the holder's owning store; disposed exactly
      when that owner ends) and add the specializer tests; run them red on 0.2.8234.
- [x] Read the remaining emission and specializer code and the tests that pin either; record the finding.
- [x] Write and link the patch docs; record the patch-to-implementation mapping.
- [x] Implement F1-F3 with docstrings; run the new tests green (GIL off and on).
- [x] Run the full tree GIL off and on; diff warm-path emission before and after.
- [x] Update the system docs, indexes and graph; release note; notch; rebuild assets and llm_support last.
- [x] Move to review and report to the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The fix in `site_plan_lowering.py` and the specializer eligibility; green regression, ownership and specializer
  tests; docs, graph, release note, notch 0.2.8235, rebuilt assets.

## Files / Paths Impacted
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py`
- `tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py`
- `tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py`
- `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py` (the pinned test, renamed)
- `src/melder/__version__.py`, `release_docs/next_version_release.md`, `src/melder/_build_assets/`, `llm_support/`
- `context_compass/system_docs/` and `context_compass/system_docs/patches/completed/many_child_follows_holder_2026_10_14/`

## Validation
- Run on the device VM (Python 3.14.7t, GIL off and on): the 26 new tests (19 red on 0.2.8234, green on the fix),
  the renamed unit test, the specializer and site-plan suites, and the full tree (13,728 passed each way; see Notes).
- Asset and LLM-bundle rebuilds and their `--check` runs: OK.
- Not run: the Windows tiers and hosted CI (the owner's).

## Risks / Rollback Notes
- Rollback: revert the three src files and the test changes; nothing persisted depends on the change (verified:
  plans are emitted from manifest rows at hydration; no cache generation or record format moved).
- A lost cold race's children now live until the holder's store ends (bounded; documented).

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/many_child_registration_20261014/
  - system_docs/patches/completed/many_child_follows_holder_2026_10_14/architecture_patch.md
  - system_docs/patches/completed/many_child_follows_holder_2026_10_14/component_patch_spellcompiler_codegen.md
  - system_docs/patches/completed/many_child_follows_holder_2026_10_14/component_patch_meld_resolution_runtime.md
  - system_docs/patches/completed/many_child_follows_holder_2026_10_14/code_description_patch_site_plan_emission.md
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch docs, archived at landing)
- CLEANUP_TRIGGER: the patch folder moves to patches/completed at landing (moved 2026-10-14 with 0.2.8235)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - the registration target of a shared site's `many` children; specializer eligibility
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose, design, implementation and tests; the whole
  ticket; initial revision 2026-10-14T15:29:53Z; evidence in Notes. The rule is the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T15:29:53Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened from the owner's directive (epic Decision Log 2026-10-14). The fix: inside a shared site's `_miss{i}`
    a disposal-bearing `many` child registers in `c{i}`, the store the site publishes to, instead of the meld's
    innermost scope; top-level `many` steps keep the innermost scope. The opt-in specializer emits every non-captured
    step unconditionally, so on 0.2.8234 it builds and records an unused child on every warm meld (probe: 7 builds and
    6 root records for 6 warm melds plus a spellspace cycle, against 1 and 1 with it off); it will decline graphs in
    which a `many` step feeds a non-`many` step. Tests first: ownership assertions red on 0.2.8234.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1390-1451
  - context_compass/artifacts/many_child_registration_20261014/probe_specializer_children.py:1-98
  IMPACT: The 11 red tests define acceptance; the ownership and specializer tests extend it.
  NEXT: Strengthen the regression tests and add the specializer tests; run them red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T15:36:26Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Tests first, red on 0.2.8234 as intended: 19 failed and 7 passed with the GIL off and on, every failure on its
    corrected-behaviour assertion. Added to the proof's 11: ownership (the child recorded in the holder's owner's
    store, not the melding scope's) for 7 routes plus 2 controls, the nested and override routes and both dynamic
    routes; the owner's end disposes the child once (a lesser's return for a per-conduit holder first melded in that
    lesser's spellspace, root teardown otherwise); and the specializer case (one child built and recorded across 6
    root melds and a spellspace meld; 0.2.8234 builds 7).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py:184-513
  - tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py:103-187
  - context_compass/artifacts/many_child_registration_20261014/runs/red_tests_before_fix.txt:1-221
  IMPACT: Acceptance is fixed before any src edit.
  NEXT: Record the remaining code facts, then the patch docs and the mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T15:36:26Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: One existing unit test pins the defect as a contract:
    `test_disposal_bearing_many_inside_a_miss_registers_in_the_innermost_scope` asserts that the `many` child built in a
    per-conduit site's miss goes to the spellspace store when the plan runs under a SpellSpace meld, and that the
    conduit store (where the site is published) records nothing. The owner's rule supersedes it; it is updated to the
    holder's store and renamed, with this note as the reason. Two other facts settle the shape of the fix: the
    generalized cache package is pure data and plans are emitted from its rows at hydration, so no cache generation
    has to move; and `site_plan_lowering.py` reads `many_store` only through `_emit_many` and the prologue, so the
    store expression can be chosen per context.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py:611-636
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_creation_cache.py:1-18
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1307-1451
  IMPACT: The unit test change is part of the fix, not a weakening; no cache invalidation work.
  NEXT: Write and link the patch docs; record the mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T15:36:26Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written and linked (read in order: architecture, the codegen component, the meld runtime component,
    the code description). Mapping: invariants 1-3 and code-description steps 1-5 -> `SitePlanEmission._emit_context`,
    `_emit_many(store)`, `_emit_miss` without the prologue -> the 7-route and ownership tests, nested, override and
    dynamic routes, and the updated unit test; invariant 4 -> an emission diff of representative plans before and
    after; invariant 5 -> `rows_feed_many_into_non_many_step` and `_install_specializing_door` -> the specializer
    test plus the existing specializer suites; invariant 6 -> the exactly-once assertions. Interface deltas are
    internal only; rollback is the three src files and the tests.
  EVIDENCE:
  - context_compass/system_docs/patches/active/many_child_follows_holder_2026_10_14/architecture_patch.md:1-72
  - context_compass/system_docs/patches/active/many_child_follows_holder_2026_10_14/component_patch_spellcompiler_codegen.md:1-30
  - context_compass/system_docs/patches/active/many_child_follows_holder_2026_10_14/component_patch_meld_resolution_runtime.md:1-20
  - context_compass/system_docs/patches/active/many_child_follows_holder_2026_10_14/code_description_patch_site_plan_emission.md:1-24
  IMPACT: The ENTRY_GATE is met: patch docs exist, are linked and mapped; the src edit can land.
  NEXT: Implement in site_plan_lowering.py, then the specializer decline, then run the new tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T15:49:34Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: F1-F3 implemented. `_emit_context` picks the store per context (`many_store` at the top level, `c{i}` in
    site i's miss) and `_emit_many(..., store)` emits `<store>.register_many(sidN, vN, dmN)`; `_emit_miss` drops the
    innermost-scope prologue; `rows_feed_many_into_non_many_step(rows)` is a pure row helper and
    `_install_specializing_door` returns the plain door when it is True (after the zero-capture check, before the
    root-only decline). Docstrings carry the rule. Line endings repaired: the rewrite had turned the three CRLF
    src files into LF; they are CRLF again (1640/1640, 1568/1568, 772/772) and a CR-insensitive diff against the
    originals shows only the intended hunks; the two new test modules are CRLF like their recent neighbours.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:771-782
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1319-1381
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1433-1503
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1158-1207
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:558-642
  IMPACT: The fix is in place with the files' original line endings; nothing else in the three files changed.
  NEXT: Update the pinned unit test, then run the new and related tests with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T15:49:34Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Invariant 4 holds: across 6 shapes x 2 modes, all 12 `_site_plan_executor` bodies (the warm path) are
    byte-identical before and after; the 14 changed functions are all `_miss{i}` bodies, where the child's
    registration moves from `many_store` to `c{i}` and the 3-line prologue goes.
  EVIDENCE:
  - context_compass/artifacts/many_child_registration_20261014/runs/emit_comparison.txt:1-16
  - context_compass/artifacts/many_child_registration_20261014/compare_emission.py:1-61
  - context_compass/artifacts/many_child_registration_20261014/emit_plan_sources.py:1-20
  IMPACT: N1 (no warm meld path changes) is shown for the site plan; the specializer change affects eligibility only.
  NEXT: Same as above - the unit test, then the test runs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T16:13:01Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green after the fix, GIL off and on. The 26 new tests (19 red on 0.2.8234) and the renamed unit test pass
    (76 with the rest of test_site_plan_lowering.py); the related suites - singleton specialization (component,
    integration deopt matrix, unit wrapper and emission contracts, the efficacy probe), many registration trim,
    door-held root, dual build, positional emission - pass (95). Full tree: 13,728 passed with the GIL off and
    13,728 with it on (unit 9,046, component 2,362, integration 2,070, experimentation 250). Not caused by the fix and
    green on rerun: 3 test_method_inspector tests that read the owner's Windows __pycache__ on the working tree, 17
    caching-system and protocol-crafter tests that cannot delete their temp folders inside tests/ on the connected
    folder (green on a scratch copy), and one flaky 0.2.8234 test (next note).
  EVIDENCE:
  - context_compass/artifacts/many_child_registration_20261014/runs/green_tests_after_fix_gil0.txt:1-36
  - context_compass/artifacts/many_child_registration_20261014/runs/full_tree_summary_gil0.txt:1-32
  - context_compass/artifacts/many_child_registration_20261014/runs/full_tree_summary_gil1.txt:1-23
  - context_compass/artifacts/many_child_registration_20261014/runs/live_method_inspector_gil0_windows_pycache.log:1-27
  - context_compass/artifacts/many_child_registration_20261014/run_part.sh:1-36
  IMPACT: The EXIT_GATE's test half is met; the fix changes no other test's outcome.
  NEXT: Docs (architecture, components, indexes), graph, release note, notch, rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T16:13:01Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: RISK
  CLAIM: Two things found on the way, neither in this task's scope. (1) The 0.2.8234 test
    test_quiet_root_pool_decays_to_baseline_and_burst_restretches is flaky: its fake clock reaches the settle time by
    two float additions (`+= settle - 1.0`, then `+= 1.0`), which for about 1% of clock origins lands one ulp short, so
    the decay step is skipped (40 != 36); it failed once in the GIL-off component chunk and passed on every rerun.
    Fix (test only): advance from a captured origin to exactly `origin + settle`. (2) The first unit chunks ran on the
    working tree and left two untracked folders behind that the connected folder will not let me delete:
    tests/unit/melder/utilities/_protocol_crafter_tmp/ (7 files) and tests/unit/melder/crystallizer/
    _spell_crystal_test_data/ (a 3-file demo package); the other chunks ran on a scratch copy.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py:129-161
  - src/melder/utilities/general_base/abstract_elastic_pool.py:533-599
  - context_compass/artifacts/many_child_registration_20261014/probe_fake_clock_rounding.py:1-31
  - context_compass/artifacts/many_child_registration_20261014/runs/probe_fake_clock_rounding.txt:1-1
  - tests/unit/melder/utilities/test_protocol_crafter.py:41-56
  IMPACT: (1) about 1% of CI runs can fail on an unrelated test; (2) two untracked folders until removed.
  NEXT: Ask the owner at handoff to approve deleting the two folders (else move them to _to_delete/) and whether to
    open a test-only task for the flaky clock.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T16:25:46Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Durable deltas merged from the patch into the canonical docs. src_architecture: an operational invariant,
    a failure mode, a meld-sequence line, the code-map extent of site_plan_lowering.py (1640), a source and the
    handoff entry. src_components: the SpellCompiler emission rule and a new "Holder-owned many children" bullet
    (with the specializer decline), the Meld Resolution store selection and live-creation probe, the trim entry's
    emitted line, the code-map extent and the handoff entry. tests_components: both new modules in their clusters and
    the code map, the touched unit test remeasured, the counts they change recounted. All three indexes regenerated
    and checked. Graph: re-extracted (--strict, nothing skipped), SitePlanEmission and the two generalized module
    nodes authored, SitePlanEmission re-read and accepted (stale back to the 134 found before), reassembled and
    checked. The release example fails its first assertion on 0.2.8234 and holds on the fix, GIL off and on.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:925-943
  - context_compass/system_docs/src_architecture.md:1673-1682
  - context_compass/system_docs/src_components.md:4217-4246
  - context_compass/system_docs/tests_components.md:2806-2814
  - context_compass/artifacts/many_child_registration_20261014/landing/land_docs_0_2_8235.py:1-250
  - context_compass/artifacts/many_child_registration_20261014/landing/graph_semantics_0_2_8235.py:1-59
  - context_compass/artifacts/many_child_registration_20261014/runs/release_example_0_2_8235.txt:1-12
  IMPACT: The patch's content now lives in the canonical docs; the patch folder can be archived at landing.
  NEXT: Notch 0.2.8235, add the release-note entry, archive the patch folder, post the notch notice, then rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T17:18:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Landed as 0.2.8235. `__version__` 0.2.8234 -> 0.2.8235 and the release note's header, its new section "A
    `many` dependency is disposed with the object that holds it" (example verified red on 0.2.8234 and green on the
    fix) and a packaging bullet; the patch folder moved to patches/completed (status completed) with a cleared row on
    the artifact board; the notch notice is on the attention board. The asset rebuild needs to delete and rewrite
    its payloads, so the owner granted delete permission for melder_private (2026-10-14T16:27Z); with it I removed the
    10 untracked temp files my first test chunks had left in tests/ (the RISK note's item 2), so the bundles carry
    the two new modules and no junk. Rebuilt and checked: `_build_asset_runner.py` (agent documentation 462 entries,
    bind guard 622 - unchanged from 0.2.8234 - and the system documents, v0.2.8235) and `llm_support/_builder.py
    --include-untracked`; both `--check` runs print only OK lines. The only untracked files left under src/tests are
    the two new test modules.
  EVIDENCE:
  - context_compass/artifacts/many_child_registration_20261014/landing/release_note_0_2_8235.py:1-90
  - context_compass/artifacts/many_child_registration_20261014/runs/build_assets_check_0_2_8235.log:1-3
  - context_compass/artifacts/many_child_registration_20261014/runs/llm_support_check_0_2_8235.log:1-3
  - release_docs/next_version_release.md:1-3
  - src/melder/__version__.py:12-12
  IMPACT: The EXIT_GATE is met except the owner's acceptance; the task moves to review.
  NEXT: Report to the owner; on acceptance, close the task and the epic (closure sync, artifact disposition).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:27:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The proof's route probe rerun on the landed 0.2.8235 src, GIL off and on: all twelve affected routes keep
    the child until the holder's owner ends (`at_exit=0 at_end=1`, built once, same holder), where 0.2.8234 disposed
    it at the melding scope's end (`at_exit=1`); the five controls are unchanged. Recorded for the review; the owner's
    follow-up question on the other lifetimes continues in TASK-2026-10-14-audit_slotted_lifetime_ownership.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_many_child_routes_after_fix_gil0.txt:1-18
  - context_compass/artifacts/many_child_registration_20261014/runs/probe_many_child_routes.txt:1-39
  IMPACT: Route-by-route confirmation of the fix beside the tests.
  NEXT: Owner accepts and turns the task and the epic in, or redirects.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In review (2026-10-14), landed as 0.2.8235. A slotted holder's disposal-bearing `many` children now register in the
holder's store (`c{i}` inside the site's miss) instead of the meld's innermost scope, so they live and die with the
holder's owner; the opt-in singleton specializer declines graphs that feed a `many` step into a non-`many` step.
Tests first (19 red on 0.2.8234), then green with the full tree, GIL off and on; warm `_site_plan_executor` bodies
byte-identical. Docs, indexes, graph, release note, notch, assets and bundles are current; the patch folder is in
patches/completed. Owed by the owner: acceptance, `git add` of the two new test modules, the archived patch folder
and the evidence folder, commit, push, the Windows tiers and hosted CI. Open beyond this task: purge and ownership
transfer semantics for children (epic questions 1-2), the flaky 0.2.8234 clock test (RISK note) and the
experimentation harness's old prologue regex (tests/experimentation/codegen_strategy_certification.py).

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
