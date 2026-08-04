# Epic: Implement View And Command ACL Fluent Builders
- Completed: 2026-04-25T20:01:52Z
- Summary: Closed after the first broader fluent-builder phase landed view and
  command family builders alongside the earlier codegen builder.

## Metadata
- Epic ID: EPIC-2026-04-25-implement-view-and-command-acl-fluent-builders
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T19:44:00Z
- Updated: 2026-04-25T20:01:52Z

## Problem / Opportunity
The first codegen ACL fluent builder is now landed and green, but the broader
ACL authoring surface is still uneven. `view` and `command` still require the
generic draft API plus direct low-level ruleset mutation, which is less readable
than the new codegen family path.

## MRP Alignment (Most Reasonable Product)
The MRP is:
- add one `FrameACLViewBuilder`
- add one `FrameACLCommandBuilder`
- wire them into `FrameACLBuilder`
- add focused tests

No broader ACL storage or compiler work should happen in this slice.

## Ticket Contract
- ENTRY_GATE: the codegen fluent-builder slice is complete enough to act as the
  implementation reference.
- EXECUTION_BOUNDARY: `view` and `command` authoring ergonomics only.
- DEPENDENCIES:
  - `src/melder/aether/nexus/acl/builder/frame_acl_builder.py`
  - `src/melder/aether/nexus/acl/configurations/frame_acl_view_configuration.py`
  - `src/melder/aether/nexus/acl/configurations/frame_acl_command_configuration.py`
- EXIT_GATE: `view` and `command` have family-specific fluent builders layered
  over the existing generic builder lifecycle and covered by focused tests.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the family vocabularies need a
  broader ACL authoring redesign instead of bounded builder additions.

## Goals (Outcomes)
- Add `FrameACLViewBuilder`.
- Add `FrameACLCommandBuilder`.
- Keep commit/discard inside `FrameACLBuilder`.
- Add readable family-specific helper methods that match the live profile
  vocabularies.

## Non-Goals (Explicit Exclusions)
- Reworking codegen builder semantics.
- Full generic metaprogrammed builder unification.
- New ACL runtime or compiler behavior.

## Acceptance Criteria (Epic Done)
- `begin_view_change(...)` exists and returns a view fluent builder.
- `begin_command_change(...)` exists and returns a command fluent builder.
- Focused tests are green.

## Notes
- DATETIME: 2026-04-25T19:44:00Z
  TYPE: DECISION
  CLAIM: The next ACL authoring slice should widen the same pattern to the
    remaining major families instead of inventing a generic builder rewrite.
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-446
  - tests/unit/melder/aether/test_frame_acl_codegen_builder.py:1-154
  IMPACT: The next implementation can stay narrow and family-shaped.
  NEXT: stage the view/command fluent-builder story and task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:53:10Z
  TYPE: MEASURE
  CLAIM: The follow-on family builders are implemented and green. With view,
    command, and codegen all covered, the first fluent-builder program phase is
    now complete enough for review.
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-446
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-390
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-329
  - tests/unit/melder/aether/test_frame_acl_codegen_builder.py:1-154
  - tests/unit/melder/aether/test_frame_acl_view_builder.py:1-112
  - tests/unit/melder/aether/test_frame_acl_command_builder.py:1-104
  IMPACT: The ACL authoring ergonomics lane can move to review as one coherent
    phase instead of staying fragmented by family.
  NEXT: review whether this is enough or whether you want a broader unified
    builder program later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
