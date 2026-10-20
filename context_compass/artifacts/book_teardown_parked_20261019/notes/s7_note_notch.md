- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Notched 0.2.8259 -> 0.2.8260, read at that moment (no other lane had notched). The running release note's
    header reads 0.2.8260; its new section "A Spellbook's teardown cleans its parked versions too" stands before
    "Packaging and documentation", its example byte-equal to the probe that ran as written with the GIL off and on;
    the packaging list gains the system documents' bullet and its rebuild line names 0.2.8260.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-1
  - release_docs/next_version_release.md:1049-1082
  - release_docs/next_version_release.md:1214-1217
  - context_compass/artifacts/book_teardown_parked_20261019/probes/probe_release_note_s7.py:1-25
  - context_compass/artifacts/book_teardown_parked_20261019/runs/release_note_probe_0_2_8260_gil0.txt:1-1
  IMPACT: The turn-in's notch and release-note steps are done; the closure and the rebuild remain.
  NEXT: The closure (story to completed/, board and artifact sync, the patch archived), then the rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
