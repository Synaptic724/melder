# Task: Investigate Record-Level Nexus Label And Payload Type Split
- Completed: 2026-04-09T21:59:36Z
- Summary: Captured the record-level Nexus contract split and handed the lane off to implementation.


## Metadata
- Task ID: TASK-2026-04-06-investigate-record-level-nexus-label-and-payload-type-split
- Story: STORY-2026-04-06-split-nexus-record-contract-from-payload-detail
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T19:39:52Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Map the exact code and contract consequences of moving the Nexus publication
contract to record/event objects and reducing spell payload detail to a
payload-owned `payload_type`.

## Ticket Contract
- ENTRY_GATE: the frame-bound viewer-profile slice is green and the next user
  direction is publication-contract cleanup, not viewer-method expansion.
- EXECUTION_BOUNDARY: investigation, ticketing, and phased plan only.
- DEPENDENCIES:
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/frame_descriptor/frame_record.py
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py
  - src/melder/aether/nexus/frame_descriptor/spell_record.py
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
- EXIT_GATE: findings are recorded with evidence and the phased implementation
  plan is explicit enough to start with user approval.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the contract must live on a
  different envelope object than `FrameRecord` / `ConduitRecord` /
  `SpellRecord`.

## Scope Boundaries
- In scope:
  - record/event contract location
  - payload/detail separation
  - validator and publish-path consequences
  - phased implementation planning
- Out of scope:
  - code edits
  - dataset migration shims
  - viewer/codegen behavior changes

## Validation
- Not run.

## Notes
- DATETIME: 2026-04-06T19:39:52Z
  TYPE: FACT
  CLAIM: The current base descriptor-payload interface defines the publication
    contract in the wrong place. `IDescriptorPayload` requires
    `profile_name/profile_version`, so the record layer currently has no
    independent publication identity at all.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2223-2233
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:26-56
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:26-56
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:28-80
  IMPACT: We cannot publish deterministic Nexus datasets independently from
    payload detail until record/event objects grow their own contract fields.
  NEXT: confirm how the publish manager and ACL validator currently consume the
    payload-side contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T19:39:52Z
  TYPE: FACT
  CLAIM: Descriptor publication and ACL validation both currently enforce the
    contract through payload fields. `FrameDescriptorManager` validates
    published frame/conduit/spell payloads directly, and `FrameACLValidator`
    reads payload-side labels from `frame_overview.payload`,
    `conduit_record.payload`, and `spell_record.payload`.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:274-291
  - src/melder/aether/nexus/frame_descriptor_manager.py:340-352
  - src/melder/aether/nexus/frame_descriptor_manager.py:427-448
  - src/melder/aether/nexus/frame_descriptor_manager.py:790-865
  - src/melder/aether/nexus/acl/frame_acl_validator.py:360-739
  IMPACT: The migration has to touch both descriptor ingest and ACL validation,
    not just record interfaces.
  NEXT: confirm the exact spell-side leak where spell-examiner profile identity
    becomes the published spell payload contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T19:39:52Z
  TYPE: FACT
  CLAIM: The spell payload contract is currently coupled to spell-examiner
    detail profiles. `SpellGeneralProfile` and `SpellDetailedProfile` publish
    `general` and `detailed` directly into `SpellDescriptorPayload`, which is
    why spell payload publication is currently pretending to be the dataset
    contract.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:72-73
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:151-156
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:105-106
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:235-242
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:80-231
  IMPACT: Spell publication needs a new separation:
    record/event contract at the record level and `payload_type` inside the
    spell payload.
  NEXT: write the phased implementation plan and stop before editing code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T19:41:58Z
  TYPE: PLAN
  CLAIM: The clean implementation order is three steps. First, add
    `nexus_label` / `nexus_version` to the record interfaces and record classes
    and publish all current records as `default:0.0.1`. Second, strip dataset
    identity out of payload classes and make spell payload detail explicit as
    `payload_type` plus optional source-provenance metadata. Third, rewire
    `FrameDescriptorManager` and `FrameACLValidator` so publication and ACL
    matching use the record-level Nexus contract while spell payload detail
    stays payload-owned.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2223-2278
  - src/melder/utilities/interfaces/interfaces.py:2293-2314
  - src/melder/utilities/interfaces/interfaces.py:2588-2613
  - src/melder/aether/nexus/frame_descriptor_manager.py:274-291
  - src/melder/aether/nexus/frame_descriptor_manager.py:340-352
  - src/melder/aether/nexus/frame_descriptor_manager.py:427-448
  - src/melder/aether/nexus/frame_descriptor_manager.py:790-865
  - src/melder/aether/nexus/acl/frame_acl_validator.py:360-739
  IMPACT: We can implement this without redoing the viewer work, but we should
    not collapse the steps together because record contract migration and ACL
    rewiring are different failure domains.
  NEXT: present the phased plan for approval before starting the first
    implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task documents the contract split before implementation starts. The main
finding is that the current system treats payload labels as publication
identity, which blocks deterministic dataset versioning.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

