# Story: Enable Lesser Conduit Descriptor Publication
- Completed: 2026-04-13T11:34:18Z
- Summary: Completed the lesser-conduit descriptor publication story and archived it after the narrower publication slice landed.

## Metadata
- Story ID: STORY-2026-04-11-enable-lesser-conduit-descriptor-publication
- Epic: EPIC-2026-04-11-publish-lesser-conduits-into-nexus-descriptor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T12:20:21Z
- Updated: 2026-04-13T11:34:18Z

## User Narrative
As the Rift/runtime designer, I want lesser conduits to appear in descriptor
truth so that Rift-facing topology and targeting surfaces can operate from a
richer set of real execution scopes.

## Ticket Contract
- ENTRY_GATE: the new epic exists and the user explicitly approved the lesser
  conduit publication slice.
- EXECUTION_BOUNDARY: descriptor/publication behavior only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_publish_lesser_conduits_into_nexus_descriptor_epic.md
  - tickets/tasks/2026-04-11_implement_lesser_conduit_descriptor_publication.md
- EXIT_GATE: lesser conduits publish/remove/upgrade through the existing
  conduit-record model and focused tests prove the behavior.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first cut requires parent
  lineage fields or frame-summary expansion to be useful at all.

## Acceptance Criteria
- Lesser conduits can be published into the descriptor.
- Lesser cleanup removes their record.
- Upgrade to normal overwrites the same descriptor record identity.
- Focused tests are green.

## Notes
- DATETIME: 2026-04-11T12:20:21Z
  TYPE: PLAN
  CLAIM: This story is intentionally a narrow topology/publication slice. The
    descriptor does not need a new conduit record family for the first cut
    because `ConduitRecord.payload.conduit_state` already distinguishes normal
    vs lesser.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:11-92
  - user_instruction: "if we improve this and instead also publish conduit_state to show lesser or normal then we can capture everything"
  IMPACT: The first implementation can stay on the existing conduit record model
    and avoid a new descriptor family.
  NEXT: inspect the current normal-only publish/remove gates and lesser create
    paths in `Conduit`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: This story is complete. Lesser conduits are now descriptor-visible
    through the existing conduit-record model, and later runtime work already
    consumes that richer topology as settled substrate.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-11_implement_lesser_conduit_descriptor_publication.md:1-155
  - codex/context_compass/system_docs/src_components.md:824-832
  IMPACT: The story can move to the completed lane and stop occupying active
    planning state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owned the first lesser-conduit descriptor publication cut only.
That cut is now complete and archived as settled topology/publication substrate.
