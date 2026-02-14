# Epic: Optimize Melder Runtime and Codegen

## Metadata
- Epic ID: EPIC-2026-02-13-optimize-melder
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14
- Target Window: 2026-Q1
- Related Program/Initiative: Melder Performance Wave

## Problem / Opportunity
Melder has multiple performance-critical planes (`conjure`, `meld`,
SpellCrafter phases, CreationContext codegen, and Phase 12 codegen). We need a
single structured epic to drive discovery-first optimization and prevent
scattershot changes.

## MRP Alignment (Most Reasonable Product)
This epic keeps optimization work coherent and durable by starting with explicit
discovery in each subsystem before implementation tasks. That preserves
correctness while improving throughput and latency on real runtime paths.

## Goals (Outcomes)
- Establish discovery baselines for each targeted optimization surface.
- Produce ranked, evidence-backed optimization opportunities per surface.
- Convert discovery outputs into scoped follow-up tasks without widening scope.

## Non-Goals (Explicit Exclusions)
- Immediate broad refactors without subsystem-level discovery evidence.
- Public API redesign as part of this planning pass.
- Mutation research/runtime wiring work (currently out of scope).

## Scope Boundaries
- In scope:
- `conjure` performance path discovery.
- `meld` performance path discovery.
- SpellCrafter phase performance discovery.
- CreationContext codegen performance discovery.
- Phase 12 codegen performance discovery.
- Out of scope:
- Unrelated architecture/doc revalidation work already closed.
- Mutation research runtime wiring.

## Success Metrics
- Five linked stories exist with clear discovery tasks and acceptance criteria.
- Each discovery story yields a prioritized optimization task list with evidence.
- Epic remains traceable and compaction-safe via ticket linkage.

## Requirements (Functional + Non-Functional)
- Every story under this epic starts with exactly one discovery task.
- Discovery outputs must include: baseline, hotspot map, and candidate actions.
- Maintain Unknowns Gate discipline: unverified claims stay UNKNOWN.
- Keep implementation changes out of this setup pass.

## Constraints / Assumptions
- Constraints:
- Use existing ticket templates and folder conventions.
- Keep planning artifacts reviewable and cross-linked.
- Assumptions:
- Existing benchmark/test harnesses are available for later discovery validation.

## Dependencies / External References
- `context_compass/WORKFLOW.md`
- `context_compass/templates/epic_template.md`
- `context_compass/templates/story_template.md`
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Discovery scaffolding created and approved for all five stories.
- [ ] Milestone 2: Discovery tasks completed with evidence-backed findings.
- [ ] Milestone 3: Follow-up implementation tasks added and prioritized.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-13-optimize-conjure-paths - Discovery-first optimization plan for conjure paths.
- [ ] Story: STORY-2026-02-13-optimize-meld-paths - Discovery-first optimization plan for meld paths.
- [ ] Story: STORY-2026-02-13-optimize-spellcrafter-phases - Discovery-first optimization plan for SpellCrafter phases.
- [ ] Story: STORY-2026-02-13-optimize-creation-context-codegen - Discovery-first optimization plan for CreationContext codegen.
- [ ] Story: STORY-2026-02-13-optimize-phase12-codegen - Discovery-first optimization plan for Phase 12 codegen.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-13-optimize-conjure-paths.
- [ ] Task: Complete story STORY-2026-02-13-optimize-meld-paths.
- [ ] Task: Complete story STORY-2026-02-13-optimize-spellcrafter-phases.
- [ ] Task: Complete story STORY-2026-02-13-optimize-creation-context-codegen.
- [ ] Task: Complete story STORY-2026-02-13-optimize-phase12-codegen.
- [ ] Task: Keep architecture/components docs synced when optimization behavior changes.

## Acceptance Criteria (Epic Done)
- All five discovery stories are completed and accepted by the user.
- Each story includes evidence-backed findings and concrete follow-up tasks.
- Optimization scope and priority order are agreed for implementation phase.

## Risks / Mitigations
- Risk: premature optimization without evidence.
  Mitigation: discovery-first gate in every story.
- Risk: scope creep across runtime subsystems.
  Mitigation: strict story boundaries and explicit out-of-scope sections.

## Validation / Test Approach
- Discovery validation via code-path evidence and targeted benchmark/test runs as
  applicable per story.
- No blanket claims without explicit run output.

## Rollout / Adoption Plan
- Complete discovery in each story.
- Review findings with user.
- Expand each story with implementation tasks in priority order.

## Open Questions
- What throughput/latency targets should define success for this wave?
- Which workloads should be treated as primary optimization baselines?

## Decision Log
- 2026-02-13: User requested a new optimization epic with five discovery-first stories.

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: SpellCrafter rank-1 execution task is implemented and in review with major warm 8-11 reduction after phase8-11 dirty-capture rollout.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:6-58, context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:60-90, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-9
  IMPACT: Epic’s SpellCrafter branch has moved from planning-only into high-impact validated implementation.
  NEXT: Confirm rank-1 acceptance and continue with rank-2 signature pipeline task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: SpellCrafter discovery moved from ready to execution-ready: hotspot mapping is complete and three ranked follow-up tasks are now queued under the story.
  EVIDENCE: context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md:6-113, context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:6-55, context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:1-76, context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:1-76, context_compass/tasks/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-77
  IMPACT: Epic progress advanced on the SpellCrafter branch and now has concrete next implementation targets.
  NEXT: Execute rank-1 SpellCrafter follow-up task while continuing remaining discovery tracks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

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
Epic created with five linked discovery-first stories for optimization of
conjure, meld, SpellCrafter phases, CreationContext codegen, and Phase 12
codegen. Meld discovery is now complete and documented with ranked hotspot
candidates and follow-up implementation tasks in
`context_compass/stories/2026-02-13_optimize_meld_paths_story.md`. SpellCrafter
discovery is now complete and execution-ready with three ranked follow-up tasks
queued. Rank-1 is now implemented and in review with strong warm 8-11 gains.
Next step is acceptance of rank-1 and execution of SpellCrafter rank-2 while
continuing remaining discovery tracks for creation-context and phase12 codegen
stories.
