# Task: Discovery CreationContext Codegen

## Metadata
- Task ID: TASK-2026-02-13-discovery-creation-context-codegen
- Story: STORY-2026-02-13-optimize-creation-context-codegen
- Status: ready
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
- [ ] Map CreationContext route families and call-count/branch-count hotspots.
- [ ] Identify repeated allocations and avoidable dispatch overhead on hot lanes.
- [ ] Capture constraints that must remain stable for route contracts.
- [ ] Produce ranked optimization candidates and append follow-up tasks.

## Deliverables
- CreationContext codegen discovery baseline with evidence-backed hotspot ranking.
- Prioritized follow-up optimization candidates for CreationContext lanes.

## Files / Paths Impacted
- `context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md`
- `context_compass/tasks/2026-02-13_discovery_creation_context_codegen_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld -k \"creation_context or runtime\"`

## Risks / Rollback Notes
- Risk: overfitting findings to one lane family.
- Rollback: split findings by route family and leave missing families as UNKNOWN.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: This story requires exactly one discovery task and already references this task ID.
  EVIDENCE: context_compass/epics/2026-02-13_optimize_melder_epic.md:51, context_compass/stories/2026-02-13_optimize_creation_context_codegen_story.md:45
  IMPACT: Creating this task closes the missing ticket link and unblocks discovery execution.
  NEXT: Start route-family mapping in `src/melder/aether/conduit/meld/creation_context/creation_context.py`.

## Context / Handoff Summary
Task created and ready. Next step is to execute discovery and append evidence to
the linked story and task notes.
