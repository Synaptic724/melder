# Task: Discovery SpellCrafter Phases

## Metadata
- Task ID: TASK-2026-02-13-discovery-spellcrafter-phases
- Story: STORY-2026-02-13-optimize-spellcrafter-phases
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## Objective
Build a source-anchored hotspot map for SpellCrafter phase execution and
phase-artifact lifecycle so follow-up optimization tasks are evidence-backed.

## Scope Boundaries
- In scope:
- SpellCrafter phase path analysis for structural, foundational, and plan phases.
- Artifact creation/cleanup and invalidation boundaries that affect phase cost.
- Hotspot ranking and candidate-task extraction.
- Out of scope:
- Runtime semantic changes in this task.
- Meld front-door optimization and mutation runtime wiring.

## Steps / Checklist
- [ ] Map phase entrypoints and call ordering contracts in SpellCrafter paths.
- [ ] Identify highest-cost operations and repeated allocations per phase group.
- [ ] Capture phase-artifact lifecycle/invalidation boundaries that impact cost.
- [ ] Produce ranked optimization candidates and append follow-up tasks.

## Deliverables
- Discovery baseline with per-phase hotspot map and evidence anchors.
- Prioritized follow-up optimization candidates for SpellCrafter phases.

## Files / Paths Impacted
- `context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md`
- `context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter -k phase`

## Risks / Rollback Notes
- Risk: phase-level claims drift from real call order.
- Rollback: keep findings as UNKNOWN until source ordering is verified.

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
  EVIDENCE: context_compass/epics/2026-02-13_optimize_melder_epic.md:51, context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:44
  IMPACT: Creating this task closes the missing ticket link and unblocks discovery execution.
  NEXT: Start call-path mapping in `src/melder/spellbook/spell_crafter/spell_crafter.py`.

## Context / Handoff Summary
Task created and ready. Next step is to execute discovery and append evidence to
the linked story and task notes.
