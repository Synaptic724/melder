- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's word (chat 2026-10-18). Shown the defect in one example - the conduit finds French until
    `remove_from_spell_index` moves it into an index of its own, then `get_spell_by_spell_id` raises "not found in
    any conduit" - he put it as "we're not updating the dam spellbook registry objects properly then is this the
    issue?" (yes: the frame's registry, not the Book's maps, which still answer), then: "it should properly follow
    the general spell index creation and registry binding processes the same way it does during bind yeah". So S4
    is fixed as filed, its boundary widened on his word: A - the seam registers its new index the way a
    post-conjure `bind` registers the index it creates, with bind's guard (`self._conjured and self._conduit is not
    None`) and call (`_register_single_spell_index(self._get_required_conduit_surface()._id, ...)`) - the index is
    already created as bind creates one (`SpellIndex(initial_id=...)`); B - the root's teardown unregisters it with
    the rest; C - residency reports a parked version as parked. A's draft keyed the registration on the spell's
    owner stamp; it is re-shaped to bind's guard and conduit. No new state (ALIGNMENT_CHECK notes).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5919-5925
  - src/melder/aether/spellbook/bind/bind.py:795-804
  - src/melder/aether/spellbook/spellbook.py:4372-4375
  - src/melder/aether/spellbook/spellbook.py:924-931
  IMPACT: The ENTRY_GATE's word on the edits is given; before the first src edit remain the patch docs, the red
    tests, spellbook.py back from melder_0 after S1 and S2 land, and mutation_research.py claimed by message.
  NEXT: Re-shape A in the lane's script, re-run the probes on the new A+B+C copy (GIL off and on), update the
    story's contract, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
