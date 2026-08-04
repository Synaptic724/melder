# Task: Implement Conduit Meld Target Dump For ACL Authoring
- Completed: 2026-04-13T11:43:06Z
- Summary: Closed the conduit/spellbook ACL authoring dump slice after the dedicated dump lane and later AR cleanup confirmed it as settled small surface.

## Metadata
- Task ID: TASK-2026-04-11-implement-conduit-meld-target-dump-for-acl-authoring
- Story: STORY-2026-04-11-describe-spells-in-conduit-and-spellbook-authoring-dump
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-11T10:10:57Z
- Updated: 2026-04-13T11:43:06Z

## Objective
Add a Conduit-facing dump that lists meld-target details useful for static ACL
authoring, including human-readable selector fields plus exact `spell_id`.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to implement the authoring dump on
  `Conduit` and the access-mode lane already established that both logical
  selectors and exact `spell_id` should be supported.
- EXECUTION_BOUNDARY: conduit/meld-facing dump only, plus focused tests.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_describe_spells_in_conduit_epic.md
  - tickets/stories/2026-04-11_describe_spells_in_conduit_and_spellbook_authoring_dump_story.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/aether/conduit/conduit.py
  - src/melder/spellbook/spellbook.py
  - src/melder/spellbook/spell.py
  - tests/unit/melder/aether/conduit/
- EXIT_GATE: `Conduit` exposes a dump of spell target details suitable for ACL
  authoring and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the dump requires a second
  selector model instead of reusing the live spell metadata already owned by
  Spell/Spellbook/Meld.

## Scope Boundaries
- In scope:
  - user-facing ACL-authoring dump on `Conduit`
  - selector fields:
    - `spell_id`
    - `spell_name`
    - `binding_name`
    - `spellframe`
    - `existence`
    - `owner_conduit_id`
  - focused tests
- Out of scope:
  - static runtime enforcement
  - ACL registry implementation
  - viewer changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to implement the conduit-side
  authoring dump now.

## Steps / Checklist
- [ ] Inspect current `Conduit`/`Meld`/`Spell` ownership of target metadata.
- [ ] Add the conduit-facing dump method.
- [ ] Add/update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- conduit-facing meld target dump
- focused tests

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py
- src/melder/aether/conduit/meld/meld.py
- tests/unit/melder/aether/conduit/
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/conduit/test_conduit_facade.py tests/unit/melder/aether/conduit/meld/test_meld.py`

## Risks / Rollback Notes
- Risk: the dump leaks internal/debug-only fields instead of the smaller
  authoring surface the user asked for.
  Rollback: keep the surface limited to selector and ownership fields only.

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
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T10:20:45Z
  TYPE: DECISION
  CLAIM: This review task has been re-homed beneath a dedicated epic/story
    named after the public conduit API surface the user chose:
    `describe_spells_in_conduit`. The broader access-modes epic remains related
    context, but this smaller runtime slice now has its own direct lane.
  EVIDENCE:
  - user_instruction: "make an epic to implement this, and lets call it describe_spells_in_conduit"
  - tickets/epics/2026-04-11_describe_spells_in_conduit_epic.md:1-138
  - tickets/stories/2026-04-11_describe_spells_in_conduit_and_spellbook_authoring_dump_story.md:1-101
  IMPACT: Review and acceptance can now route through the dedicated dump lane
    without hiding under the larger access-modes work.
  NEXT: keep the task in review until the user accepts the payload shape or
    redirects the next static-authoring step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T10:10:57Z
  TYPE: PLAN
  CLAIM: The user-facing dump should stay small and authoring-oriented. The
    current target field set is: `spell_id`, `spell_name`, `binding_name`,
    `spellframe`, `existence`, and `owner_conduit_id`.
  EVIDENCE:
  - user_instruction: "we should support both"
  - user_instruction: "print out a JSON of meld target details and SHA256 key per spell"
  - user_instruction: "owner_conduit_id can stay too"
  IMPACT: The implementation should avoid leaking internal debug fields like
    `storage_scope_kind` into the authoring dump.
  NEXT: inspect `Conduit`, `Meld`, and `Spell` to confirm where each field
    already lives before adding the new dump surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T10:10:57Z
  TYPE: DECISION
  CLAIM: The likely owner should be `Spellbook`, with `Conduit` as the public
    façade. The selector/identity fields the user wants are spell-owned/runtime-
    registration data, and `Spellbook` already owns the local spell registries.
    `Meld` may still be useful for lookup semantics later, but it does not need
    to own this authoring dump if the data is already available from the bound
    spell state.
  EVIDENCE:
  - user_instruction: "this would be implemented in spellbook, and facaded via conduit"
  - user_instruction: "all this stuff exists in spell"
  IMPACT: The implementation should inspect `Spellbook`/`Spell` first and only
    pull `Meld` in if a selector field is not already available through owned
    spell state.
  NEXT: inspect `Spellbook` and `Spell` ownership of the target fields before
    patching the façade.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T10:10:57Z
  TYPE: FACT
  CLAIM: The target field set is already available from owned spell state. The
    clean source set is `Spellbook._spell_id_pool`, which already acts as the
    accessible spell-id map across local and contracted spell ids. Each `Spell`
    already carries the authoring fields we need:
    - `spell_id`
    - `spell_name`
    - `binding_name`
    - `spellframe`
    - `existence`
    - `owner_conduit_info`
    So this dump does not need `Meld` as the primary owner.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:195-203
  - src/melder/spellbook/spellbook.py:541-584
  - src/melder/spellbook/spellbook.py:715-772
  - src/melder/spellbook/spell.py:274-314
  - src/melder/spellbook/spell.py:372-378
  - src/melder/spellbook/spell.py:847-857
  IMPACT: The implementation can stay simple: add the owner method on
    `Spellbook`, then façade it through `Conduit`.
  NEXT: patch `Spellbook.describe_spells_in_spellbook(...)` first, then add the
    `Conduit.describe_spells_in_conduit(...)` façade and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T10:10:57Z
  TYPE: MEASURE
  CLAIM: The conduit/spellbook authoring dump is now landed and green.
    `Spellbook.describe_spells_in_spellbook(...)` now returns the requested
    small selector/ownership payload from the Spellbook-visible spell-id pool,
    and `Conduit.describe_spells_in_conduit(...)` facades it directly.
    The public protocol layer now exposes both methods.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:1293-1350
  - src/melder/aether/conduit/conduit.py:2633-2667
  - src/melder/utilities/interfaces/interfaces.py:1610-1615
  - src/melder/utilities/interfaces/interfaces.py:4535-4540
  - tests/unit/melder/spellbook/test_spellbook.py:3715-3758
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:215-256
  - validation_result: `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/test_conduit_facade.py` -> 168 passed
  IMPACT: Static/capability ACL authoring now has a conduit-facing dump that
    exposes both logical targeting fields and exact SHA256 spell ids without
    leaking the internal live-creation debug payload.
  NEXT: review the authoring dump and decide whether the next step is to plug
    it into static ACL authoring directly or expand the payload shape further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:43:06Z
  TYPE: DECISION
  CLAIM: The conduit/spellbook authoring dump slice is complete and can move
    to the completed lane. The small payload and owner/facade split are now
    settled enough that this task does not need to stay in active review state.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:1293-1350
  - src/melder/aether/conduit/conduit.py:2633-2667
  - tickets/stories/2026-04-11_describe_spells_in_conduit_and_spellbook_authoring_dump_story.md:1-97
  IMPACT: This small authoring-dump task no longer belongs on the active board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the conduit-side ACL authoring dump only.
