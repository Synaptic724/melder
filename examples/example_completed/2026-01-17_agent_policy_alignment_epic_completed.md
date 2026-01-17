# Epic: Agent Policy and Documentation Standards Alignment

- Completed: 2026-01-17
- Summary: Codified agent stance, MRP-first framing, and documentation standards across policy and architecture docs.

## Metadata
- Epic ID: EPIC-2026-01-17-agent-policy-alignment
- Status: done
- Owner:
- Priority: p0
- Created: 2026-01-17
- Updated: 2026-01-17
- Target Window: 2026-Q1
- Related Program/Initiative: CommandOps Core

## Problem / Opportunity
The current agent policy documents do not fully encode the required collaboration stance,
MRP-only product framing, tone constraints, and documentation quality standards. This
creates drift in how the agent communicates, prioritizes context, and documents the core
system in a way that is durable across context compaction.

## MRP Alignment (Most Reasonable Product)
These policy updates are the minimal coherent foundation for how the agent works in this
repo. They set the durable core expectations for communication, documentation, and
MRP-first product strategy without introducing unnecessary scope.

## Goals (Outcomes)
- Codify team-oriented engagement, direct technical tone, and professional baseline framing.
- Make recommendations conditional on real tradeoffs or explicit user requests.
- Embed the MRP definition (with MLP for UI contexts) and explicitly reject MVP.
- Add a skills folder with supporting policy docs referenced by AGENTS/SKILLS.
- Add documentation quality standards to architecture/components docs.

## Non-Goals (Explicit Exclusions)
- Runtime code changes.
- Test changes.
- Refactoring existing policy sections not touched by the new requirements.

## Scope Boundaries
- In scope:
  - `codex_todo/AGENTS.MD`, `codex_todo/SKILLS.MD`
  - new `codex_todo/skills/` policy docs
  - `codex_todo/architecture/src_architecture.md`
  - `codex_todo/components/src_components.md`
- Out of scope:
  - Implementation code in `src/`
  - Test or CI changes

## Success Metrics
- AGENTS and SKILLS reflect the updated stance, tone, and MRP-only strategy.
- New skills docs exist and are referenced from SKILLS/AGENTS.
- Architecture and components docs include explicit documentation quality standards.

## Requirements (Functional + Non-Functional)
- Keep changes ASCII-only and consistent with existing formatting.
- Explicitly instruct re-entry ritual after context compaction (read architecture/components docs first).
- Ensure MRP definition is unambiguous and MVP is disallowed.

## Constraints / Assumptions
- Follow the Propose -> Confirm -> Implement protocol for edits.
- No new tooling or dependencies introduced.

## Dependencies / External References
- `codex_todo/AGENTS.MD`
- `codex_todo/SKILLS.MD`
- `codex_todo/architecture/src_architecture.md`
- `codex_todo/components/src_components.md`

## Milestones (Track Progress)
- [x] Milestone 1: Policy updates in AGENTS/SKILLS and new skills docs created.
- [x] Milestone 2: Doc standards added to architecture/components docs.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-17-agent-policy-alignment - Update agent policy and doc standards.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-17-agent-policy-alignment

## Acceptance Criteria (Epic Done)
- All required policy changes are present in AGENTS/SKILLS.
- New skills docs exist under `codex_todo/skills/` and are referenced.
- Architecture/components docs include explicit documentation quality standards.

## Risks / Mitigations
- Risk: Policy duplication across docs. Mitigation: centralize details in skills docs and reference them.

## Validation / Test Approach
- Documentation-only changes; no tests required.

## Rollout / Adoption Plan
- Use the updated docs as the default operating policy for future sessions.

## Open Questions
- None.

## Decision Log
- 2026-01-17: Create a dedicated skills folder for policy extensions.

## Context / Handoff Summary
- Completed. AGENTS/SKILLS updated, skills policy docs created, and doc standards added to architecture/components.
