- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The patch docs now carry the owner's go, the shared-key refinement and the preface's line-break refusal
    (scripts/patch_docs_refinement_20261019.py), and every method the fix changes was re-read whole on the mirror
    (0.2.8260). Mapping, patch section -> step -> validation: the architecture invariants and the notch component's
    After -> `_notch_spell` (the before-state, the seam, `_check_notched_version`, the journal once the notch
    stands), `_apply_notch` without the journal, `_revert_refused_notch` (the seam run back with
    `mutation_rolled_back`; a differing key set back by `_restore_binding_key`; a minted index through
    `_revert_refused_activation` and `_remove_spell_record_from_nexus`) and the artifact reset -> the 14 integration
    tests (13 red, one control), GIL off and on; the preface component -> `SpellbookValidationError.__init__(...,
    preface=None)` and `_check_preface` -> the 7 unit tests plus a new line-break test; the docstrings
    (`Conduit.notch_spell`, the CCM validator, `_stage_spell_for_structural_phases`) -> the documentation ritual.
    Two of the four files are CRLF on disk (spellbook_validation_error.py, change_control_manager.py; git holds
    them LF), so their edits keep CRLF.
  EVIDENCE:
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-69
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_notch_refusal.md:1-62
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/code_description_patch_notch_refusal.md:1-38
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_validation_error_preface.md:1-23
  - src/melder/aether/spellbook/spellbook.py:3947-4157
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:147-174
  IMPACT: The code follows the patch section by section; the red set is its acceptance.
  NEXT: Write the edit script for the mirror and run the red set with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
