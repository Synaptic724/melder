# Task: Investigate Spell Examiner Registry Rebuild
- Completed: 2026-04-09T21:59:36Z
- Summary: Locked the SpellExaminer rebuild boundary before the registry-driven implementation landed.


## Metadata
- Task ID: TASK-2026-04-05-investigate-spell-examiner-registry-rebuild
- Story: STORY-2026-04-05-spell-examiner-registry-rebuild
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T13:45:00Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Lock the live SpellExaminer consumer surface and the safe rebuild boundary
before implementation starts.

## Notes
- DATETIME: 2026-04-05T13:45:00Z
  TYPE: FACT
  CLAIM: The live `src/` consumer surface is narrow. The only non-test
    `SpellExaminer(...)` construction path currently found is in
    `bind.py`, and the only live runtime use from there is
    `binding_profile_for_object(...)`. The richer resolution and AI profile
    creation paths exist in `SpellExaminer`, but they are not called from live
    runtime paths in `src/`. At the same time, `spell.profile` is definitely
    live and at least one runtime consumer in
    `spellbook_creation_system.py` still expects it to be binding-profile
    shaped. So the safe rebuild is:
    1) rebuild SpellExaminer itself,
    2) keep current profile families intact,
    3) keep bind on the binding-profile path for now,
    4) rewire direct consumers/tests to the new `create_profile(...)` contract.
  EVIDENCE:
  - src/melder/spellbook/bind/bind.py:198-199
  - src/melder/spellbook/bind/bind.py:284-285
  - src/melder/spellbook/spell.py:265-298
  - src/melder/spellbook/spellbook_creation_system.py:451-453
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py:1-175
  IMPACT: We can safely rebuild the examiner API without reopening the wider
    spell/descriptor profile-storage contract in the same slice.
  NEXT: implement the registry-driven SpellExaminer and rewire bind/tests to
    the new contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The consumer scan is done and the implementation boundary is locked.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

