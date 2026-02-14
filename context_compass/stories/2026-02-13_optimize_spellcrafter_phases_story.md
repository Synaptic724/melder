# Story: Optimize SpellCrafter Phases

## Metadata
- Story ID: STORY-2026-02-13-optimize-spellcrafter-phases
- Epic: EPIC-2026-02-13-optimize-melder
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want SpellCrafter phase costs mapped and prioritized,
so that phase execution remains efficient as graph complexity grows.

## Value / MRP Alignment
SpellCrafter phase overhead impacts both conjure preparation and runtime safety.
Discovery-first optimization gives us a stable path to reduce overhead safely.

## Requirements (Functional)
- Identify highest-cost SpellCrafter phase operations and data-flow bottlenecks.
- Produce ranked optimization opportunities with evidence.
- Capture follow-up implementation tasks from discovery findings.

## Requirements (Non-Functional)
- Discovery pass must not alter phase semantics.
- Findings must include reproducible evidence references.

## Scope Boundaries
- In scope:
- SpellCrafter phase execution path and phase-generated artifacts.
- Phase-level validation and planning overhead analysis.
- Out of scope:
- Direct meld dispatch optimization.
- Mutation research runtime wiring.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py`
- `src/melder/spellbook/spell_crafter/dag/resolution_frame/resolution_frame.py`
- `EPIC-2026-02-13-optimize-melder`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-13-discovery-spellcrafter-phases - Build discovery baseline, hotspot map, and prioritized optimization candidates for SpellCrafter phases. (`context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md`)

## Acceptance Criteria
- Discovery output identifies top SpellCrafter phase hotspots with evidence.
- Follow-up optimization tasks are documented and prioritized.

## Validation / Test Plan
- Use targeted code-path inspection and relevant existing test/benchmark hooks.
- Record commands and outputs for any executed measurements.

## UX / API / Data Notes
- Internal optimization planning only; no API change in discovery pass.

## Risks / Mitigations
- Risk: optimizing one phase causes regressions in others.
  Mitigation: capture per-phase boundaries and dependencies in findings.

## Open Questions
- Which phase groups should be treated as highest ROI for the first implementation pass?

## Decision Log
- 2026-02-13: Story created from user-requested optimization epic setup.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story is ready with one discovery task. Next step is to collect phase-path
baselines and hotspot evidence before adding implementation tasks.

