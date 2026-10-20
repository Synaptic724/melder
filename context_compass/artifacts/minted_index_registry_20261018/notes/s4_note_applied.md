- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Edits A-D are in the repository, on the 0.2.8258 tree melder_0 handed back (M0-204), as the owner approved
    them (owner told first, chat): apply_s4.py with the notch S4 takes, 0.2.8259, written beside the patch id in the
    comments and docstrings; every anchor found once; spellbook.py and spell.py LF, mutation_research.py CRLF kept
    (4005 lines, all CRLF); the three files byte-equal to the /tmp mirror's. The landed diff is 182 lines. Before it,
    every landing script was re-checked on 0.2.8258: apply_s4.py, land_s4_docs.py (counts from disk: integration 176
    of 183, the spellbook tree 53, the three tiers 857), release_note_s4.py, graph_prose_s4.py and close_s4.py
    --check, and remap_s4_citations.py on a /tmp root (9 and 14 citation lines). The S4 tests on the 0.2.8258 tree
    before A-D: 12 failed, 38 passed, GIL off and on - the same cases and reasons as on 0.2.8256; in the mirror with
    A-D: 50 passed, GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2695-2736
  - src/melder/aether/spellbook/spellbook.py:4290-4435
  - src/melder/aether/spellbook/spell.py:963-1004
  - src/melder/mutation_research/mutation_research.py:1374-1541
  - context_compass/artifacts/minted_index_registry_20261018/runs/apply_s4_repo_0_2_8259.txt:1-4
  - context_compass/artifacts/minted_index_registry_20261018/runs/s4_landed_0_2_8258_abcd.diff:1-182
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_s4_0_2_8258_gil0.txt:1-54
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_s4_0_2_8258_gil1.txt:1-62
  - context_compass/artifacts/minted_index_registry_20261018/runs/green_s4_mirror_0_2_8259_gil0.txt:1-2
  - context_compass/artifacts/minted_index_registry_20261018/runs/green_s4_mirror_0_2_8259_gil1.txt:1-10
  IMPACT: The fix is in src; the version is still 0.2.8258 until the notch, which follows the validation and the
    documents in the contribution guide's turn-in order.
  NEXT: The whole tree by shards in the mirror, GIL off and on; then the probes M1-M7, V1-V4, G1-G3 and the release
    note's block.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
