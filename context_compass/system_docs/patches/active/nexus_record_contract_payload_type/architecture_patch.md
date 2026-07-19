# Patch Architecture: Nexus Record Contract Payload Type

## Metadata
- Patch ID: `nexus_record_contract_payload_type`
- Status: active
- Updated: 2026-04-06T19:50:41Z

## Objective
Move deterministic Nexus dataset identity to the published record/event layer
and keep spell detail variation inside the spell payload body.

## Core Decision
- `FrameRecord`, `ConduitRecord`, and `SpellRecord` carry:
  - `nexus_label`
  - `nexus_version`
- The default published dataset is:
  - `default`
  - `0.0.1`
- Spell payloads no longer use spell-examiner profile identity as dataset
  identity.
- Spell payload detail is represented by:
  - `payload_type`
  - optional source profile provenance
- ACL validation and viewer binding validate against the record-level Nexus
  contract instead of payload labels.

## Non-Goals
- a second dataset label/version
- codegen execution changes
- mutation work
