# Story: Optimize Phase 12 Codegen

## Metadata
- Story ID: STORY-2026-02-13-optimize-phase12-codegen
- Epic: EPIC-2026-02-13-optimize-melder
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want Phase 12 codegen hotspots mapped and prioritized,
so that emitted executors are lean and fast across override and non-override lanes.

## Value / MRP Alignment
Phase 12 emission quality materially affects runtime hot paths. Discovery-first
work ensures optimization effort lands where it gives the highest systemic value.

## Requirements (Functional)
- Identify major cost centers in Phase 12 code generation and emitted executor shape.
- Produce ranked optimization opportunities with evidence.
- Capture follow-up implementation tasks from discovery findings.

## Requirements (Non-Functional)
- Discovery pass must not alter runtime behavior.
- Findings must be grounded in concrete source evidence and measurement notes.

## Scope Boundaries
- In scope:
- Phase 12 no-overrides and overrides executor emission paths.
- Executor-shape and branching-cost discovery for generated code.
- Out of scope:
- Broader SpellCrafter phase optimization outside Phase 12.
- Mutation research runtime wiring.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `EPIC-2026-02-13-optimize-melder`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-13-discovery-phase12-codegen - Build discovery baseline, hotspot map, and prioritized optimization candidates for Phase 12 codegen. (`context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md`)

## Acceptance Criteria
- Discovery output identifies top Phase 12 codegen hotspots with evidence.
- Follow-up optimization tasks are documented and prioritized.

## Validation / Test Plan
- Use targeted code-path inspection and relevant existing test/benchmark hooks.
- Record commands and outputs for any executed measurements.

## UX / API / Data Notes
- Internal optimization planning only; no API change in discovery pass.

## Risks / Mitigations
- Risk: generated-code optimizations introduce semantic drift.
  Mitigation: discovery output must tie each candidate to contract-preserving constraints.

## Open Questions
- Should Phase 12 prioritize branch-count reduction, call-count reduction, or cache locality first?

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
Story is ready with one discovery task. Next step is to collect Phase 12 codegen
baselines and hotspot evidence before adding implementation tasks.

