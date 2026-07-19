# Epic: Nexus Record Contract And Payload Type Alignment
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the Nexus record-contract alignment epic and archived the record-level contract migration lane.


## Metadata
- Epic ID: EPIC-2026-04-06-nexus-record-contract-and-payload-type-alignment
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T19:39:52Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Separate the Nexus publication contract from payload detail so published frame,
conduit, and spell records all carry one deterministic record-level Nexus
contract while spell payload detail can vary independently.

## Problem / Opportunity
The current descriptor publication model mixes two different concerns:
- record/event dataset identity
- payload detail/provenance

That makes the contract unstable. Right now spell payload publication can look
like a different published contract purely because the spell payload was built
from a different spell-examiner detail profile.

## Goals
- Put `nexus_label` and `nexus_version` on the published record objects.
- Make the default published contract deterministic:
  - `nexus_label = "default"`
  - `nexus_version = "0.0.1"`
- Keep payload variation inside payload objects instead of the record/event
  contract.
- Make spell payload detail explicit as payload detail, not as Nexus dataset
  identity.
- Rewire descriptor ingest and ACL validation to use the record/event contract.

## Non-Goals
- viewer tool expansion
- codegen execution changes
- mutation work
- a second dataset label/version in this slice

## Story Links
- STORY-2026-04-06-split-nexus-record-contract-from-payload-detail

## Validation
- Not run.

## Notes
- DATETIME: 2026-04-06T19:39:52Z
  TYPE: FACT
  CLAIM: The current Nexus publication model stores contract identity on
    payload objects instead of record/event objects. `IDescriptorPayload`
    defines `profile_name` / `profile_version`, all three payload classes
    implement those fields directly, `FrameDescriptorManager` validates those
    payload fields at publish time, and `FrameACLValidator` validates against
    descriptor payload contract fields rather than a record-level publication
    contract.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2223-2278
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:14-111
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:15-82
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:80-231
  - src/melder/aether/nexus/frame_descriptor_manager.py:274-291
  - src/melder/aether/nexus/frame_descriptor_manager.py:340-352
  - src/melder/aether/nexus/frame_descriptor_manager.py:427-448
  - src/melder/aether/nexus/frame_descriptor_manager.py:790-865
  - src/melder/aether/nexus/acl/frame_acl_validator.py:360-739
  IMPACT: We need a contract migration that moves dataset identity to the
    record layer before later dataset labels/versions can vary sanely.
  NEXT: define the story and task sequence around record-level contract
    identity, spell payload typing, and ACL validation rewiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic exists to separate Nexus dataset identity from payload detail. The
default published dataset contract should live on the record/event objects,
while spell payload detail should vary through payload-owned fields like
`payload_type`.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

