# Task: Implement Advanced isolation and inspection chapters and all 19 lessons

## Metadata
- Task ID: TASK-2026-09-04-rtd-advanced-content
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-advanced-curriculum
- Story Path: ../stories/2026-09-04_rtd_advanced_curriculum_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T22:07:46Z

## Objective
Deliver isolated-world, configuration, override, cluster, viewer/room, policy, and continuity-entry guidance with every Advanced example.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/advanced/, Advanced lesson presentations, relevant diagrams/reference links, and source-backed lesson corrections.
- DEPENDENCIES: S1/S2 and agreed Intermediate concepts.
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
- [ ] All required chapters and 19 examples are represented.
- [ ] Frame/scope meanings, setup, authority, and lifecycle are explicit.
- [ ] Drawings and long examples remain readable and directly accessible.
- [ ] Current source supports public API and configuration statements.
- [ ] Applicable example/probe and navigation checks have recorded outcomes.

## Validation
- Advanced scripts and shared corpus metadata: 286 passed (19 scripts plus 267 metadata checks).
- Documentation unit tests: 20 passed. Integrated HTML/reference checks remain.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/rtd_validation_20260904/advanced.xml
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement Advanced isolation and inspection chapters and all 19 lessons
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

- DATETIME: 2026-09-04T23:53:00Z
  TYPE: FACT
  CLAIM: Advanced lesson 02 differentiates binding names across worlds and asserts process-wide
    refusal for identical binding IDs, contradicting README's zero-collision claim. Use that canonical
    lesson for the correction. Logger lesson 04 performs attachment/detachment without checking its
    documented public logger property; add public identity/null assertions plus handler cleanup.
    Viewer lessons distinguish host-scoped reads, required frame names, and withheld-section probes;
    checkpoint lessons distinguish created records, local sealing, remote delivery, and replay.
  EVIDENCE:
  - UX_and_AIX_experiences/03_advanced/02_frames_as_worlds.py:52-110
  - src/melder/aether/aether.py:533-666
  - UX_and_AIX_experiences/03_advanced/13_the_frame_viewer_facade.py:69-173
  - UX_and_AIX_experiences/03_advanced/18_loading_it_back.py:66-163
  IMPACT: Guide prose must preserve these boundaries and not inherit stale README or lesson history.
  NEXT: Add Advanced chapters, correct the README identity paragraph, and verify all 19 lessons.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T23:55:00Z
  TYPE: FACT
  CLAIM: Twelve Advanced chapter mappings and ten authored guides now cover the defined topics,
    with cross-level links preserving cluster/targeting lesson placement. Corrected the README's
    cross-frame identity claim from the canonical example. Logging lesson now checks public
    attachment/null state and releases its handler; no Melder runtime code changed.
  EVIDENCE:
  - docs/curriculum.toml:211-313
  - README.md:608-620
  - UX_and_AIX_experiences/03_advanced/04_utility_system_logger.py:26-75
  IMPACT: New cross-level destinations can now resolve as Expert content is added.
  NEXT: Run Advanced examples and the shared documentation tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:55:00Z
  TYPE: MEASURE
  CLAIM: All 19 Advanced scripts and all 267 shared corpus metadata checks pass on Python 3.14t.
    The documentation unit suite also passes all 20 checks. Earlier metadata failures are resolved
    by the source-backed cluster and logger assertions; no source lesson was excluded.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/advanced.xml:1-1
  - docs/tests/test_curriculum.py:1-51
  IMPACT: Advanced content is ready for integrated site/reference review; proceed to Expert authoring.
  NEXT: Read Expert lessons and map their operational chapters.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [x] No silently omitted content or invented validation.
- [x] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Twelve Advanced chapters and all 19 saved lessons are implemented. All scripts and corpus metadata
checks pass. The README now distinguishes frame isolation from process-wide binding identity.
Integrated HTML, API links, and browser checks remain in the reference/quality work.
