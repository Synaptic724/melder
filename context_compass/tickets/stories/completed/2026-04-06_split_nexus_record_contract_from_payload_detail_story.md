# Story: Split Nexus Record Contract From Payload Detail
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the Nexus record-contract split and moved dataset identity off the payload body.


## Metadata
- Story ID: STORY-2026-04-06-split-nexus-record-contract-from-payload-detail
- Epic: EPIC-2026-04-06-nexus-record-contract-and-payload-type-alignment
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T19:39:52Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Move the deterministic Nexus publication contract to the descriptor record
objects and keep spell payload detail variation inside the spell payload body.

## Scope
- record/interface contract fields:
  - `nexus_label`
  - `nexus_version`
- spell payload detail field:
  - `payload_type`
- descriptor-manager publish validation
- ACL validation contract matching
- focused unit tests

## Out Of Scope
- new viewer behavior
- codegen behavior
- multi-dataset publication authoring beyond `default:0.0.1`

## Task Links
- TASK-2026-04-06-investigate-record-level-nexus-label-and-payload-type-split
- TASK-2026-04-06-implement-record-level-nexus-label-and-version-contract
- TASK-2026-04-06-rewire-acl-validation-to-record-contract-and-payload-type

## Validation
- Not run.

## Notes
- DATETIME: 2026-04-06T19:39:52Z
  TYPE: DECISION
  CLAIM: The publication contract and payload detail are being split at the
    story level. Record/event objects should carry `nexus_label` and
    `nexus_version`, while spell payloads should carry a separate
    `payload_type` like `general` or `detailed`.
  EVIDENCE:
  - user_instruction: "each event should have a nexus_label and a nexus_version"
  - user_instruction: "the PAYLOAD itself for spell can have a payload type describing general|detailed"
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:8-75
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:8-76
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:9-123
  IMPACT: Implementation should not rename payload labels in place. It should
    introduce a record-level publication contract and then move ACL validation
    to that contract boundary.
  NEXT: finish the investigation task and write the phased implementation plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story is the contract-cleanup lane for Nexus publication identity. It
keeps the published dataset deterministic without coupling it to spell payload
detail richness.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

