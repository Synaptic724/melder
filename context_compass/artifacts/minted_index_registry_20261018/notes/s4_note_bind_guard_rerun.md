- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Edit A re-shaped to the owner's word in the lane's script: the seam registers its new index with bind's
    guard (`self._conjured and self._conduit is not None`) and call (`_register_single_spell_index` under
    `self._get_required_conduit_surface()._id`), and its docstrings say so; B and C unchanged. The three probes
    re-run on fresh /tmp copies of the 0.2.8256 src with A, A+B and A+B+C (GIL off; A+B+C GIL on too): every output
    is byte-equal to the run the prototypes' MEASURE note recorded, so the re-shape changes nothing the probes see
    (in their worlds the spell's owner stamp and the Book's root conduit are one id). The preview of the three
    edits against 0.2.8256 is now 162 lines.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-237
  - context_compass/artifacts/minted_index_registry_20261018/runs/s4_preview_0_2_8256_bind_guard.diff:1-162
  IMPACT: The edits to land are this preview's; the earlier preview stays as the record of the first draft.
  NEXT: Update the story's contract to the owner's word; then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
