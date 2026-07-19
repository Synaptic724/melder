# Story: Implement View And Command ACL Fluent Builders
- Completed: 2026-04-25T20:01:52Z
- Summary: Closed after the follow-on view/command builder slice landed and
  validated green, extending the fluent authoring pattern beyond codegen.

## Metadata
- Story ID: STORY-2026-04-25-implement-view-and-command-acl-fluent-builders
- Epic: EPIC-2026-04-25-implement-view-and-command-acl-fluent-builders
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T19:44:00Z
- Updated: 2026-04-25T20:01:52Z

## User Narrative
As an engineer, I want fluent ACL builders for `view` and `command` too, so all
major ACL families can be authored through readable builder surfaces instead of
direct ruleset surgery.

## Ticket Contract
- ENTRY_GATE: the codegen family builder is already the reference pattern.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/acl/builder/`
  - directly affected tests
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_implement_view_and_command_acl_fluent_builders_task.md`
- EXIT_GATE: view and command fluent builders exist, are reachable through the
  generic builder, and have focused tests.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the live family vocabularies
  do not fit bounded builder helpers cleanly.

## Acceptance Criteria
- `FrameACLViewBuilder` lands.
- `FrameACLCommandBuilder` lands.
- The builders reflect the actual family rule vocabularies.
- Focused tests are green.

## Notes
- DATETIME: 2026-04-25T19:44:00Z
  TYPE: PLAN
  CLAIM: The story should mirror the codegen slice closely, but the helper
    methods need to match the live family vocabularies:
    payload/member visibility for `view`, and frame/conduit/spell enablement
    plus member operation controls for `command`.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/view/safe_profile.py:1-58
  - src/melder/aether/nexus/acl/configurations/profiles/command/safe_profile.py:1-38
  IMPACT: The new builders should be specific, not generic placeholders.
  NEXT: implement the task with family-shaped helper methods and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:53:10Z
  TYPE: FACT
  CLAIM: The story is now implemented and green. The new builders are not just
    copies of the codegen surface; they follow the live family vocabularies:
    view uses visibility/payload/member helpers, and command uses enablement
    and member-operation helpers with selector-shaped member overrides.
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-390
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-329
  - tests/unit/melder/aether/test_frame_acl_view_builder.py:1-112
  - tests/unit/melder/aether/test_frame_acl_command_builder.py:1-104
  IMPACT: The fluent-builder program now covers the three major ACL families.
  NEXT: return the story for review and decide whether the program stops here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
