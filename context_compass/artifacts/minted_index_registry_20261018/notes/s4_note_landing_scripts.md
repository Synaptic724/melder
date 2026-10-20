- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The landing pass is scripted, each part checked against the 0.2.8256 tree and documents (--check, with
    0.2.8257 standing in for the notch S4 takes). apply_s4.py now takes the notch (--notch) and writes it beside the
    patch id where its comments and docstrings named the patch alone, as S9's do ("(direct_cleanup_refusal,
    0.2.8256)"); its anchors still hold. land_s4_docs.py writes the documentation draft into the four system
    documents: section headers or short phrases melder_0's S1/S2 documentation does not reach anchor the edits,
    code-map records are found by path and remeasured from disk, and the counts S4 moves are recounted from disk
    (integration 176 of 183, spellbook tree 53, 852 in the three tiers; the S4 test file is on disk already). It
    also corrects tests_components' core count: the key-file union is 265, not the 264 it states, since S9
    (0.2.8256) added a key file without updating it - 266 with S4's. graph_prose_s4.py adds the Spellbook node's
    registration responsibility and the lineage condition to MutationResearch's residency one; release_note_s4.py
    adds the section, the packaging bullet and the rebuild line, its example run as written by
    run_release_note_block_s4.py (it raises on 0.2.8256 and holds with A-D, GIL off and on).
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-265
  - context_compass/artifacts/minted_index_registry_20261018/scripts/land_s4_docs.py:1-474
  - context_compass/artifacts/minted_index_registry_20261018/scripts/graph_prose_s4.py:1-69
  - context_compass/artifacts/minted_index_registry_20261018/scripts/release_note_s4.py:1-113
  - context_compass/artifacts/minted_index_registry_20261018/probes/run_release_note_block_s4.py:1-18
  - context_compass/artifacts/minted_index_registry_20261018/runs/release_note_block_s4_repo_and_abcd.txt:1-4
  - context_compass/system_docs/tests_components.md:2025-2027
  IMPACT: After the handover the pass is mechanical: re-check every anchor on the landed tree, apply A-D with the
    notch, run the tests, the whole tree and the probes, then the documents, graph, release note, notch, closure
    and the rebuild in a mirror.
  NEXT: melder_0's handover NOTICE (the mailbox read every 30 seconds while blocked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
