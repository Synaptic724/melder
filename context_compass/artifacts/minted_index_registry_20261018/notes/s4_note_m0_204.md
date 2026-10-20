- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-204 from melder_0 (2026-10-18T23:43:33Z, the handover NOTICE answering M1-40), consumed. S1 and S2 of
    EPIC-2026-10-18-spell_identity_is_the_code landed and are turned in at 0.2.8257 and 0.2.8258 (`__version__`
    0.2.8258): their release-note sections, the system documents, the graph and the rebuild, both checks OK.
    spellbook.py and spell.py are melder_1's again and melder_0 holds no src file, so every file S4 edits is free;
    S4 notches above 0.2.8258. For S4's tests: one object is one spell now, so a test that needs a second
    registration of a class binds a version of it (`version_of` in tests/_spell_identity_test_support.py) or a
    class of its own. melder_0 rebuilt in a /tmp mirror and copied back byte for byte, its LLM bundles too (the
    mirror must carry the tracked src/melder/__melder_cache__/__melder_cache__.py).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:882-914
  - src/melder/__version__.py:12-12
  - tests/_spell_identity_test_support.py:18-21
  IMPACT: The ENTRY_GATE's last condition is met; the landing pass starts on the landed tree: re-check every
    script's anchors and the S4 tests, tell the owner, then apply A-D.
  NEXT: Re-sync the /tmp mirror to 0.2.8258, re-check the landing scripts and run the S4 tests on the tree (red).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
