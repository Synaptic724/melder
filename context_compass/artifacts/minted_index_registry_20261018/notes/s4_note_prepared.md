- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Prepared while spellbook.py and spell.py wait for S1 and S2's landing. (1) melder_0's S1+S2 src diff (his
    lane, 17:48Z) changes spellbook.py in seven hunks (2564-2576, 2605-2618, 2635-2643, 2851-2868, 5443-5453,
    5557-5563, 5792-5802 of 0.2.8256) and spell.py in eighteen, the nearest ending at 865; none reaches the text A,
    B or D anchor on (spellbook.py 2695-2716 and 4271-4388, spell.py 911-924), so the edits should apply unchanged.
    They are re-checked on the landed tree before applying, since the landing may differ from that diff. (2) The
    documentation is drafted - the architecture's invariant, failure mode, sequence, code map and handoff entries,
    the component entries, the tests map and the release note - to be applied after the edits, against the landed
    documents. (3) The release note's example runs as written: on 0.2.8256 the lookup of French's spell_id after
    the move raises ValueError "Spell version ... not found in any conduit."; with A-D every assert holds, GIL off
    and on.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_s1s2_src.diff:693-916
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_s1s2_src.diff:1391-1529
  - src/melder/aether/spellbook/spellbook.py:2695-2716
  - src/melder/aether/spellbook/spellbook.py:4271-4388
  - src/melder/aether/spellbook/spell.py:911-924
  - context_compass/artifacts/minted_index_registry_20261018/notes/s4_docs_draft.md:1-157
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_release_note_s4.py:1-36
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_release_note_s4_repo_and_abcd.txt:1-4
  IMPACT: The landing pass is mechanical once the files come back: re-check the anchors, apply, run, docs, notch,
    closure, rebuild.
  NEXT: melder_0's handover message (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
