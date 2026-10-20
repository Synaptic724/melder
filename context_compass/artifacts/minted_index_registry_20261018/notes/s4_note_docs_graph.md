- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The documents and the graph carry S4 at 0.2.8259. land_s4_docs.py wrote the four system documents (a new
    operational invariant, a fixed failure mode, the index mutation sequence, the code map remeasured, the
    handoff entries; the component, tests-architecture and tests-components entries); remap_s4_citations.py
    moved 9 citation lines in src_architecture and 14 in src_components across A-D; the citation check finds only
    the two bare file names of handoff history it found at 0.2.8256. mark_gap_fixed_s4.py marked fixed the
    collision-check gap S1 and S2's text still called open (the identity invariant's Open list, the identity
    release-note section's Known limits). All four indexes --check OK. The graph: extract_graph.py --strict
    exit 0 (593 descriptors, none skipped); graph_prose_s4.py added the Spellbook's registration responsibility and
    the lineage condition to MutationResearch's residency one; the Spellbook and Spell nodes, read against S1 and
    S2's changes and A-D, accepted; MutationResearch stays SEMANTICS_STALE (its prose was authored against an
    older span before S4 and needs a full re-read); assemble_graph.py --check OK (593 sections, 28190 lines).
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/runs/land_s4_docs_apply_0_2_8259.txt:1-7
  - context_compass/artifacts/minted_index_registry_20261018/runs/remap_s4_citations_apply_0_2_8259.txt:1-75
  - context_compass/artifacts/minted_index_registry_20261018/runs/citation_check_0_2_8259.txt:1-3
  - context_compass/artifacts/minted_index_registry_20261018/scripts/mark_gap_fixed_s4.py:1-50
  - context_compass/artifacts/minted_index_registry_20261018/runs/graph_extract_0_2_8259.txt:1-46
  - context_compass/artifacts/minted_index_registry_20261018/runs/graph_accept_0_2_8259.txt:1-6
  - context_compass/artifacts/minted_index_registry_20261018/runs/graph_assemble_check_0_2_8259.txt:1-4
  IMPACT: Only the notch, the release note, the closure and the rebuild remain.
  NEXT: Notch to 0.2.8259, then release_note_s4.py and close_s4.py, then the rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
