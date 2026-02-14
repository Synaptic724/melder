# Task: Discovery CreationContext Codegen

## Metadata
- Task ID: TASK-2026-02-13-discovery-creation-context-codegen
- Story: STORY-2026-02-13-optimize-creation-context-codegen
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## Objective
Build a discovery baseline and hotspot map for CreationContext lane/codegen
dispatch paths so optimization work stays contract-safe and measurable.

## Scope Boundaries
- In scope:
- CreationContext lane routing and specialization paths.
- Codegen-connected helper paths that affect CreationContext runtime overhead.
- Ranked optimization candidate extraction from discovery findings.
- Out of scope:
- Broad conjure orchestration changes.
- Standalone Phase 12 compiler internals outside CreationContext integration.

## Steps / Checklist
- [x] Map CreationContext route families and call-count/branch-count hotspots.
- [x] Identify repeated allocations and avoidable dispatch overhead on hot lanes.
- [x] Capture constraints that must remain stable for route contracts.
- [x] Produce ranked optimization candidates and append follow-up tasks.

## Deliverables
- CreationContext codegen discovery baseline with evidence-backed hotspot ranking.
- Prioritized follow-up optimization candidates for CreationContext lanes.

## Files / Paths Impacted
- `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md`
- `context_compass/tasks/2026-02-13_discovery_creation_context_codegen_task.md`
- `context_compass/tasks/2026-02-14_optimize_creation_context_override_shape_preprocessing_task.md`
- `context_compass/tasks/2026-02-14_optimize_creation_context_override_miss_compile_reuse_task.md`
- `context_compass/tasks/2026-02-14_optimize_creation_context_override_prefilter_caching_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld -k \"creation_context or runtime\"`

## Risks / Rollback Notes
- Risk: overfitting findings to one lane family.
- Rollback: split findings by route family and leave missing families as UNKNOWN.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Discovery ranking finalized with three follow-up tasks: (1) override shape preprocessing reduction, (2) override miss compile reuse, (3) override prefilter caching.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_creation_context_override_shape_preprocessing_task.md:1-63, context_compass/tasks/2026-02-14_optimize_creation_context_override_miss_compile_reuse_task.md:1-64, context_compass/tasks/2026-02-14_optimize_creation_context_override_prefilter_caching_task.md:1-62
  IMPACT: Story is now execution-ready with ranked optimization backlog and concrete implementation scopes.
  NEXT: Sync story checklist/notes and request user acceptance for discovery closure before starting rank-1 task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Override-specialization cache misses trigger full Phase12 override compilation without pre-supplied source: `_get_or_compile_override_executor` calls `compile_phase12_overrides_executor`, which rebuilds step-target filters, emits source, then executes `compile+exec` to produce `_phase12_executor`.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:860-890, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:176-214, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:281-347, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:668-719
  IMPACT: Shape churn on override calls can pay a substantial miss-path compilation tax; this is a ranked discovery candidate for compile-path caching or miss-path preprocessing reduction.
  NEXT: Build ranked candidate list (per-call override preprocessing vs miss-path compiler work vs kwargs materialization) and draft follow-up implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: CreationContext route generation already splits no-overrides and overrides into dedicated doors for five resolve routes, and the `many` no-overrides lane has an explicit fast transient template (`_no_overrides_executor()` direct call), while override-bearing lanes consistently route into `_execute_with_overrides`.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:74-81, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:170-177, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:443-457, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:590-597, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:599-810
  IMPACT: Discovery ranking should bias toward override-path preprocessing/compiler cache behavior rather than no-overrides transient lanes, which already have dedicated fastpath generation.
  NEXT: Trace override specialization compile flow (`compile_phase12_overrides_executor`) to identify repeated miss-path shaping/filtering costs and build ranked candidates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Override-bearing runtime calls always compute `socket_shape` before specialization-cache lookup, and cache misses with non-empty overrides run a second full override-map walk to build grouped targets; for payloads with 3+ sockets this includes per-call sort work.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:570-589, src/melder/aether/conduit/meld/creation_context/creation_context.py:653-720, src/melder/aether/conduit/meld/creation_context/creation_context.py:722-839
  IMPACT: This is a high-confidence discovery candidate for override-heavy lanes because per-call preprocessing cost exists before cache-hit resolution and doubles on cache misses.
  NEXT: Map which generated route families hit `_execute_with_overrides` most frequently and rank this candidate against no-overrides route dispatch costs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Activated this discovery task as the current phase-ticket route after SpellCrafter rank-3 closure.
  EVIDENCE: context_compass/attention_board.md:23-25, context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-15
  IMPACT: Investigation now proceeds on CreationContext codegen hotspots with ticket-first note logging.
  NEXT: Map CreationContext route families and identify first meaningful hotspot finding with source anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: This story requires exactly one discovery task and already references this task ID.
  EVIDENCE: context_compass/epics/2026-02-13_optimize_melder_epic.md:51, context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:45
  IMPACT: Creating this task closes the missing ticket link and unblocks discovery execution.
  NEXT: Start route-family mapping in `src/melder/aether/conduit/meld/creation_context/creation_context.py`.

## Context / Handoff Summary
Discovery is complete and in review. Ranked follow-up tasks are created and
ready; next step is user acceptance for closure and rank-1 implementation start.
