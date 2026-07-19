Completed: 2026-06-12T12:29:40Z
Summary: Closed as a stale tranche ticket after the older graph-population lane
was superseded by a fresh documentation-drift investigation epic.

# Task: Populate Src Graph For Spellbook Second Tranche

## Metadata
- Task ID: TASK-2026-04-19-populate-src-graph-for-spellbook-second-tranche
- Story: STORY-2026-04-19-populate-src-graph-for-spellbook-directory
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T20:29:57Z
- Updated: 2026-06-12T12:29:40Z

## Objective
Continue the `spellbook` graph lane by populating the next high-value layer
above the root binding objects: the deeper SpellCrafter planning and
system-validation artifacts that sit on top of the rooted blueprint model.

## Ticket Contract
- ENTRY_GATE: the first `spellbook` tranche is in review and the story still
  has deeper SpellCrafter planning/system-validation objects that materially
  sharpen the graph.
- EXECUTION_BOUNDARY:
  - deeper `src/melder/spellbook/**` planning and system-validation objects
  - `codex/context_compass/system_docs/src_graph.json`
  - patch-lane expanded graph working copy for the active `spellbook` story
- DEPENDENCIES:
  - `tickets/tasks/2026-04-19_populate_src_graph_for_spellbook_first_tranche_task.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
- EXIT_GATE: the second `spellbook` tranche lands the next high-value
  planning/system-validation nodes and edges with JSON validation still green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the second tranche starts to
  devolve into low-signal strategy/helper inventory instead of meaningful
  planning/system structure.

## Scope Boundaries
- In scope:
  - deeper SpellCrafter plan objects
  - rooted blueprint consumers and system-index consumers
  - spellbook-side system-validation objects only when they clarify the phase graph
- Out of scope:
  - `tests/**`
  - low-value validation strategy leafs unless they become structurally necessary
  - utilities-wide infrastructure

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the first `spellbook` tranche is coherent enough to hand
  off and the story still has a denser planning/system-validation layer worth
  graphing next.

## Steps / Checklist
- [ ] Choose the next high-value `spellbook` planning/system-validation set from source evidence.
- [ ] Read the selected files in compliant chunks where needed.
- [ ] Record the next meaningful finding in `## Notes` before graph edits.
- [ ] Patch the expanded graph working copy.
- [ ] Recompress and validate the canonical graph.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- second `spellbook` graph tranche
- updated `src_graph.json`
- validation record and tranche notes

## Files / Paths Impacted
- src/melder/spellbook/
- codex/context_compass/system_docs/src_graph.json
- codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
- codex/context_compass/tickets/tasks/2026-04-19_populate_src_graph_for_spellbook_second_tranche_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- JSON validation only.
- `OK_EXPANDED_GRAPH_AFTER_SPELLBOOK_PLAN_PATCH`
- `OK_CANONICAL_GRAPH_AFTER_SPELLBOOK_PLAN_PATCH`
- `OK_EXPANDED_GRAPH_AFTER_SPELLBOOK_SYSTEM_PATCH`
- `OK_CANONICAL_GRAPH_AFTER_SPELLBOOK_SYSTEM_PATCH`
- Recommended commands:
  - `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null`

## Risks / Rollback Notes
- Risk: the second tranche widens into low-signal plan/helper coverage.
  Rollback: stop at the next meaningful structural boundary and hand the story
  off once the planning/system layer stops getting denser in useful ways.

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
  - system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the active `spellbook` story is complete or the
  working copy is replaced by a later patch-lane artifact.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T20:29:57Z
  TYPE: PLAN
  CLAIM: The second `spellbook` tranche should not reopen the already-modeled
    root binding objects. The next useful layer is the deeper SpellCrafter
    planning/system-validation family that sits above the rooted blueprint and
    below the later codegen/runtime consumers.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_spellbook_first_tranche_task.md: latest note stack
  - codex/context_compass/system_docs/src_graph.json: current spellbook graph shape
  IMPACT: The story can keep moving without turning the first spellbook tranche
    into one giant task.
  NEXT: choose the next high-value planning/system-validation set from source
    evidence before patching the graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:31:28Z
  TYPE: FACT
  CLAIM: The next high-value set is the retained plan and system-validation
    family, not the individual validation strategies. The class boundaries show
    a tight object set around:
    - `OccurrencePlan`
    - `InjectionPlan`
    - `ExecutionPlan`
    - `OverridePatchMap`
    - `MutationPatchMap`
    - `SystemDiagnostic`
    - `SpellSystemValidationSystem`
    Those are the next real objects sitting above the rooted blueprint/system
    index layer.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:27-398
  - src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:13-472
  - src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:18-1183
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:39-852
  - src/melder/spellbook/spell_crafter/system/system_diagnostic.py:7-14
  - src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py:26-26
  IMPACT: The second tranche can stay dense and honest by focusing on retained
    plan artifacts and system-level validation surfaces instead of exploding
    into every strategy leaf.
  NEXT: read the selected files by contract surface and patch the graph with
    the retained plan/system-validation objects they define.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:32:04Z
  TYPE: FACT
  CLAIM: The selected second-tranche files are the actual retained plan family
    above Phase 5:
    `OccurrencePlan` (Phase 8),
    `InjectionPlan` (Phase 9),
    `OverridePatchMap` and `MutationPatchMap` (Phase 10),
    `ExecutionPlan` (Phase 11),
    plus the system-level validation pair
    `SpellSystemValidationSystem` and `SystemDiagnostic`.
    These are not helper-only objects; they are the objects SpellCrafter later
    retains, consumes, or emits once the rooted blueprint/system index layer
    already exists.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:104-104
  - src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:339-339
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:79-79
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:524-524
  - src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:377-377
  - src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py:28-28
  - src/melder/spellbook/spell_crafter/system/system_diagnostic.py:16-16
  IMPACT: The next graph patch can stay centered on retained plan/runtime
    semantics instead of reopening earlier phase roots or exploding into
    validation-strategy leafs.
  NEXT: patch the graph with the retained Phase 8-11 plan objects and the
    system-level validation objects that consume or emit them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:34:04Z
  TYPE: FACT
  CLAIM: The second spellbook patch is now landed in the active expanded graph
    and canonical storage. The graph now includes the retained Phase 8-11 plan
    family (`OccurrencePlan`, `InjectionPlan`, `OverridePatchMap`,
    `MutationPatchMap`, `ExecutionPlan`) plus the system-level validation pair
    (`SpellSystemValidationSystem`, `SystemDiagnostic`) and the edges that tie
    them back to `SpellCrafter`, `RootResolutionBlueprint`,
    `SpellSystemIndex`, and `SpellSystemStates`.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:27-398
  - src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:13-472
  - src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:18-1183
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:39-852
  - src/melder/spellbook/spell_crafter/system/system_diagnostic.py:14-146
  - src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py:26-215
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
  IMPACT: The spellbook graph now reaches through the retained plan/runtime
    preparation layer instead of stopping at the rooted blueprint boundary.
  NEXT: decide whether the remaining second-tranche value is the builder-side
    helper seam or whether this is already coherent enough to pause and move
    deeper by another bounded slice later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:34:04Z
  TYPE: MEASURE
  CLAIM: The expanded and canonical graph both still validate as JSON after the
    retained plan/system-validation patch and recompression.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_SPELLBOOK_PLAN_PATCH`
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_SPELLBOOK_PLAN_PATCH`
  IMPACT: The working copy and canonical graph remain structurally sound while
    the spellbook story deepens into the planning layer.
  NEXT: choose whether to keep the second tranche active or pause it at this
    new coherent boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:36:31Z
  TYPE: FACT
  CLAIM: There is still one dense supporting Phase 5/system-validation seam
    worth graphing before this tranche pauses:
    `SpellSystemAdjacencyBuilder`,
    `SpellSystemAdjacencySnapshot`,
    `SpellSystemRootBlueprintBuilder`,
    `SpellSystemNode`,
    and `SpellSystemValidationState`.
    Together they explain how SpellSystemStates becomes rooted blueprints and
    how system validation returns a frame-level verdict.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:21-21
  - src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:39-138
  - src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py:9-9
  - src/melder/spellbook/spell_crafter/system/spell_system_adjacency_snapshot.py:9-9
  - src/melder/spellbook/spell_crafter/system/spell_system_node.py:12-12
  - src/melder/spellbook/spell_crafter/system/spell_system_validation_state.py:10-29
  IMPACT: One more bounded patch can make the rooted-system layer much more
    legible without exploding into strategy-level detail.
  NEXT: patch the graph with the supporting Phase 5/system-validation objects
    and the edges that connect them to `SpellSystemStates`,
    `RootResolutionBlueprint`, and `SpellSystemValidationSystem`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:38:07Z
  TYPE: FACT
  CLAIM: The supporting Phase 5/system-validation patch is now landed in the
    active expanded graph and canonical storage. The graph now includes
    `SpellSystemAdjacencyBuilder`, `SpellSystemAdjacencySnapshot`,
    `SpellSystemRootBlueprintBuilder`, `SpellSystemNode`, and
    `SpellSystemValidationState`, plus the edges that show how `SpellCrafter`
    lifts `SpellSystemStates` into an adjacency snapshot, builds rooted
    blueprints from it, stores version-scoped system nodes, and returns a
    frame-level validation verdict.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py:7-82
  - src/melder/spellbook/spell_crafter/system/spell_system_adjacency_snapshot.py:7-125
  - src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py:19-242
  - src/melder/spellbook/spell_crafter/system/spell_system_node.py:8-130
  - src/melder/spellbook/spell_crafter/system/spell_system_validation_state.py:8-82
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3904-4950
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
  IMPACT: The spellbook graph now covers the full rooted-system seam from
    `SpellSystemStates` through adjacency and rooted blueprint construction
    into system-level validation state, not just the retained plan objects.
  NEXT: decide whether the `spellbook` story is coherent enough to pause and
    hand off to the next top-level directory or whether one more dense
    spellbook slice still justifies staying here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:38:07Z
  TYPE: MEASURE
  CLAIM: The expanded and canonical graph both still validate as JSON after the
    supporting system patch and recompression.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_SPELLBOOK_SYSTEM_PATCH`
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_SPELLBOOK_SYSTEM_PATCH`
  IMPACT: The graph remains structurally sound while the second `spellbook`
    tranche deepens into the supporting rooted-system layer.
  NEXT: make a bounded coherence decision for the `spellbook` story instead of
    widening blindly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the second active `spellbook` graph-population tranche.
