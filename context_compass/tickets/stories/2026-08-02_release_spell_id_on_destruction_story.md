# Story: Release a spell_id on every destruction path

## Metadata
- Story ID: STORY-2026-08-02-release-spell-id-on-destruction
- Epic ID: EPIC-2026-08-02-process-wide-spell-id-uniqueness
- Status: ready
- Owner: cowork
- Agent Name: UNASSIGNED
- Priority: p1
- Created: 2026-08-02T20:25:00Z
- Updated: 2026-08-02T20:25:00Z

## Problem / Opportunity

THIS IS THE ONE THAT WILL BITE. Every teardown path today drops a per-frame
REFERENCE, and that is currently sufficient because the frame holds a live alias
to the Spellbook's own set - clearing your set empties the frame's view for free.

Against a SHARED process-wide set that is no longer true. `_spell_ids.clear()`
removes nothing from a unified set, so a cleaned Spellbook permanently poisons
the process namespace and rebinding the same target throws forever. The failure
is silent at cleanup and surfaces much later as "I cleaned up and now I can't
rebind" - which reads as a bind bug, not a teardown bug.

## Ticket Contract
- ENTRY_GATE: STORY-2026-08-02-aether-unified-spell-id-set landed.
- EXECUTION_BOUNDARY: teardown paths in `spellbook.py`, `aetheric_frame.py`,
  `conduit.py`, plus `Spell`/`SpellIndex` cleanup. No changes to allocation.
- DEPENDENCIES: the unified set must exist before release can target it.
- EXIT_GATE: cleanup-then-rebind of the same target succeeds, proven by test, on
  every enumerated path.
- FAILURE_ESCALATION: `BLOCKER` if any path cannot determine which ids it owns at
  teardown time.

## Goals
- Every path that destroys a spell releases its id from the authoritative set.
- Cleanup-then-rebind works. No namespace poisoning.

## Non-goals
- Signature release (`LookupContainer`). Different axis, different lifecycle.
- Notch/park paths - those DELIBERATELY keep existence and must not release.

## Requirements

R1 Enumerate and cover every destruction path. Known so far, none verified as
complete:
- `Spellbook.cleanup_and_remove_spell` -> `_unregister_owned_spell_id` (`:655`)
- `Spellbook.cleanup_spell` (`:4036`)
- `Spellbook._cleanup_components` (`:511` clear, `:514` del)
- `AethericFrame.unregister_conduit_spells` (`:1052`)
- `AethericFrame._cleanup_data_structures` (`:310`, `:333`)
- Conduit teardown -> `_unregister_conduit_spells_from_aether` (`:2511`)
- `TransferOfOwnership` - moves ids BETWEEN books; release-then-claim, not drop
- contracted/borrowed teardown - `_contracted_spell_ids`, NOT in the unified set

R2 PARK IS NOT DESTRUCTION. `_deactivate_owned_spell` states "Leaves `_spell_ids`
untouched: existence is kept across the deactivation", and `bind_inactive` "keeps
existence in `_spell_ids`". A parked spell's id stays allocated - that is the
point. Releasing on park would let a duplicate be minted for a sleeping spell,
which is the exact failure `EPIC-2026-06-14` named.

R3 Release must be idempotent - teardown is best-effort and partially-completed
teardown is an existing, documented state.

## Acceptance criteria
- Bind -> cleanup -> rebind the same target in the same process succeeds.
- Bind -> park (notch away) -> attempt duplicate bind is still REFUSED.
- Frame cleanup releases every id that frame's books owned.
- Transfer of ownership does not lose or double-hold an id.
- Owner-run suite green.

## Risks / Mitigations
- RISK: a missed path poisons the namespace permanently and silently. MITIGATION:
  enumerate from source rather than from this list; the list above is a starting
  point and is explicitly NOT verified complete.
- RISK: over-releasing on park breaks the sleeping-duplicate guarantee.
  MITIGATION: R2 test asserts the park case stays refused.
- RISK: `Spellbook.cleanup` does `_spell_ids.clear()` then `del`. With the live
  alias the frame sees the clear; with a unified set it sees nothing. Ordering
  against `_unregister_conduit_spells_from_aether` is UNKNOWN - its call sites
  were never traced.

## Validation plan
- Component: cleanup-then-rebind, per path.
- Component: park-then-duplicate-bind stays refused.
- Integration: frame cleanup with two books, then rebind both targets.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: risk analysed and scoped; blocked only on the unified set.

## Applicable Anti-Patterns
- [ ] Do not treat the path list above as complete - it is a lead, not an
      inventory.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.

## Notes

- DATETIME: 2026-08-02T20:25:00Z
  TYPE: RISK
  CLAIM: THE ALIAS IS DOING INVISIBLE WORK TODAY, and moving to a shared set
    removes it. `AethericFrame._selected_spell_registry[conduit_id]` stores the
    live `Spellbook._spell_ids` OBJECT, not a copy
    (`aetheric_frame.py:1026`, comment: "Live REFERENCE... frame never
    re-derives"). So `Spellbook.cleanup`'s `_spell_ids.clear()` at `:511` mutates
    the shared object and the frame's view empties as a side effect - no explicit
    release is written anywhere, and none is needed. Every teardown path in the
    codebase was written under that assumption.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1024-1026
  - src/melder/aether/spellbook/spellbook.py:511-514
  IMPACT: The moment ids live in a set the Spellbook does not own, EVERY teardown
    path silently stops working. Nothing will fail loudly; ids simply accumulate.
    This is why this is a separate story and not a step in S2.
  NEXT: Enumerate destruction paths from source, then add explicit release to
    each, then test cleanup-then-rebind on every one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-02T20:25:00Z
  TYPE: UNKNOWN
  CLAIM: The ordering between `Spellbook.cleanup`'s `_spell_ids.clear()` and
    `_unregister_conduit_spells_from_aether` is not established. If unregister
    runs first the frame entry is already gone and the clear is harmless; if it
    runs after, the frame briefly holds a reference to a set the Spellbook has
    disowned. `_unregister_conduit_spells_from_aether` is defined at
    `spellbook.py:2511` and its call sites were never traced.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2511-2532
  IMPACT: Decides whether teardown ordering needs changing alongside the release
    calls, or whether release can simply be added at each site.
  NEXT: `grep -rn "_unregister_conduit_spells_from_aether" src/` and read the
    call sites before writing any release code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Do not start this before the unified set exists, and do not fold it into that
story. The whole risk is that today's teardown paths work by ACCIDENT - they
mutate a shared object through an alias - and a unified set removes that accident
without any of them failing loudly. Enumerate destruction paths from source
first; the list in Requirements is a lead, not an inventory.
