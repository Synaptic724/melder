# Story: Design conduit-scoped change-control semantics

- Completed: 2026-02-03
- Summary: Conduit-scoped change-control design documented with scoping key, contracted-spell rules, and call-site impacts.

## Metadata
- Story ID: STORY-2026-02-01-change-control-conduit-scope
- Epic: EPIC-2026-02-01-conduit-scoped-devops-phase5-7
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-03

## User Narrative
As a Melder maintainer, I want conduit-scoped change-control semantics so that component_of and revalidation do not cross-contaminate between conduits in the same frame.

## Value / MRP Alignment
Defines the durable, correct scoping model for multi-conduit frames, preventing last-writer-wins behavior and preserving isolation guarantees.

## Requirements (Functional)
- Define conduit-scoped component_of mapping and revalidator registration behavior.
- Specify how contracted spells are included/excluded in the conduit-scoped model.
- Identify required API changes across DevOps and Phase 5/7 call sites.

## Requirements (Non-Functional)
- Evidence-backed; no assumptions.
- Minimize public API changes.

## Scope Boundaries
- In scope:
  - ChangeControlManager data structures and public methods.
  - Phase 5/7 integration points.
- Out of scope:
  - Implementation changes and tests (covered by separate story).

## Dependencies / Related Work
- Story: STORY-2026-02-01-devops-scope-audit

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-01-change-control-conduit-scope-design - Design conduit-scoped component_of and revalidator.

## Acceptance Criteria
- A clear, documented design exists for conduit-scoped change-control behavior.
- All affected APIs and call sites are identified.

## Validation / Test Plan
- Not applicable (design only).

## UX / API / Data Notes
- Potential API changes must be enumerated.

## Risks / Mitigations
- Risk: Contracted spells semantics are unclear.
  Mitigation: Explicit decision logged with evidence.

## Open Questions
- Should component_of be keyed by conduit_id or root conduit_id?
- How should spellbooks sharing a frame coordinate revalidation?

## Decision Log
- 2026-02-01: Story created under conduit-scoped DevOps epic.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Design task completed with a recommended conduit-scoped model keyed by resolution conduit id (root for lessers), inclusion of spellbook-visible contracted spells, and an impacted call-site map (Meld/MeldRuntime gating, SpellCrafter Phase 5/7, Aether revalidation, TransferOfOwnership incident path). See TASK-2026-02-01-change-control-conduit-scope-design for details.
