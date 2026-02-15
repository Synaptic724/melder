# Story: Contract, link, and ownership impact alignment for id maps

- Completed: 2026-01-25
- Summary: Audited contract/link and ownership transfer flows, confirmed contract
  id map wiring, and updated ownership transfer to move spell_id maps and
  SpellIndex owner references.

## Metadata
- Story ID: STORY-2026-01-25-contract-link-ownership-impacts
- Epic: EPIC-2026-01-25-spell-id-lookup-foundation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As the contract and ownership system, we want spell_id maps to stay consistent
through link, contract, and ownership transfer flows so resolution remains correct.

## Value / MRP Alignment
Ensures the O(1) lookup foundation remains correct across cross-conduit and
ownership flows that update spell registries.

## Requirements (Functional)
- Audit link and contract flows for spell_id map updates.
- Audit ownership transfer flows for map updates and attachment changes.
- Implement required updates in Spellbook or related components based on audit
  findings.

## Requirements (Non-Functional)
- Keep changes scoped to contract and ownership flows only.
- Preserve existing contract and transfer semantics.

## Scope Boundaries
- In scope:
  - Contract link and contracted spell update flows.
  - Ownership transfer flows that move spell stewardship.
- Out of scope:
  - Mutation pipelines.
  - New contract policy behavior.

## Dependencies / Related Work
- Story: STORY-2026-01-25-spellbook-spell-id-maps
- Story: STORY-2026-01-25-spellindex-update-propagation

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-contract-link-audit - Audit contract and link flows.
- [x] Task: TASK-2026-01-25-ownership-transfer-audit - Audit ownership transfer flow.
- [x] Task: TASK-2026-01-25-contract-update-followups - Implement required updates.

## Acceptance Criteria
- Contract and link flows are confirmed to update new id maps or are patched.
- Ownership transfer flow is confirmed to update id maps or is patched.
- Any remaining gaps are documented with follow-up tasks.

## Validation / Test Plan
- Targeted unit or component tests based on changes from audits.

## UX / API / Data Notes
- Internal-only updates; no external API changes expected.

## Risks / Mitigations
- Risk: ownership transfer updates happen outside Spellbook.
  Mitigation: audit transfer flow and add explicit update hooks if needed.

## Open Questions
- Resolved: Contract adds/removals flow through Spellbook helpers that update
  contracted spell_id maps via SpellIndex attachments.
- Resolved: Ownership transfer now moves spell_id maps and updates SpellIndex
  owner references in `transfer_of_ownership.py`.

## Decision Log
- 2026-01-25: Separate audit work from implementation to keep scope controlled.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
- Contract/link flows already use Spellbook contract helpers that update
  contracted spell_id maps; no further changes needed.
- Ownership transfer now updates owned spell_id maps and SpellIndex owner
  references; unit coverage added.
- Acceptance confirmed by user.
