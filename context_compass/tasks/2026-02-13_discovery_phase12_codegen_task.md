# Task: Discovery Phase12 Codegen

## Metadata
- Task ID: TASK-2026-02-13-discovery-phase12-codegen
- Story: STORY-2026-02-13-optimize-phase12-codegen
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## Objective
Build a discovery baseline and hotspot map for Phase 12 executor generation
paths so optimization tasks can be prioritized by measured impact.

## Scope Boundaries
- In scope:
- No-overrides and overrides Phase 12 executor emission paths.
- Emission-shape hotspots that influence runtime branch/call depth.
- Ranked optimization candidate extraction with contract constraints.
- Out of scope:
- Runtime behavior changes in this task.
- Broader SpellCrafter phase optimization outside Phase 12.

## Steps / Checklist
- [ ] Map no-overrides and overrides compiler/emitter entrypaths.
- [ ] Identify highest-cost emission steps and duplicated shaping logic.
- [ ] Record invariants that must remain stable for generated executor contracts.
- [ ] Produce ranked optimization candidates and append follow-up tasks.

## Deliverables
- Phase 12 codegen discovery baseline with evidence-backed hotspot ranking.
- Prioritized follow-up optimization candidates for Phase 12 emitter work.

## Files / Paths Impacted
- `context_compass/stories/2026-02-13_optimize_phase12_codegen_story.md`
- `context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter -k \"phase12 or codegen\"`

## Risks / Rollback Notes
- Risk: optimization candidates ignore generated-executor contract boundaries.
- Rollback: mark candidates UNKNOWN until contract constraints are evidenced.

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
  EVIDENCE: context_compass/epics/2026-02-13_optimize_melder_epic.md:51, context_compass/stories/2026-02-13_optimize_phase12_codegen_story.md:44
  IMPACT: Creating this task closes the missing ticket link and unblocks discovery execution.
  NEXT: Start emitter-path mapping in `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py` and `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`.

## Context / Handoff Summary
Task created and ready. Next step is to execute discovery and append evidence to
the linked story and task notes.
