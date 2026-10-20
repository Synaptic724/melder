- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner did not take the three edits (chat 2026-10-18): "lets talk please you can't just unregister
    indexes without an active version". Edit B was read as unregistering live indexes that hold no active version.
    It does not: `_unregister_conduit_spells_from_aether` has one caller, the root's permanent teardown
    (`Conduit._cleanup_normal_conduit` step 4, reached from `_permanent_cleanup` for a normal conduit only), which
    already removes every index of the dying root that holds an active version, just before the Book is cleaned.
    B adds the indexes holding only parked versions to that same teardown. While the root lives nothing is
    unregistered: with A the minted index stays registered whether its version is parked or active, and leaves only
    when it empties (`_destroy_spell_index`, as today) or its root is torn down. Without B, A leaves the dead root's
    entry, because the frame drops a conduit's entry only once its set is empty (prototype A, M6). Explained to the
    owner; his word is awaited, and nothing changes meanwhile.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:805-860
  - src/melder/aether/conduit/conduit.py:1034-1178
  - src/melder/aether/spellbook/spellbook.py:2695-2716
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1216-1240
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_A_probe_minted_index_fix_cases_gil0.txt:19-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_AB_probe_minted_index_fix_cases_gil0.txt:19-26
  IMPACT: The scope question stays open; the boundary, patch docs and tests wait for the owner's answer.
  NEXT: The owner's answer on B (and on A + C).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
