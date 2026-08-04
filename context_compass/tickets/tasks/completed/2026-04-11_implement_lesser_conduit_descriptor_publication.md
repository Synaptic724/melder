# Task: Implement Lesser Conduit Descriptor Publication
- Completed: 2026-04-13T11:34:18Z
- Summary: Closed the lesser-conduit descriptor publication slice after later topology/runtime work treated lesser publication as settled foundation.

## Metadata
- Task ID: TASK-2026-04-11-implement-lesser-conduit-descriptor-publication
- Story: STORY-2026-04-11-enable-lesser-conduit-descriptor-publication
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T12:20:21Z
- Updated: 2026-04-13T11:34:18Z

## Objective
Publish lesser conduits into the Nexus descriptor using the existing
`ConduitRecord` model, remove them on lesser cleanup, and preserve same-id
overwrite behavior on lesser -> normal upgrade.

## Ticket Contract
- ENTRY_GATE: the user approved the lesser-conduit publication slice and the
  patch docs exist for the system-impacting behavior change.
- EXECUTION_BOUNDARY: conduit publication/removal/upgrade paths, descriptor
  manager eligibility gate, focused tests, and ticket sync only.
- DEPENDENCIES:
  - tickets/stories/2026-04-11_enable_lesser_conduit_descriptor_publication_story.md
  - system_docs/patches/active/lesser_conduit_descriptor_publication/architecture_patch.md
  - system_docs/patches/active/lesser_conduit_descriptor_publication/component_patch_conduit.md
  - system_docs/patches/active/lesser_conduit_descriptor_publication/component_patch_frame_descriptor_manager.md
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: lesser conduits publish into the descriptor, lesser cleanup removes
  their records, upgrade re-publishes with the same `conduit_id`, and the
  focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if useful lesser publication
  requires `parent_conduit_id` or frame-summary changes in the same cut.

## Scope Boundaries
- In scope:
  - lesser publish gating
  - lesser removal gating
  - lesser create path publication
  - upgrade overwrite semantics
  - focused tests
- Out of scope:
  - new record family
  - frame summary redesign
  - spellspace publication
  - parent lineage fields

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved the lesser conduit
  descriptor publication implementation slice.

## Steps / Checklist
- [ ] Inspect current lesser create, cleanup, and upgrade publication seams.
- [ ] Patch the conduit publish/remove gating and lesser create path.
- [ ] Patch descriptor-manager publish eligibility if needed.
- [ ] Add/update focused tests.
- [ ] Record findings, implementation, and validation in `## Notes`.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_descriptor_manager.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/lesser_conduit_descriptor_publication/architecture_patch.md
  - system_docs/patches/active/lesser_conduit_descriptor_publication/component_patch_conduit.md
  - system_docs/patches/active/lesser_conduit_descriptor_publication/component_patch_frame_descriptor_manager.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the publication model is merged or intentionally retired.

