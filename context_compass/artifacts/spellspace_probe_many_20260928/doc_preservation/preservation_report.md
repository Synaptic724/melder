# Content preservation report - spellspace_probe_many_2026_09_28 promotion (2026-09-28)

Baseline captured before the first edit (src_components_before.txt, src_components_before.md); the after-capture
spans the document alone (nothing was moved out) and was retaken after the second pass
(docs/edit_src_components_failure_mode.py). Comparison: src_components_compare.md (15 lines lost, 42 added).
Every lost line is accounted for:

- 5 lines: the Creations and SpellSpace failure mode "Known probe inaccuracy (2026-09-27)" (with its
  EVIDENCE line), removed because the probe is fixed; the fix and the old behaviour are recorded in the Meld
  Resolution Runtime paragraph "Live-creation probe scope" (CORRECTED 2026-09-28) and the handoff.
- 3 lines: the Meld Resolution Runtime responsibility "Select creations container by Existence", replaced by
  the corrected bullet, which quotes what the old text claimed.
- 3 lines: the C1 fields of spellspace_meld.py (end_line, loc 1031 -> 1045; verified_at).
- 4 lines: the Meld Resolution Runtime failure mode "SpellSpaceScopeError for unique_per_spell_space without an
  active spellspace", replaced by the RuntimeError the conduit door raises (CORRECTED 2026-09-28, quoting the
  old claim); it contradicted the new probe-scope paragraph.

Added: the probe-scope paragraph (13 lines with evidence), the corrected responsibility (7), flow step 4 (4),
the C1 fields (3), the handoff paragraph (8) and the corrected failure mode (7).
