- Completed: 2026-01-22
- Summary: Completed structure profiles and AI-facing tooling with provenance.

# Epic: Fuzzy Structure Profiles and Tools

## Metadata
- Epic ID: EPIC-2026-01-21-melder-structure-profiles-tools
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-21
- Target Window: 2026-Q1
- Related Program/Initiative: AI structure intelligence

## Problem / Opportunity
Melder does not yet expose structure profiles or AI-facing structure tools
that provide fuzzy, provenance-tagged system context. We need a structured
profile family that can be consumed by future AethericRift tooling.

## MRP Alignment (Most Reasonable Product)
The MRP is a reliable, explicit structure profile layer with clear provenance
and ranked hints, without claiming perfect truth.

## Goals (Outcomes)
- Define structure profile types at frame/conduit/spellbook scope.
- Separate truth artifacts from fuzzy derived hints with provenance.
- Provide AI-facing structure tool outputs (queries) as profile consumers.

## Non-Goals (Explicit Exclusions)
- Enforcing ACLs during profile generation.
- Replacing static analyzers or proving complete call graphs.
- Network/auth/transport work for AethericRift.

## Scope Boundaries
- In scope:
  - Structure profile schema design and tool query surfaces.
  - Integration points with runtime evidence (spells, resolution, contracts).
- Out of scope:
  - AethericRift exposure and policy enforcement.
  - Repo-wide refactors unrelated to profiling.

## Success Metrics
- A frame-level structure profile can be generated from runtime evidence.
- Tools can return ranked related spells and at least one cluster candidate.
- Fuzzy outputs carry provenance and confidence tags.

## Requirements (Functional + Non-Functional)
- Explicit truth vs derived separation.
- Provenance and confidence per derived hint.
- Extensible schema without breaking consumers.

## Constraints / Assumptions
- Dataclasses are value-only; profile objects with nested data must use
  normal classes with cleanup if needed.
- No TYPE_CHECKING or future annotations.

## Dependencies / External References
- Future AethericRift tooling (downchain consumer).

## Milestones (Track Progress)
- [x] Milestone 1: Investigation completed and schema proposal drafted.
- [x] Milestone 2: Profile types implemented with truth/derived separation.
- [x] Milestone 3: Tool queries return ranked results with provenance.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-21-melder-structure-profiles-tools - Build structure profiles and tools.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-21-melder-structure-profiles-tools

## Acceptance Criteria (Epic Done)
- Structure profile types exist and support frame/conduit/spellbook scopes.
- Tool outputs provide ranked hints with provenance.
- Degradation behavior is explicit for weak-signal projects.

## Risks / Mitigations
- Risk: Fuzzy hints overclaim accuracy.
  - Mitigation: enforce provenance/confidence fields and explicit labeling.

## Validation / Test Approach
- Targeted unit/component tests for profile generation and tool queries.

## Rollout / Adoption Plan
- Land schema and truth signals first, then add fuzzy hints incrementally.

## Open Questions
- Which clustering heuristic is acceptable for v1?

## Decision Log
- 2026-01-21: Start structure profile + tool effort for AI consumption.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to define structure profiles and AI-facing tools with truth and
fuzzy signals separated and provenance-tagged.
Story tasks are complete; acceptance confirmed and ready for closeout.
