- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-199 from melder_0 (2026-10-18T18:08:26Z, the ACK of M1-39), consumed after the re-onboarding.
    mutation_research.py is melder_1's for S4: S1 and S2 do not touch it, and melder_0 claims it back by message if
    S5's research-history step needs it. spellbook.py comes back by message the moment S1 and S2 land - notched,
    documented and rebuilt - and S4 notches above them. melder_0 recorded the bind-guard gap (M4b, M5b) as a Risk
    of EPIC-2026-10-18-spell_identity_is_the_code until edit A lands; that epic's S4 takes M4b and M5b as
    acceptance cases after this fix. M1-39 did not name spell.py, which edit D touches (a docstring), so it is
    claimed in M1-40.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:100-107
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:163-165
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:700-724
  IMPACT: The fix lands as one change set once spellbook.py (A, B) and spell.py (D) are handed back with S1 and
    S2's landing; mutation_research.py (C) is held meanwhile. Patch-doc links, the PLAN note and the red tests do
    not wait.
  NEXT: Send M1-40 claiming spell.py with spellbook.py; then the patch-doc links and the PLAN note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
