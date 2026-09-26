

# Task: Each collection member gets its own many-existence dependencies

## Metadata
- Task ID: TASK-2026-09-26-fix-collection-member-many-sharing
- Story: STORY-2026-09-26-implement-override-site-plan-lowering
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T12:13:26Z
- Updated: 2026-09-26T12:21:23Z

## Objective
A `many` dependency reached through two collection members is built once per member, as `Existence.many`
promises. Today `CollectionRoot(members: list[IMember])` over `MemberA(leaf: Leaf)` and `MemberB(leaf: Leaf)`
hands both members the same `Leaf` object.

## Ticket Contract
- ENTRY_GATE: Owner ruling 2026-09-26T12:13:26Z ("a many is not meant to be shared like that"); root cause
  traced in source and written in Notes; a patch doc for the changed component and the exact file list in
  Notes before code.
- EXECUTION_BOUNDARY: The compiler path-keying and its direct consumers named in the file list below once the
  investigation fixes it. No change to shared existences, key grammar or public API.
- DEPENDENCIES: S1 site graph (instance keys); melder_1's regression matrix; fable_0's task 5 (Phase-9
  contract rows) for shared-file notices.
- EXIT_GATE: Regression test red before and green after; suites unchanged otherwise on 3.14t and GIL; the S1
  oracle updated (collection PATH difference re-examined); cache generation bumped if emitted code changes.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix changes override key semantics; CONFLICT with fable_0's
  in-flight files; BLOCKER if a green baseline cannot be established.

## Scope Boundaries
- In scope: distinct occurrences and instance keys for collection members' many dependencies, and whatever
  reads those keys (injection, runtime plans, override targeting rows).
- Out of scope: S2-S6 lowering work, shared existences (they are shared by design), value validation.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner ruled the sharing a defect and asked to keep working, 2026-09-26T12:13:26Z.

## Steps / Checklist
- [x] Trace where occurrence paths and path ids are minted (Phase 8) and every consumer of them.
- [x] Write a failing regression test (component) for the probe case.
- [x] Patch doc + file list in Notes.
- [ ] Implement; re-run the regression test, the S1 oracle and the suites on 3.14t and GIL.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Fix, regression test, notes with before/after evidence.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/dag/dag_index.py (PathRegistry.extend_path member key)
- src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py (Phase-5 overlay)
- src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py
  (Phase-8 topology expansion and DAG fallback)
- src/melder/utilities/caching_system/caching_system.py (generation 13)
- tests/integration/melder/spellbook/test_cache_schema_version_integration.py (expected history)
- tests/component/melder/spellbook/test_spellbook_component_collection_many_instances.py (new regression)

## Validation
- Not run.

## Risks / Rollback Notes
- Changing path ids can move override-targeting rows and cached executors; cache generation 13 may land here.

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
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_collection_member_paths.md
  - artifacts/melder_override_design_20260926/collection_fix_staging/ (apply script, regression test copy)
