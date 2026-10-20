- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: remap_s4_citations.py runs after A-D are applied: it rebuilds each file's pre-edit text by undoing the
    edits it reads from apply_s4.py, then maps old line numbers to new. Since apply_s4.py fills a `{notch}` placeholder
    in its new texts, the remap could no longer find the applied texts; it now takes --notch and fills the
    placeholder the same way before undoing. Checked on a /tmp root holding the three files with A-D at 0.2.8259 and
    today's two documents: spellbook.py 7802 -> 7848 lines, spell.py 1972 -> 1975, mutation_research.py 3990 -> 4005;
    9 citation lines in src_architecture and 14 in src_components remap. The landing scripts write no numeric
    citation into these three files, so the remap can run before or after land_s4_docs.py without shifting a line
    twice.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/remap_s4_citations.py:1-133
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:225-265
  IMPACT: The citation step of the landing pass runs as scripted, with the notch passed as apply_s4.py takes it.
  NEXT: melder_0's handover NOTICE (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
