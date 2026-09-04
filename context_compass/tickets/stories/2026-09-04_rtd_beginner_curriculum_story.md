# Story: Deliver the complete Beginner learning level

## Metadata
- Story ID: STORY-2026-09-04-rtd-beginner-curriculum
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: in_progress
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-04T21:36:46Z

## User Narrative
As a first-time user, I can build, resolve, scope, and clean up a useful application without needing
advanced runtime concepts before my first working result.

## Value / MRP Alignment
Preserve the owner's low-entry-cost curriculum as a complete, independently useful learning level.

## Ticket Contract
- ENTRY_GATE: S1/S2 contracts exist; README and beginner sources are read; a bounded task is routed.
- EXECUTION_BOUNDARY: docs/beginner/, explanatory wrappers for all 41 beginner lessons, related links,
  and source-backed corrections to beginner examples only when required by their public contracts.
- DEPENDENCIES: S1 navigation/build; S2 catalog; settled disposal contract from codex_1's separate lane.
- EXIT_GATE: Required chapters and every lesson are covered, rendered, and verified with honest evidence.
- FAILURE_ESCALATION: Runtime defects or unsettled ownership/disposal behavior become separate findings.

## Requirements (Functional)
- Cover installation/first run, Hello Melder, bind/conjure/meld, binding forms, address law, spellframes,
  typed resolution, three basic lifetimes, child scopes, bootstrap, disposal, memory, and useful errors.
- Provide the beginner capstone as a complete application with explained results and cleanup.
- Include all 41 saved lessons in their existing order, plus topic links from the concept map.
- Use public md.* vocabulary and concrete examples. Preserve level labels and the first-depth sidebar.
- Keep prerequisites short; future-level links are optional depth, not hidden requirements.

## Requirements (Non-Functional)
- Static first-contact path; advanced subsystems do not become prerequisites.
- Every code block is canonical source or an explicitly verified authored snippet.
- Align guide text with source behavior and the current documented revision.

## Scope Boundaries
- In scope: beginner guides, example explanations, glossary/API links, and focused lesson verification.
- Out of scope: relocating lessons, adding dynamic/agent machinery to the beginner path, runtime redesign.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Beginner delivery scope defined; no implementation started.

## Dependencies / Related Work
Read UX_and_AIX_experiences/AGENTS.md and 01_beginner/_concept_map.txt. S4 inherits this vocabulary.

## Tasks (Implementation Checklist)
- [ ] [Implement Beginner chapters and all 41 lesson presentations](../tasks/2026-09-04_rtd_beginner_content_task.md)
- [ ] Map every Beginner chapter to lesson IDs and public API references.
- [ ] Author the guide sequence and all lesson explanations from actual source.
- [ ] Verify first run, lifetimes, errors, cleanup, and capstone against the target revision.
- [ ] Review the complete learning route and unrestricted contents/topic access.

## Acceptance Criteria
- [ ] Every blueprint Beginner chapter is complete and all 41 lessons are accounted for.
- [ ] A new reader can install, run Hello Melder, and finish the capstone from the documented commands.
- [ ] Addressing, spellframes, scopes, and ownership are distinguished clearly.
- [ ] Disposal descriptions match the settled implementation and current examples.
- [ ] Each chapter links relevant lessons/API; full contents reaches every page directly.
- [ ] Execution results and any exceptions are recorded without inferred verification claims.

## Validation / Test Plan
Not run. Use the existing Beginner example harness and applicable contract probes on 3.14t; inspect
asserted outcomes as well as execution success. Check HTML, links, copying, and mobile readability.

## UX / API / Data Notes
Entry is plain Python. Completion means a useful owned application graph, not familiarity with internals.

## Risks / Mitigations
Disposal work is owned separately by codex_1; read its settled source before updating affected lessons.
Old concept-map statements are intent/history and require source verification for current behavior.

## Open Questions
Per-lesson drift is resolved during scoped authoring tasks; do not silently change the curriculum tier.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Beginner curriculum and all saved beginner lessons
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S3 owns the complete Beginner level and its 41 lessons, preserving the README's public,
    static, low-floor teaching path and giving it independent contents and completion criteria.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:70-93
  - README.md:229-260
  - UX_and_AIX_experiences/01_beginner/_concept_map.txt:1-54
  IMPACT: The first level remains complete without dependency on later learning levels.
  NEXT: Map Beginner chapters to lessons after the shared catalog is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No advanced prerequisites or hand-copied example code.
- [ ] No stale disposal claims or invented execution evidence.

## Closure Confirmation
- [ ] Owner accepts the learning route and all task/board state is synchronized.

## Noting Behavior
Record chapter coverage, verified contracts, example drift, and vocabulary handed to Intermediate.

## Context / Handoff Summary
Defined, not implemented. Deliver the entire Beginner level, with source-backed examples and a real capstone.
