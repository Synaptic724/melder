- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The documents and the graph carry S7. Citations: every numeric `spellbook.py:N` past the edit moved 45 lines
    and was remapped line by line against the pre-edit copy (11 lines in src_architecture, 14 in src_components;
    handoff history left as written). src_architecture: the cleanup sequence, a new operational invariant, a fixed
    failure mode, the 0.2.8256 invariant's "Not changed", the code map (7903 lines) and a handoff entry;
    src_components: Spellbook Core's cleanup line, a new invariant, the 0.2.8256 invariant's teardown sentence, the
    code map and a handoff entry; tests_components: the Spellbook Integration Cluster's new module (8 tests), a key
    file and its code-map record, counts recounted (integration 177 of 184, spellbook tree 54, 858 test modules,
    key-file union 274 = code-map records); tests_architecture: the inventory and a handoff entry. The four indexes
    are regenerated and their checks read OK; the citation check reports only the two bare file names in
    src_components' handoff history, as at 0.2.8259. The graph: extract --strict (593 descriptors, none skipped),
    Spellbook's 27 responsibilities re-read against the edited source and one added (the teardown's parked loop),
    accepted, assembled (28191 lines) and checked OK. The release note's example runs as written, GIL off and on.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1094-1095
  - context_compass/system_docs/src_architecture.md:1159-1177
  - context_compass/system_docs/src_architecture.md:2412-2418
  - context_compass/system_docs/src_components.md:746-759
  - context_compass/system_docs/tests_components.md:1793-1800
  - context_compass/system_docs/src_graph.md:15888-15888
  - context_compass/artifacts/book_teardown_parked_20261019/runs/remap_s7_citations_apply.txt:1-79
  - context_compass/artifacts/book_teardown_parked_20261019/runs/land_s7_docs_apply.txt:1-5
  - context_compass/artifacts/book_teardown_parked_20261019/runs/citation_check_0_2_8260.txt:1-4
  - context_compass/artifacts/book_teardown_parked_20261019/runs/graph_extract_0_2_8260.txt:1-46
  - context_compass/artifacts/book_teardown_parked_20261019/runs/graph_assemble_check_0_2_8260.txt:1-4
  - context_compass/artifacts/book_teardown_parked_20261019/runs/release_note_probe_0_2_8260_gil1.txt:1-5
  IMPACT: The documents describe the landed behaviour; the notch, the release-note entry, the closure and the
    rebuild remain, in that order.
  NEXT: Notch 0.2.8259 -> 0.2.8260 (read at that moment), then the release-note section.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
