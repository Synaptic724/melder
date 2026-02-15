- Completed: 2026-01-22
- Summary: Delivered structure profile models, tooling queries, and unit tests.

# Story: Structure profiles and AI-facing tools

## Metadata
- Story ID: STORY-2026-01-21-melder-structure-profiles-tools
- Epic: EPIC-2026-01-21-melder-structure-profiles-tools
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-21

## User Narrative
As a maintainer, I want structure profiles and AI-facing tools so models can
get grounded, provenance-tagged system context without guessing.

## Value / MRP Alignment
This provides the minimal, trustworthy structure layer needed for future
tool exposure and AI reasoning.

## Requirements (Functional)
- Structure profiles at frame/conduit/spellbook scope.
- Truth artifacts separated from fuzzy hints.
- Tool queries return ranked results with provenance and confidence.

## Requirements (Non-Functional)
- No ACL enforcement at profile stage.
- Extensible schema without breaking consumers.

## Scope Boundaries
- In scope:
  - Profile schemas, data sources, and tool query outputs.
- Out of scope:
  - AethericRift exposure/policy.
  - Network/auth/transport.

## Dependencies / Related Work
- Task: TASK-2026-01-21-melder-structure-profiles-tools-investigation
- Task: TASK-2026-01-21-melder-structure-profiles-tools-implementation

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-21-melder-structure-profiles-tools-investigation - Inventory data sources and propose schema.
- [x] Task: TASK-2026-01-21-melder-structure-profiles-tools-implementation - Implement profiles and tool outputs.

## Acceptance Criteria
- A frame-level structure profile is generated from runtime evidence.
- Tool outputs identify related spells and at least one cluster candidate.
- Fuzzy hints include provenance and confidence scores.

## Validation / Test Plan
- Unit tests for profile generation and tool output shaping.

## UX / API / Data Notes
- Outputs are designed as AI-facing tools; exposure is downchain.

## Risks / Mitigations
- Risk: Derived hints are overconfident.
  - Mitigation: require provenance/confidence for every hint.

## Open Questions
- Cluster algorithm selection for v1.

## Decision Log
- 2026-01-21: Start structure profile + tool story.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to deliver structure profiles and AI-facing tool outputs.
Investigation and implementation tasks are complete; user reported passing the
structure profile builder unit tests. Acceptance confirmed; ready for closeout.
