# Task: Rewire ACL Validation To Record Contract And Payload Type
- Completed: 2026-04-09T21:59:36Z
- Summary: This implementation slice was absorbed by the landed record-level Nexus contract migration.


## Metadata
- Task ID: TASK-2026-04-06-rewire-acl-validation-to-record-contract-and-payload-type
- Story: STORY-2026-04-06-split-nexus-record-contract-from-payload-detail
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T19:39:52Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Move ACL-side matching to the record/event Nexus contract and reduce spell
payload detail matching to spell payload-owned `payload_type`.

## Scope
- ACL view profile/config contract fields
- ACL validator
- spell payload detail field change
- focused tests

## Validation
- Not run.

## Context / Handoff Summary
This is the second implementation slice after the record/event contract exists.
It rewires validation so ACLs stop treating payload labels as dataset identity.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

