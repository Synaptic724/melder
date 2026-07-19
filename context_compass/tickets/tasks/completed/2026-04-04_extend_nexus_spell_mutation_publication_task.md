# Task: Extend Nexus Spell Mutation Publication
- Completed: 2026-04-09T21:59:36Z
- Summary: Retired the provisional mutation continuity child with the frameinfolink lane so future mutation work can reopen under a cleaner contract-specific path.


## Metadata
- Task ID: TASK-2026-04-04-extend-nexus-spell-mutation-publication
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-04T09:19:22Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Extend the passive Nexus ingest slice so spell version changes, spell removal,
and conduit ownership transfer keep the canonical `SpellRecord` state current
instead of only handling bind/conjure publication.

## Ticket Contract
- ENTRY_GATE: the first passive Nexus ingest tranche is landed and the next
  highest-value continuity gap is spell mutation ownership/version/removal
  handling.
- EXECUTION_BOUNDARY: extend the existing passive-ingest runtime paths for
  spell version/removal/ownership changes only.
- DEPENDENCIES:
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md
  - src/melder/spellbook/spellbook.py
  - src/melder/spellbook/bind/spell_index.py
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py
  - src/melder/spellbook/spell.py
- EXIT_GATE: canonical `SpellRecord` state stays correct across version-id
  changes, removal/unregister paths, and ownership transfer paths.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the runtime semantics of
  `spell_id` versus lineage/current-version identity are too ambiguous to patch
  safely in this slice.

## Scope Boundaries
- In scope:
  - `Spellbook._update_owned_spell_id(...)`
  - `Spellbook._unregister_owned_spell_id(...)`
  - ownership transfer publication hooks
  - focused tests for spell mutation continuity
- Out of scope:
  - broader viewer integration
  - contract/borrower publication
  - full mutation research promotion logic

## State Transition Event
- from_state: review
- to_state: blocked
- transition_reason: the mutation continuity patch is mechanically landed but
  semantically provisional, because the real mutation contract likely promotes
  a new Spell object under a stable lineage instead of mutating one Spell
  object's identity in place.

## Steps / Checklist
- [x] Validate the runtime meaning of `spell_id` versus lineage/current version.
- [x] Extend version-update publication in Spellbook/SpellIndex paths.
- [x] Extend removal publication in Spellbook unregister paths.
- [x] Extend ownership-transfer publication in TransferOfOwnership.
- [x] Add focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- spell mutation publication updates
- focused tests

