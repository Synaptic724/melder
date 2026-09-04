# Story: Deliver the complete Advanced learning level

## Metadata
- Story ID: STORY-2026-09-04-rtd-advanced-curriculum
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: draft
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-04T21:36:46Z

## User Narrative
As a reader building isolated or inspectable systems, I can choose world boundaries, query live state,
and apply precise targeting while understanding configuration, authority, and ownership.

## Value / MRP Alignment
Provide the owner's third level as a clear progression from subsystem composition to multi-world control.

## Ticket Contract
- ENTRY_GATE: S1/S2 available, Intermediate vocabulary agreed, current sources read, and task routed.
- EXECUTION_BOUNDARY: docs/advanced/, all 19 Advanced lesson explanations, relevant links and checks.
- DEPENDENCIES: S1/S2; S4 concepts; source-backed frame/room/override contracts.
- EXIT_GATE: Complete guide/lesson coverage and verified isolation/inspection walkthrough.
- FAILURE_ESCALATION: Record current API gaps, metadata contradictions, or needed runtime work separately.

## Requirements (Functional)
- Distinguish spellframe, conduit, and aetheric frame with concrete pictures and examples.
- Cover frame posture, root configuration/logging, deep/wildcard/broadcast overrides, and clusters.
- Explain Nexus/Rift setup, static rooms, viewer/describe depth, visibility gaps, and workstation ownership.
- Cover policy/authority boundaries and the checkpoint/load entry points in existing Advanced lessons.
- Publish all 19 saved lessons; cross-link cluster material in its existing source location.
- Provide an isolated-world inspection walkthrough and links into deeper Expert operations.

## Requirements (Non-Functional)
- Preserve the Advanced name/color and exact place in the four-level hierarchy.
- State required setup and what a surface can observe/modify; keep public examples runnable.
- Do not turn historical concept-map findings into present-day claims without source verification.

## Scope Boundaries
- In scope: Advanced guide prose, wrappers, diagrams/references, lesson checks, and source-backed corrections.
- Out of scope: reclassifying source folders or redesigning frame/room runtime APIs.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Advanced delivery scope defined; no implementation started.

## Dependencies / Related Work
S6 builds on world/room boundaries. S7 supplies architectural drawings, glossary, and public API links.

## Tasks (Implementation Checklist)
- [ ] Map all chapters and lessons, including explicit cross-level topic links.
- [ ] Author isolation, configuration, targeting, and inspection explanations.
- [ ] Verify lesson setup, authority outcomes, and lifecycle behavior against the current revision.
- [ ] Review complete contents, diagrams, and the Advanced-to-Expert continuation.

## Acceptance Criteria
- [ ] All required chapters and 19 saved lessons are discoverable and complete.
- [ ] The three frame/scope concepts are explained without interchangeable terminology.
- [ ] Setup and authority/visibility boundaries match current public contracts.
- [ ] Large diagrams remain usable and have adjacent explanatory text.
- [ ] No lesson is moved or omitted to resolve a topic overlap.
- [ ] Current verification results, prerequisites, API links, and next-depth routes are recorded.

## Validation / Test Plan
Not run. Run applicable Advanced lesson/probe harnesses on 3.14t, inspect real outcomes, then verify
HTML, complete contents, cross-level links, images, commands, and mobile/keyboard readability.

## UX / API / Data Notes
Advanced introduces broader boundaries and deeper inspection; the site must let readers choose depth.

## Risks / Mitigations
Source/configuration APIs have evolved since some map notes. Read the relevant implementations before
rewriting lessons, and raise inaccessible public paths as explicit findings rather than inventing a seam.

## Open Questions
Per-lesson source drift and the exact reusable drawing subset are determined during implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Advanced isolation, rooms, targeting, and examples
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S5 owns the full Advanced level and 19 saved lessons, with source-backed world/room
    boundaries and clear links to overlapping Intermediate examples and deeper Expert material.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:117-138
  - README.md:598-670
  - UX_and_AIX_experiences/03_advanced/_concept_map.txt:1-321
  IMPACT: Advanced has its own meaningful outcomes without becoming an undifferentiated feature list.
  NEXT: Map Advanced guide chapters and current source contracts after S1/S2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No inferred authority, stale setup paths, or inaccessible drawings.
- [ ] No automatic tier changes to existing lessons.

## Closure Confirmation
- [ ] Owner accepts the level and task/board state is synchronized.

## Noting Behavior
Record setup/API drift, verified authority, diagram needs, and dependencies handed to Expert.

## Context / Handoff Summary
Defined, not implemented. Deliver the complete isolation/inspection level and all Advanced lessons.
