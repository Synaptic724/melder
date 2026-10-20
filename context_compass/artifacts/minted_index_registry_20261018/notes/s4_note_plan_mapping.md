- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The patch read in the required order (architecture, Spellbook component, MutationResearch component) and
    mapped patch section -> implementation step -> validation step. No code-description patch: no state machine,
    gate pipeline, rollback or concurrency semantics change. (1) Changed components (the seam) and the Spellbook
    patch's Before/after -> edit A in `_apply_remove_from_index`: after the Book-locked move and with bind's guard,
    `Spellbook._aether._register_single_spell_index(self._get_required_conduit_surface()._id, new_index,
    self._aetheric_frame_name)`; the entry's Contract, the seam's summary, step 4 and Threading -> tests: the version
    is found by spell_id parked and notched active (frame index and conduit, both Conduit lookups), a grant and a
    transfer by spell_id proceed, a second bind of its spell_id is refused (another Book of the frame, conjured and
    not; a Book of another frame under process-wide ids), the move back drops the minted index; probes M2-M5, M7.
    (2) The teardown invariant and the Spellbook patch's teardown half -> edit B in
    `_unregister_conduit_spells_from_aether`: each parked version's index joins the set under the Book lock, read
    through `_spell_index_unless_cleaned`; Contract and Threading -> test: a torn-down root leaves no registry or
    id-set entry and its separated version's index is not found; probe M6. (3) The residency component patch ->
    edit C in `_locate_live_membership` (CRLF kept): active only when the index selects the version and
    `get_by_index_id(index.id).current_spell_id` is it (None for an index no lineage registered); the verdict text
    and the method's Contract -> tests: V2 parked, V3 active, V1 and V4 as before; two unit tests whose frame
    doubles leave the lineage unset would read parked under C and get doubles whose lineage tracks the selected
    id (`test_root_residency_view_reports_runtime_and_custody_join`,
    `test_residency_view_prefers_selected_membership_in_later_frame`), and a new unit test reads a selected version
    no lineage tracks as parked; probe V1-V4. (4) Docstrings -> edit D in `Spell._spell_index_unless_cleaned` ->
    the documentation ritual. (5) No new lock edge -> registration after the Book lock, teardown reads Book ->
    spell -> the whole tree in a /tmp mirror by shards, GIL off and on. (6) Migration 5-7 and Rollback -> system
    documents, indexes and graph, the release note, the next free notch, closure, the rebuild last; no cache
    generation or record version moves.
  EVIDENCE:
  - context_compass/system_docs/patches/active/minted_index_registry_2026_10_18/architecture_patch.md:1-72
  - context_compass/system_docs/patches/active/minted_index_registry_2026_10_18/component_patch_spellbook_minted_index_registration.md:1-60
  - context_compass/system_docs/patches/active/minted_index_registry_2026_10_18/component_patch_mutation_research_residency.md:1-36
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-258
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:361-397
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:439-482
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:560-576
  IMPACT: The patch gate's mapping is recorded; tests may be written now, src edits wait for the files (M1-40).
  NEXT: Read S9's integration test and the three probes for conventions, then write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
