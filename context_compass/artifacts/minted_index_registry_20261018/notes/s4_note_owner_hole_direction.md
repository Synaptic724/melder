- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner's question and direction (chat 2026-10-18): "so why would we ever have an index without a spell in
    it? ... by default we should have one, and our mechanisms are trying to enforce at least 1 active spell", then
    "we probably do need to have a way to have a hole available with no_active_spell and a way to manage this state
    and notify all dependencies and reliances so they revalidate ... cleaning up a spell thats actively relied on
    could then be reasonable instead of just refusing it so that is the right approach to all your issues I think
    but we need a new spellsystemstate for it and various other concepts need to overlap with this". The code's
    answer: every path keeps one active spell per index - `bind` makes its new index's spell active,
    `bind_inactive` and `add_to_spell_index` only park versions in an existing index (an emptied source is
    destroyed), a notch swaps which version is active, the three cleanup calls refuse the active member while
    parked versions remain (0.2.8256), and an index goes with its last member - except `remove_from_spell_index`,
    whose contract is that the separated version "becomes the only member of a fresh index and stays parked" (kept
    by the owner's S10 ruling: activation takes a notch). So Melder already has an index with no active spell, and
    nothing manages it: S4, S5, S7, S9 and S10 of the correctness epic are its symptoms, S1 (C4), S2 (C7) and S8 (its
    minted-index branch) in part.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5806-5822
  - src/melder/aether/spellbook/spellbook.py:5279-5300
  - src/melder/aether/spellbook/spellbook.py:4095-4269
  - src/melder/aether/spellbook/spellbook.py:1590-1649
  - src/melder/aether/spellbook/spellbook.py:4271-4388
  - src/melder/aether/spellbook/spellbook.py:4390-4456
  - src/melder/aether/spellbook/spellbook.py:700-713
  - src/melder/aether/conduit/conduit.py:6122-6210
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:94-123
  IMPACT: A managed no_active_spell state makes S4's registration (A) and teardown (B) part of one design, makes C
    unnecessary if such an index selects nothing, and replaces S9's refusal; it is an epic (the owner's rule: an
    epic and its stories before implementing) reaching SpellIndex, SpellSystemStates, the meld gate, contracts and
    index links, the record, Nexus and residency.
  NEXT: Ask the owner to open that epic, a design story first (no src); S4 waits for its outcome.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
