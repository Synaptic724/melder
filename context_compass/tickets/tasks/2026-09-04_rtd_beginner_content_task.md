# Task: Implement Beginner chapters and all 41 lesson presentations

## Metadata
- Task ID: TASK-2026-09-04-rtd-beginner-content
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-beginner-curriculum
- Story Path: ../stories/2026-09-04_rtd_beginner_curriculum_story.md
- Status: in_progress
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T22:07:46Z

## Objective
Deliver the complete Beginner learning path, public vocabulary, current cleanup explanation, capstone, and every saved Beginner lesson.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/beginner/, Beginner lesson editorial metadata/wrappers, related reference links, and evidence-backed documentation/example corrections in 01_beginner only.
- DEPENDENCIES: S1/S2; settled disposal source contract from codex_1's lane.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Implementation task defined; prerequisite work remains ahead of activation.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] Every blueprint Beginner chapter and all 41 lessons are accounted for.
- [ ] The first useful result and capstone can be followed from their stated prerequisites.
- [ ] Current address/lifetime/disposal claims are source-backed.
- [ ] Code matches canonical source and all navigation links resolve.
- [ ] Applicable existing example/probe checks run or concrete blockers are recorded.

## Validation
- Not run. Implementation task just created.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false until this task produces or owns a supporting artifact.
- ARTIFACT_PATHS: none; the parent story links the shared blueprint.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement Beginner chapters and all 41 lesson presentations
- IF_UNKNOWN: none

## Noting Behavior
- Finish a coherent read/work unit and append evidence, impact, and one next action.
- Keep notes append-only; label unverified claims explicitly.

## Notes
- DATETIME: 2026-09-04T22:07:46Z
  TYPE: PLAN
  CLAIM: Implement this bounded part of the accepted documentation program under its existing story.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - Owner implementation instruction on 2026-09-04.
  IMPACT: The complete program now has explicit execution tasks and dependency boundaries.
  NEXT: Activate this task when its dependency milestone is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

- DATETIME: 2026-09-04T23:31:19Z
  TYPE: FACT
  CLAIM: Added twelve Beginner chapters, explicit README-section selection, authored setup/registration/
    error/capstone guidance, and exact links into the existing lesson catalog. The strict site build
    passes at 158 pages. Read both test-document indexes and their verified bootstrap/isolation slices,
    plus the complete example conftest and Beginner harness. The actual fixture resets MutationResearch,
    Crystallizer, Nexus, and Aether and rebinds Spellbook/Conduit before and after each test.
  EVIDENCE:
  - docs/curriculum.toml
  - docs/tools/curriculum.py
  - UX_and_AIX_experiences/pytest_examples/conftest.py:39-74
  - UX_and_AIX_experiences/pytest_examples/test_beginner_examples.py:1-36
  - system_docs/tests_architecture.md:238-275
  - system_docs/tests_components.md:171-213
  - system_docs/tests_components.md:835-842
  IMPACT: The chapter sources and existing verification setup are understood. A separate free-threaded
    environment now has editable Melder 0.2.3, pytest 9.1.1, and the project test group installed.
  NEXT: Run the Beginner examples and the corpus metadata contract with a contained working directory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Defined task awaiting its dependency milestone.
Deliver the complete Beginner learning path, public vocabulary, current cleanup explanation, capstone, and every saved Beginner lesson.