- DISPOSITION: promote_to_documentation (patch doc); retain_as_reference (staging)
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Phase-8 occurrence paths and many-existence instance keys under collections
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T12:13:26Z
  TYPE: FACT
  CLAIM: Defect reproduced in S1 (probe, 3.14t): CollectionRoot(members: list[IMember]) over MemberA(leaf) and
    MemberB(leaf), all many -> members[0].leaf is members[1].leaf is True. PathRegistry interns path ids by
    (parent id, parameter name), so both members sit on path "members" and both leaf edges get
    (Leaf, id("members>leaf")); the instance processor mints one many instance per path id.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/dag_index.py:118-150
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:131-190
  IMPACT: Every many dependency below a collection member is silently shared across members.
  NEXT: Trace the Phase-8 occurrence build that calls extend_path, and every consumer of path ids.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T12:16:53Z
  TYPE: FACT
  CLAIM: Trace. Phase 5 (blueprint overlay) and Phase 8 (occurrence graph) share one PathRegistry and mint a
    child path as extend_path(parent, param_name) for EVERY target of a socket; for a collection socket all
    members therefore sit on one path id, and any many dependency below them resolves to one occurrence
    (spell, id("members>leaf")) -> one instance key -> one object. Consumers relate sockets to occurrences
    only through path ids: the override compilers match a socket to a plan step by parent_id(socket path)
    == the step's occurrence path; the override-targeting processor keys PATH specs by format_path(...)
    (last write wins, so "members>leaf" keeps one row); the sanity validator checks socket/index agreement
    by id. resolve_path_id has no caller outside dag_index.py; SpellOverrider (the only DagTargetingEngine
    user) has no caller.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:970-1030
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:435-490
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:2284-2368
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:43-110
  - src/melder/aether/spellbook/spell_compiler/dag/dag_index.py:118-176
  IMPACT: The fix is local to path minting: give each collection member its own child path id while keeping
    the parameter-name segment, in Phase 5 and Phase 8 identically, so socket parent ids still equal
    occurrence paths.
  NEXT: Write the failing regression test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:16:53Z
  TYPE: PLAN
  CLAIM: Fix design. (1) PathRegistry.extend_path(parent_id, segment, member=None): the interning key becomes
    (parent, segment, member); stored segments stay parameter names, so materialize/format/depth/parent and
    every string key are unchanged; resolve_path_id keeps resolving member-less paths. (2) Phase 5 overlay:
    a collection socket keeps its own path (member None) and queues each target at
    extend_path(path, name, member=target_id). (3) Phase 8 topology expansion: the same rule. (4) Phase 8 DAG
    fallback (no topology, collection-ness unknown): a parameter with two or more dependencies uses
    member=target id. (5) Cache generation 13 (emitted plans follow instance keys); notice melder_1 before
    editing caching_system.py. Consequences: two many objects per member as owner ruled; UNIQUE counts for
    parameters below those objects count each member's copy (they are real objects now); today's
    "members>leaf" PATH row stays last-wins until S3's resolver replaces it; shared existences unchanged.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/dag_index.py:118-176
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:435-490
  IMPACT: One small, uniform change at the only two path-minting sites that fan out to several targets.
  NEXT: Write the regression test and see it fail on the current tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:21:23Z
  TYPE: MEASURE
  CLAIM: Regression test written and RED on the consistent VM tree (3.14t): 4 failed, 1 passed. Six members
    across two collections got 2 distinct Leaf objects (one per collection) instead of 6; many Configs below
    them 2 instead of 6; two melds 4 leaves instead of 12. The shared-Config case (1 object) passes, as it
    must.
  EVIDENCE: artifacts/melder_override_design_20260926/collection_fix_staging/test_spellbook_component_collection_many_instances.py:1-159
  IMPACT: The defect is reproduced by a test that will guard the fix.
  NEXT: Apply the fix (file list above; patch doc component_patch_collection_member_paths.md).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T12:21:23Z
  TYPE: PLAN
  CLAIM: Patch mapping. component_patch_collection_member_paths.md "After" bullets 1-4 ->
    apply_cfix_edits.py DAG_EDITS (extend_path member key, resolve_path_id member-less), BLUEPRINT_EDITS
    (collection targets on member paths), ANALYZER_EDITS (topology rule, DAG-fallback rule); "After" bullet 5
    -> CACHE_EDITS (generation 13 + expected history). Validation: the regression test red->green, S1 oracle,
    unit/component A/B on the consistent VM tree for the path edits, and a device-state A/B with the cache
    edit. Owner's standing instruction ("keep working ... don't stop until your done") is the confirmation
    for this file list; melder_1 gets a notice before caching_system.py changes.
  EVIDENCE:
  - system_docs/patches/active/override_site_plan_2026_09_26/component_patch_collection_member_paths.md
  - artifacts/melder_override_design_20260926/collection_fix_staging/apply_cfix_edits.py
  IMPACT: Every patch bullet has an edit and a check before code.
  NEXT: Apply to the VM trees and run the regression test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened after the owner ruled the sharing a defect. Next: trace Phase-8 path minting and its consumers.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
