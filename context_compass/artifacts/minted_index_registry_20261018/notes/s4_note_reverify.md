- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8256, re-verified before any change as the owner asked. melder_0's two probes,
    copied with the 0.2.8253 renames (`find_spell_by_id` -> `find_spell_by_spell_id`, `get_spell_by_id` ->
    `get_spell_by_spell_id`), ran on Python 3.14.7t; with the GIL on each output equals the GIL-off run apart from
    the GIL-mode warning. M1 (control): the frame finds French parked in English's index, and
    `get_spell_by_spell_id` now answers French itself, by the 0.2.8253 rule (it answered English). M2 (French alone
    and parked in the minted index) and M3 (French notched active there): `find_index_for_spell` answers None,
    `find_conduit_id_for_spell` not the lender, `get_spell_by_spell_id` and `get_conduit_by_spell_id` raise "Spell
    version <id> not found in any conduit."; in M3 `meld(spell_id=French)` builds French while a borrower's
    `add_spell_to_contract(spell_id=French)` raises the same ValueError. V1-V4: `residency_view` reads French
    `declared_only in none` in the minted index, parked (V2) and active (V3); members of English's index read right.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_minted_index_registry_0_2_8256.py:1-152
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_registry_0_2_8256_gil0.txt:1-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_registry_0_2_8256_gil1.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_research_residency_moves_0_2_8256.py:1-113
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_research_residency_moves_0_2_8256_gil1.txt:1-17
  IMPACT: Nothing landed since 0.2.8251 changed the failure; only M1's answer moved, as the 0.2.8253 rule says.
  NEXT: Read the minting seam, the frame registry and its readers whole (FACT note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