## Files / Paths Impacted
- src/melder/spellbook/
- src/melder/aether/conduit/conduit_ward/transfer/
- tests/unit/melder/spellbook/
- tests/unit/melder/aether/
- codex/context_compass/tickets/tasks/2026-04-04_extend_nexus_spell_mutation_publication_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/spellbook/bind/spell_index.py src/melder/spellbook/spellbook.py src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py tests/unit/melder/spellbook/bind/test_spell_index.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
  - `python -m pytest -q tests/unit/melder/spellbook/bind/test_spell_index.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the runtime meaning of `spell_id` and current-version identity is
  muddier than the first passive-ingest slice assumed.
  Rollback: stop at lineage-only updates and document the unresolved contract
  explicitly instead of faking certainty.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_spellbook.md
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/code_description_patch_nexus.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-04T10:20:00Z
  TYPE: CONFLICT
  CLAIM: The current mutation-continuity implementation likely overreached on
    spell identity semantics. We previously forced the contract
    `spell_index.current == spell.spell_id` and wired `SpellIndex.update(...)`
    plus Nexus publication around that assumption. The user now clarified a
    different intended direction for real mutation work: mutation may require a
    separate new `Spell` object with its own SHA256-backed physical
    representation, while `SpellIndex.current` advances to point at that newly
    registered spell rather than mutating the existing spell object's
    `spell_id` in place. The currently-commented `spell.spell_id = new_id`
    rewrite in `SpellIndex.update(...)` is therefore likely semantically wrong
    even if it was mechanically consistent with the previous assumption.
  EVIDENCE:
  - src/melder/spellbook/bind/spell_index.py:111-139
  - src/melder/spellbook/spell.py:101-118
  - src/melder/spellbook/spell.py:233-236
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_extra.py:717-780
  - user_instruction: "mutations will require seperate spell objects not the same spell object modifying its spell id to the index current"
  IMPACT: The mutation-publication slice should not be treated as semantically
    settled. The safe immediate posture is to stop asserting that an existing
    `Spell` object's `spell_id` must track `SpellIndex.current` and to treat
    the current Nexus mutation continuity work as provisional until the real
    mutation object-registration contract is designed.
  NEXT: inspect the remaining runtime/test assumptions that still depend on the
    forced `spell_index.current == spell.spell_id` contract, then recommend the
    narrowest safe rollback or redesign path before further mutation work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T10:53:00Z
  TYPE: FACT
  CLAIM: The mutation contract warning is now preserved directly in runtime
    code, not just in tickets. `mutation_research.py` now carries a top-level
    TODO block stating the intended direction: `SpellIndex.id` stays lineage,
    `SpellIndex.current` should point at the active concrete version, and
    `Spell.spell_id` should remain the physical identity of one specific Spell
    object. The note explicitly warns against treating mutation as in-place
    `spell_id` rewriting on an existing Spell object and points future work
    toward new-Spell registration plus explicit promotion/swap semantics.
  EVIDENCE:
  - src/melder/spellbook/mutations/mutation_research.py:9-26
  IMPACT: Future mutation work now has a visible code-level warning at the
    runtime entrypoint most likely to own the eventual promotion contract,
    which reduces the chance of the provisional current behavior getting
    normalized by drift.
  NEXT: leave the mutation task blocked until the actual promotion transaction
    model is designed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T09:19:22Z
  TYPE: PLAN
  CLAIM: The next highest-value continuity gap after the first passive-ingest
    slice is spell mutation continuity. The current store handles frame/root
    conduit publication plus spell publication at bind/conjure time, but it
    does not yet explicitly track later spell-id/version changes,
    unregister/removal paths, or conduit ownership transfer. The clean runtime
    hooks for that work appear to be `Spellbook._update_owned_spell_id(...)`,
    `Spellbook._unregister_owned_spell_id(...)`, and
    `TransferOfOwnership._flip_registry_and_spellbooks(...)`.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:539-655
  - src/melder/spellbook/bind/spell_index.py:111-205
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:930-987
  IMPACT: This is the next clean implementation slice if we want Nexus spell
    records to stay correct beyond initial bind/conjure publication.
  NEXT: validate the `spell_id`/lineage/current-version contract before
    patching these hooks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T09:27:00Z
  TYPE: FACT
  CLAIM: The current code does not make `SpellIndex.id` and `spell_id` the same
    thing. `SpellIndex.id` is an immutable ULID lineage identity, while
    `SpellIndex.current` is the mutable current version id. At spell creation
    time, `Spell.spell_id` is initialized from the bind-time fingerprint and
    starts equal to `SpellIndex.current`, but the existing `SpellIndex.update(...)`
    and `Spellbook._update_owned_spell_id(...)` paths only rewrite the
    Spellbook's spell-id lookup maps; they do not appear to rewrite the
    `Spell.spell_id` field itself. So right now the code only guarantees
    `spell_index.current == spell_id` at initial bind, not necessarily after
    later version updates.
  EVIDENCE:
  - src/melder/spellbook/bind/spell_index.py:14-22
  - src/melder/spellbook/bind/spell_index.py:61-66
  - src/melder/spellbook/spell.py:233-236
  - src/melder/spellbook/spellbook.py:498-505
  - src/melder/spellbook/spellbook.py:539-600
  IMPACT: The follow-up publication slice cannot safely assume that the runtime
    still treats `spell.spell_id` as the current version id after a lineage
    update. If the intended contract is `spell_index.current == spell_id`, we
    should enforce that explicitly first, because it would simplify the Nexus
    spell-record key/update model.
  NEXT: ask the user to confirm whether the intended contract should be
    `spell_index.current == spell.spell_id` at all times, then implement the
    version/removal/ownership publication slice against that clarified rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T09:35:30Z
  TYPE: DECISION
  CLAIM: The intended runtime contract is now explicit: `SpellIndex.id` stays
    the stable lineage id, while `SpellIndex.current` and `spell.spell_id`
    should always refer to the same active version id. That means version
    updates must rewrite `spell.spell_id` in lockstep with
    `spell_index.current`, and Nexus spell-record updates can safely treat
    `spell.spell_id` as the current-version key while keeping `lineage_id` as
    the stable lineage identity.
  EVIDENCE:
  - user_instruction: "spell_index.current = spell_id"
  - src/melder/spellbook/bind/spell_index.py:14-22
  - src/melder/spellbook/spell.py:233-236
  IMPACT: The mutation-publication slice can now patch version, remove, and
    ownership-transfer paths against one clear identity rule instead of
    preserving the current drift.
  NEXT: patch `SpellIndex.update(...)`, then wire Nexus updates into the owned
    version/remove hooks and ownership-transfer path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T09:50:19Z
  TYPE: FACT
  CLAIM: The mutation continuity slice is now implemented. `SpellIndex.update(...)`
    rewrites attached spell objects so `spell.spell_id` stays aligned with
    `spell_index.current`; `Spellbook._update_owned_spell_id(...)` now replaces
    the canonical Nexus spell record when the active version changes;
    `Spellbook._unregister_owned_spell_id(...)` now removes the canonical spell
    record on owned-spell removal; and
    `TransferOfOwnership._flip_registry_and_spellbooks(...)` now republishes the
    transferred spell into Nexus after ownership is restamped. Focused version,
    Spellbook, ownership-transfer, passive-ingest, and Nexus unit surfaces all
    passed after the change.
  EVIDENCE:
  - src/melder/spellbook/bind/spell_index.py:111-139
  - src/melder/spellbook/spellbook.py:539-659
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:930-987
  - tests/unit/melder/spellbook/bind/test_spell_index.py:56-91
  - tests/unit/melder/spellbook/test_spellbook.py:3473-3557
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:2747-2794
  - command:python -m pytest -q tests/unit/melder/spellbook/bind/test_spell_index.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/test_nexus.py
  IMPACT: Nexus canonical `SpellRecord` state now stays correct not only at
    initial bind/conjure time, but also across active-version changes, owned
    spell removal, and conduit ownership transfer.
  NEXT: review the mutation continuity slice with the user and decide whether
    the next expansion should add contracted-spell publication, viewer
    consumption, or store refactoring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task extends the passive Nexus ingest slice to cover spell version/removal
and ownership-change continuity after the first bind/conjure publication path,
but it is now explicitly blocked pending the real mutation object-promotion
contract.

