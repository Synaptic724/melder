- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs drafted (failed_notch_refusal_2026_10_18; Artifact Links). Mechanism: `Spellbook._notch_spell`
    records the before-state, runs the seam, then runs phases 1-4 for a never-compiled incoming version inside the
    window (the commit validator's own test); on a broken verdict it reverts (`_revert_refused_notch`, new: the seam
    run toward the outgoing version with reason `mutation_rolled_back`, then the incoming key's Book lookup and frame
    claim set back; with no outgoing version - a minted index - park, unregister, Nexus record out), resets the
    refused version's Phase 1-4 artifacts and raises SpellbookValidationError with a new `preface` line saying the
    notch did not happen. The research journal entry moves after the check. Mapping, patch section -> step ->
    validation: architecture invariants and the notch component's After -> `_notch_spell`, `_apply_notch` minus the
    journal, `_revert_refused_notch`, the artifact reset -> component tests 1-5 and integration N1-N3, GIL off and
    on; the preface component -> `SpellbookValidationError.__init__(..., preface=None)` and its docstring -> unit
    tests (message unchanged without it, first line with it, TypeError for a non-str or empty one); docstrings
    (`Conduit.notch_spell`, the CCM validator, `_stage_spell_for_structural_phases`) -> the documentation ritual.
    No src edit before the owner approves the patch and melder_0 hands the files over.
  EVIDENCE:
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-62
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_notch_refusal.md:1-54
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_validation_error_preface.md:1-21
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/code_description_patch_notch_refusal.md:1-35
  IMPACT: The ENTRY_GATE's patch docs exist; what remains before code is the owner's approval and the file claim.
  NEXT: Ask the owner to approve the patch docs; claim spellbook.py, conduit.py, spellbook_validation_error.py and
    change_control_manager.py from melder_0 once he does.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
