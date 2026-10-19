- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch book_teardown_parked_2026_10_19 (architecture and a Spellbook component patch; no code-description
    patch - no state machine, gate or rollback semantics change) mapped to steps and tests. Edit (apply_s7.py, one
    module): (A) `_cleanup_spells`' docstring names the parked loop and its threading; (B) after the active loop,
    each parked version's index is read while the version is live and noted when no active member holds it, the
    version is retired locally (`_spellbook_cleanup`, `Spell.cleanup()`), then each noted index is cleaned - every
    step best-effort and logged; (C) `_cleanup_components`' docstring names them. Tests (new integration file, 8
    cases): six regressions red on 0.2.8259 - a parked version on a shared index and alone in its own index, with the
    frame kept and collapsed, a version parked before conjure under a direct `Spellbook.cleanup()`, a parked managed
    version's Spell - and two controls (active only; a parked version disposed first). In a /tmp mirror with the
    edit (preview 72 lines): 8 passed, the GIL off and on; probe T2 and T3 fixed, T1, T4 and T5 unchanged. Then the
    whole tree, docs, graph, the release note, the next notch (0.2.8260 unless someone notches first), closure and
    the rebuild last. No src edit before the owner's word.
  EVIDENCE:
  - context_compass/system_docs/patches/active/book_teardown_parked_2026_10_19/architecture_patch.md:1-44
  - context_compass/system_docs/patches/active/book_teardown_parked_2026_10_19/component_patch_spellbook_book_teardown.md:1-30
  - context_compass/artifacts/book_teardown_parked_20261019/scripts/apply_s7.py:1-141
  - context_compass/artifacts/book_teardown_parked_20261019/runs/s7_preview_0_2_8259.diff:1-72
  - tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py:1-330
  - context_compass/artifacts/book_teardown_parked_20261019/runs/red_s7_0_2_8259_gil0.txt:1-32
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_mirror_gil0.txt:1-2
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_mirror_gil1.txt:1-10
  - context_compass/artifacts/book_teardown_parked_20261019/runs/prototype_s7_probe_book_teardown_parked_gil0.txt:1-30
  IMPACT: The patch gate's mapping is recorded; the edit waits for the owner's word only (melder_0 holds no src file,
    M0-207).
  NEXT: The owner's word on the edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
