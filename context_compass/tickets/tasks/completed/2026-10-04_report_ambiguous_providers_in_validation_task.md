

# Task: Report an ambiguous provider through the readable conjure report instead of a Phase-3 RuntimeError

## Metadata
- Task ID: TASK-2026-10-04-report-ambiguous-providers-in-validation
- Story: none (standalone; follows EPIC-2026-10-03-annotation_category_provider_collision, completed)
- Status: done
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-04T16:40:00Z
- Updated: 2026-10-04T17:35:00Z

- Completed: 2026-10-04T17:35:00Z
- Summary: Landed 2026-10-04 (fable_1) at Melder 0.2.8224 (notched from 0.2.8223): two or more providers for one
  single annotation refuse the consumer through the readable conjure report (`AMBIGUOUS_PROVIDER`: parameter,
  expected type, every candidate's address, the SpellMap / override / single-provider remedies) instead of a
  Phase-3 RuntimeError; `SocketKind.AMBIGUOUS_INPUT`, `AmbiguousProviderStrategy`, watcher and cycle strategy
  updated; five pinned tests converted, 9 regressions added; README, system docs, indexes, graph, release note,
  assets and bundles current. Owner ruling: an error, never a warning. Full tiers Not run after landing (owner
  runs them); touched directories green except the known mount/cache-race flakes. Closed by owner directive.

## Objective
Owner decision (chat, 2026-10-04 10:30 local): ambiguity stays a hard error - no warning - but it must declare what
is busted. Today two resolvable providers for one single annotation raise a raw `RuntimeError` out of Phase 3
(`compiler_phase_3.py:698-710`), so the consumer never reaches Phase 4 and the user gets a compiler trace. Make it
a first-class validation error: Phase 3 records an `AMBIGUOUS_INPUT` socket (candidates as descriptive references,
no target, no edge, dependency_key kept), and a Phase-4 strategy emits `AMBIGUOUS_PROVIDER` (error) naming the
parameter, its annotation, every candidate WITH its address (spellframe, binding_name) and the two remedies
(`SpellMap(spellframe=..., binding_name=...)` as the parameter default; `override={param: ...}` at meld). Conjure
refuses through `SpellbookValidationError` like every other broken spell; the same refusal, same timing.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; patch lane
  `system_docs/patches/active/ambiguous_provider_report_2026_10_04/` (architecture + Phase 3 component patch);
  the resolver, the DAG builder, the topology builder, the self-dependency strategy (the Phase 3 -> Phase 4 pattern
  this copies), the watcher and the cycle strategy read in full.
- EXECUTION_BOUNDARY: `spell_compiler/dag/socket_kind.py`, `spell_compiler/phases/compiler_phase_3.py`,
  `spell_compiler/validation/strategies/ambiguous_provider_strategy.py` (new), `validation/validation_system.py`,
  `dev_ops/spell_system_states/spell_system_states.py` (watcher set), `validation/strategies/
  binding_resolution_cycle_strategy.py` (skip set), the five tests pinning the RuntimeError text, new regressions,
  README, release note, system docs, graph descriptors.
- DEPENDENCIES: the 0.2.8222 kind rule (completed).
- EXIT_GATE: two providers -> `SpellbookValidationError` at conjure (and at a late dynamic bind's first meld) whose
  text carries code `AMBIGUOUS_PROVIDER`, both candidate addresses and both remedies; the MCPScanner shape (two
  classes named alike in two frames) covered; the five pinned tests converted; unit tests for the socket kind, the
  topology mapping and the strategy; the touched tiers run; notch; release note; docs; rebuild.
- FAILURE_ESCALATION: DECISION_REQUEST if a planner or watcher must learn the new kind in a way that changes
  executors (none expected: a broken spell never plans).

## Scope Boundaries
- In scope: the error's path and text.
- Out of scope: any softening to a warning (owner: no); identity keying of class annotations.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: landed at 0.2.8224; closed under the owner's standing turn-in directive with the full tiers owner-owed.

## Steps / Checklist
- [x] Patch lane + consumption mapping note.
- [x] Source: socket kind, resolver returns candidates, DAG/topology record AMBIGUOUS_INPUT, strategy, registration,
      watcher and cycle-strategy skip sets.
- [x] Tests: five pinned sites converted; new unit + integration regressions (incl. the two-`ScanProfile` shape).
- [x] Touched tiers run from the tree (owner runs the full set).
- [x] Docs (README DI paragraph line; src_architecture failure mode + code map; src_components Phase 3 + validation
      strategies entries; indexes; graph), notch, release note, closure, rebuild last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The change at the notched version, regressions, docs.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/spellbook tests/component/melder/spellbook tests/integration/melder/spellbook tests/integration/melder/aether/conduit -q -n 4 -p no:cacheprovider`

## Risks / Rollback Notes
- A new `SocketKind` member: planners never see it (a broken spell does not plan); the watcher and the cycle
  strategy learn it explicitly. No cache generation moves (no captured row can carry it: conjure refuses before
  the snapshot is taken).
- Rollback: revert source and tests together.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] Never claim a test ran that did not run ("Not run.").

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/ambiguous_provider_report_2026_10_04/architecture_patch.md
  - system_docs/patches/active/ambiguous_provider_report_2026_10_04/component_patch_spellcompiler_phase3.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: promoted and archived at turn-in.

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
- DATETIME: 2026-10-04T16:40:00Z
  TYPE: FACT
  CLAIM: The ambiguity path today: `_resolve_single_by_annotation` raises RuntimeError at >1 resolvable candidates
  (text already names SpellMap) and the DAG builder documents that raise; no Phase-4 strategy sees it. The pattern
  to copy is SELF_DEPENDENCY (2026-09-26): Phase 3 records the fact on the topology, `SelfDependencyStrategy` reads
  `get_local_topology` and emits the readable error. UNRESOLVED_INPUT shows the socket plumbing: `socket_unresolved`
  in the DAG builder -> `_build_local_topology` kind + dependency_key -> the watcher
  (`_extract_collection_frame_keys`) and the cycle strategy skip set name the kind explicitly.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:628-712
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:896-986
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1060-1160
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/self_validation_strategy.py:1-136
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1494-1527
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:228-244
  IMPACT: the change is a socket kind + a strategy + two skip-set lines; no planner or cache change.
  NEXT: write the patch lane, then the source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T17:35:00Z
  TYPE: MEASURE
  CLAIM: LANDED AT 0.2.8224 (melder_1 took 0.2.8223 for the `.meldercache` rename in between). Source: `SocketKind.AMBIGUOUS_INPUT`;
  the resolver returns all candidates; `_build_local_frame_dag` records `socket_ambiguous`; `_build_local_topology`
  maps the kind with the candidates as references and the frame key kept; `AmbiguousProviderStrategy` (new,
  registered after RequiredHolesStrategy) emits AMBIGUOUS_PROVIDER with every candidate's address (ordered) and
  the three remedies; the watcher and the cycle strategy learn the kind. Probed both postures on the tree: conjure
  raises SpellbookValidationError with the readable report; a late dynamic bind raises the same report and so
  does a meld of the consumer. Tests: five pinned sites converted (unit resolver, component topology, three
  integration), new unit module for the strategy (8 tests) and the MCPScanner-shaped integration case (two classes
  named ScanProfile in two categories -> both addresses in the report). Tree runs: strategy+phase-3 unit and the
  unresolved-input component file 93 passed; the three integration files 78 passed (one cache temp-file race, passes
  alone); tests/unit/melder/spellbook 2270 passed / 3 failed (method_inspector, the mount-only environment failure);
  tests/component/melder/spellbook 791 passed; tests/integration/melder/spellbook 602 passed / 2 failed under xdist
  that pass alone and a second xdist run green (the cache temp-file race, backlog task). Docs: README SpellMap
  paragraph, src_architecture failure mode + code map + sources + handoff, src_components SpellCompiler block +
  Spell Validation Strategies entry + handoff, both indexes, graph (new module authored, five nodes re-accepted,
  587 sections). Release note: new section + Packaging bullets (bind-guard 622 pending the rebuild).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py:1-196
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1090-1116
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_ambiguous_provider_strategy.py:1-183
  - tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py:366-430
  - artifacts/annotation_category_collision_20261003/fix/ambiguous_report/tree_unit_spellbook.txt:1-2
  - artifacts/annotation_category_collision_20261003/fix/ambiguous_report/tree_component_spellbook.txt:1-2
  - artifacts/annotation_category_collision_20261003/fix/ambiguous_report/tree_integration_spellbook.txt:1-3
  IMPACT: EXIT_GATE met except the full tiers (owner runs them, as for 0.2.8222); closure and rebuild follow.
  NEXT: closure, boards, patch docs archived, rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-10-04T17:35:00Z: DONE. Landed at 0.2.8224; docs, graph, release note, assets and bundles current; the full
tiers are owner-owed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