## Notes
- DATETIME: 2026-04-11T12:29:06Z
  TYPE: FACT
  CLAIM: The lesser-conduit publication payload now carries lineage context.
    `ConduitDescriptorPayload` exposes `parent_conduit_id` and
    `lineage_depth`, the descriptor manager computes those values from the
    conduit ward lineage state, and the payload protocol now reflects both
    fields.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:9-112
  - src/melder/aether/nexus/frame_descriptor_manager.py:353-420
  - src/melder/utilities/interfaces/interfaces.py:2271-2285
  IMPACT: Lesser conduits are now descriptor-visible with enough lineage
    context for richer topology/navigation work without introducing a second
    conduit record family.
  NEXT: rerun the focused descriptor/publication test slice and confirm the
    lineage-field expansion stays green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T12:29:06Z
  TYPE: MEASURE
  CLAIM: The lineage-field expansion is green. Descriptor-manager publication,
    descriptor payload consumers, and the lesser publication lifecycle tests all
    pass together after adding `parent_conduit_id` and `lineage_depth`.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_descriptor_manager.py:276-306
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:477-505
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:631-666
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:319-438
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_descriptor_manager.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/conduit/test_conduit_lifecycle.py tests/unit/melder/aether/conduit/test_conduit_dynamic.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py` -> 133 passed
  IMPACT: The lesser-conduit descriptor surface is now materially richer and is
    ready for review. The next decision is whether to keep expanding topology
    or return to RiftSpace command tools.
  NEXT: review the lesser-publication lineage-field cut and choose the next
    runtime slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T12:24:36Z
  TYPE: DECISION
  CLAIM: The first lineage-field expansion should add
    `parent_conduit_id` and `lineage_depth` to the published conduit payload.
    That is enough to make lesser-conduit topology navigable without inventing
    a new record type or redesigning frame summaries.
  EVIDENCE:
  - user_instruction: "lineage fields are fine add them in we already agreed on that"
  - src/melder\aether\nexus\frame_descriptor\conduit_record.py:11-92
  - src/melder\aether\conduit\conduit_ward\conduit_ward.py:116-126
  IMPACT: The payload can stay in the existing `ConduitRecord` family while
    still exposing parent/depth information needed for richer Rift topology.
  NEXT: patch `ConduitDescriptorPayload`, update descriptor-manager payload
    construction, and extend focused descriptor/publication tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T12:24:36Z
  TYPE: FACT
  CLAIM: The lesser-conduit publication slice is now landed in source. Lesser
    conduits publish through the existing conduit-record model, lesser cleanup
    removes the record before local teardown, and descriptor-manager conduit
    publication now accepts both lesser and normal conduit states. Lesser
    creation publishes the new child at the end of the lineage-linking flow,
    and lesser->normal upgrade keeps the same overwrite-by-`conduit_id`
    behavior because upgrade already republishes after state flips to normal.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:279-334
  - src/melder/aether/conduit/conduit.py:414-483
  - src/melder/aether/conduit/conduit.py:1421-1514
  - src/melder/aether/nexus/frame_descriptor_manager.py:307-371
  IMPACT: Rift-facing topology can now see lesser conduits through descriptor
    truth without redesigning frame-level summary publication.
  NEXT: run the focused lesser-publication pytest slice and confirm the
    lifecycle/upgrade/descriptor-manager behavior stays green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T12:24:36Z
  TYPE: MEASURE
  CLAIM: The focused lesser-publication slice is green. The updated conduit
    lifecycle tests, the lesser-creation publication test, and the direct
    descriptor-manager lesser acceptance test all pass together.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:631-666
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:319-438
  - tests/unit/melder/aether/test_frame_descriptor_manager.py:249-301
  - validation_result: `python -m pytest -q tests/unit/melder/aether/conduit/test_conduit_lifecycle.py tests/unit/melder/aether/conduit/test_conduit_dynamic.py tests/unit/melder/aether/test_frame_descriptor_manager.py` -> 86 passed
  IMPACT: The first lesser-conduit descriptor publication cut is ready for
    review. The next decision is whether we stay on topology and add lineage
    fields like `parent_conduit_id`, or go back to RiftSpace command tools.
  NEXT: review the lesser publication cut and choose the next runtime slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T12:20:21Z
  TYPE: PLAN
  CLAIM: The minimal coherent first cut is to publish lesser conduits through
    the same `ConduitRecord` family, remove them on lesser cleanup, and let
    lesser->normal upgrade overwrite the same record because upgrade preserves
    `conduit_id`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1295-1383
  - src/melder/aether/nexus/frame_descriptor_manager.py:307-371
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:11-92
  IMPACT: We can get descriptor-visible lesser topology without inventing a new
    record family or changing frame summary behavior.
  NEXT: inspect the exact lesser create/cleanup call sites and patch the publish/remove gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T12:20:21Z
  TYPE: FACT
  CLAIM: The minimal implementation seam is confirmed. Lesser creation currently
    never publishes, lesser cleanup never removes a descriptor record, and the
    descriptor manager still rejects non-normal conduits. Upgrade already
    republishes after the state flips to normal and keeps the same `conduit_id`,
    so upgrade overwrite semantics already fit the existing `upsert_conduit_record(...)`
    model.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:296-334
  - src/melder/aether/conduit/conduit.py:1413-1498
  - src/melder/aether/conduit/conduit.py:413-483
  - src/melder/aether/conduit/conduit.py:1295-1383
  - src/melder/aether/nexus/frame_descriptor_manager.py:307-371
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:631-640
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:319-358
  IMPACT: The first cut can stay narrow:
    1) publish lesser conduits at the end of `create_lesser_conduit(...)`
    2) remove their records at the start of `_cleanup_lesser_conduit()`
    3) relax descriptor-manager eligibility from normal-only to published-state-only
    4) leave frame summary publication coarse
  NEXT: patch the conduit publish/remove gates and the lesser create path, then
    update the focused conduit lifecycle/dynamic tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the first lesser-conduit descriptor publication cut only.
