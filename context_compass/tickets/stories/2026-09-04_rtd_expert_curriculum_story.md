# Story: Deliver the complete Expert learning level

## Metadata
- Story ID: STORY-2026-09-04-rtd-expert-curriculum
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: draft
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-04T21:36:46Z

## User Narrative
As a runtime or agent infrastructure builder, I can understand and operate mediated execution,
continuity, research, and governed change through complete examples and explicit contracts.

## Value / MRP Alignment
Make Melder's highest level discoverable and operationally useful while preserving the earlier levels'
independent value and the owner's established progression.

## Ticket Contract
- ENTRY_GATE: S1/S2 available, Advanced vocabulary agreed, scoped sources read, and task routed.
- EXECUTION_BOUNDARY: docs/expert/, all 36 Expert lesson explanations, related references and checks.
- DEPENDENCIES: S1/S2; S5 world/room concepts; current expert source and public API contracts.
- EXIT_GATE: Full chapter/lesson coverage, verified complete demonstrations, and explicit operational limits.
- FAILURE_ESCALATION: Unreproducible examples, runtime gaps, or external-state requirements are recorded.

## Requirements (Functional)
- Cover packaged self-documents, targeted agent reads, capability/codegen rooms, and workstations.
- Teach validate/materialize/import/bind/meld through a working generated application demonstration.
- Explain DevOps/admission, concurrent structural change, observation, and failure/rollback behavior.
- Cover persistence records, custody, checkpoints, restore/cold boot, drift, and external storage seams.
- Explain research sets/lanes/residency/campaigns, source/diffs/impact, compositions, previews, and notch.
- Include all 36 saved lessons, with prerequisites, exact setup, and links to relevant API/architecture.
- Feature complete demonstrations only after verifying the advertised outcome at the target revision.

## Requirements (Non-Functional)
- Keep Expert directly accessible; prerequisites explain required knowledge without hiding content.
- Distinguish example code, generated code, stored records, and real execution results explicitly.
- Preserve known limits and failure semantics without inventing successful output or an unavailable API.

## Scope Boundaries
- In scope: Expert guides/wrappers, topic mapping, source-backed lesson corrections, and verification.
- Out of scope: executing demos in the RTD rendering process or redesigning runtime subsystems.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Expert delivery scope defined; no implementation started.

## Dependencies / Related Work
S7 provides detailed references. S8 publishes tested source/version outputs; S9 audits full coverage.

## Tasks (Implementation Checklist)
- [ ] Read and map every current Expert lesson; reconcile older map counts against actual files.
- [ ] Author per-topic guides and explanations for all 36 lessons.
- [ ] Verify complete codegen, restore, and governed-change demonstrations in isolated test contexts.
- [ ] Record current limits/results and review search, contents, downloads, and cross-reference behavior.

## Acceptance Criteria
- [ ] Every required chapter and all 36 current lessons are accounted for.
- [ ] Setup order, authority, ownership, and record/live-state distinctions are explicit.
- [ ] Advertised full demonstrations are supported by current execution evidence.
- [ ] Unverified/failed behavior has a concrete disposition; no silent omission or green claim.
- [ ] Readers can jump from a feature/lesson to prerequisites, architecture, and public API.
- [ ] Advanced prerequisites and Expert-specific machinery are clearly separated in the presentation.

## Validation / Test Plan
Not run. Use the existing Expert example/probe harness on 3.14t and inspect meaningful assertions.
Exercise full demonstrations with required isolation. Validate long code, outputs, links, and rendering.

## UX / API / Data Notes
Discovery read only the first 150 lines of the large Expert map and one full Expert demonstration;
implementation must read each lesson and its relevant source before making current behavior claims.

## Risks / Mitigations
Historical VERIFY notes can lag code. Lesson 36 was labeled not yet run when inspected; no current
success is assumed. Source discovery, not the map's old 33-lesson heading, defines the coverage floor.

## Open Questions
Current correctness and resource needs of each demonstration must be measured during its scoped task.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Expert agent surfaces, continuity, research, and examples
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S6 owns the full Expert curriculum and 36 lessons, including complete operational
    demonstrations with revision-bound evidence rather than inherited verification labels.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:139-195
  - README.md:683-1030
  - UX_and_AIX_experiences/04_expert/36_an_agent_builds_a_working_system.py:1-247
  IMPACT: The highest level is a maintained learning surface with explicit contracts and outcomes.
  NEXT: Map and read all Expert lessons after the shared publication system exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No invented output, shallow smoke-only proof, or silent difficult-lesson omissions.
- [ ] No accidental execution of the corpus during documentation rendering.

## Closure Confirmation
- [ ] Owner accepts the level and all task/board state is synchronized.

## Noting Behavior
Record verified operational sequences, current limitations, output evidence, and cross-reference needs.

## Context / Handoff Summary
Defined, not implemented. Deliver all Expert guides and lessons with honest, current operational evidence.
