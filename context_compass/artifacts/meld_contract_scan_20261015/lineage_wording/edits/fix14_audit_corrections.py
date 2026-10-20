"""Corrections found by the audit of the applied wording edits (melder_1, 2026-10-18).

The owner's order (chat 2026-10-18): "if their docstrings were adjusted make sure they are fine ... after that ...
move on". Three applied lines say something the code does not do; each goes to the wording the code supports.
Not named batch*.py on purpose: audit_edits.py reads batch*.py as the applied edit set.

- conduit_meld.py 755, 915: the conduit door refuses every `requires_spellspace_request` spell (Phase 5 sets the
  flag for a spellspace-scoped spell AND for any spell that depends on one: spell_system_root_blueprint_builder.py
  274-296), not only spellspace-scoped ones; the class docstring (line 31) already says so.
- transfer_of_ownership.py 1131: `_rollback_creations_move` restores ONE member id per call (`_move_creations`
  registers one handler per member), not the index's members at once.
"""
CM = "src/melder/aether/conduit/meld/conduit_meld.py"
TO = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"

EDITS = [
    (CM, 755,
     "            - Rejects spellspace-scoped spells on the conduit-facing door.",
     ["            - Rejects `requires_spellspace_request` spells on the conduit-facing door."]),
    (CM, 915,
     "            - Rejects spellspace-scoped spells on the conduit-facing door",
     ["            - Rejects `requires_spellspace_request` spells on the conduit-facing door"]),
    (TO, 1131,
     "        target-side creations for the index's members, then restores the original",
     ["        target-side creations for that spell_id, then restores the original"]),
]
