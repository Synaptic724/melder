- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: One step of the patch's reversal undoes the refusal when the refused version shares the restored version's
    address - the usual case, probe N2's. Staging a version under the active version's key drops that key's frame
    claim and Book address lookup (STORY-2026-10-17-staged_version_releases_active_signature, C1, unfixed), so
    before the notch English holds neither. The reversal runs the seam toward English, whose promotion sets both to
    English again (`_reactivate_owned_spell` sets `_lookup_spells[key]`, `_apply_notch` calls `update_lookup`); the
    step "set the incoming key's lookup and claim back to their before-values" would then release both: English
    active but unclaimed and not meldable by address, against this story's acceptance ("the lender melds English by
    address"). Refinement for the code: set the refused version's key back only when it is not the restored
    version's key, or when there is no restored version (a minted index); a shared key is left to the reversal's
    promotion, as a notch back leaves it today. Asked of the owner with the edit list.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1500-1622
  - src/melder/aether/spellbook/spellbook.py:3911-4066
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:307-336
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:83-89
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_notch_refusal.md:24-30
  IMPACT: Without it the main acceptance test fails after the fix; with it a refused notch also leaves English's
    address claimed, which staging (S1) had dropped - the structure S1's own fix will keep in place.
  NEXT: The owner's OK on the refinement; then the patch docs updated to say it, before the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
