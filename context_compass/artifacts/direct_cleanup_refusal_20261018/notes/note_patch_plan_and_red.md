- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written (direct_cleanup_refusal_2026_10_18: architecture and component; no code-description -
    a plain refusal with no new control flow) and red tests run. Mapping, patch section -> step -> validation: the
    invariants and the component's After -> `Spellbook.cleanup_and_remove_spell`: in its first Book-locked section,
    after the spell is resolved and before `unregister_index`, `SpellIndex.is_sole_member` False logs and raises
    RuntimeError "Spellbook cannot remove spell <id>: it is the active member of a multi-member index; notch away
    from it before disposing it, or dispose the index's parked versions first with cleanup_spell."; its docstring's
    Contract and Raises; `Spell.cleanup`'s Raises -> the integration tests (7) and probe D1-D3 re-run, GIL off and
    on. The Breaking interface delta -> the release note and a src_architecture failure mode; the Spellbook Core
    contract -> src_components; the new test file -> tests_components. Red on 0.2.8255, the same with the GIL off
    and on: 5 failed ("DID NOT RAISE RuntimeError": both doors, by Spell and by spell_id, and the two remedies), 2
    passed (the sole-member controls, either door). Two findings on the way: every test that calls the method
    removes a sole member (ten files, not only the four the FACT note named; the other six stage no version), so
    none changes; and `cleanup_spell`, which decides and removes in two Book-locked sections with no transaction,
    now refuses a version staged in between instead of orphaning it - so the message names no door.
  EVIDENCE:
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/architecture_patch.md:1-49
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/component_patch_spellbook_removal_path.md:1-47
  - tests/integration/melder/spellbook/test_direct_cleanup_refuses_active_member_with_parked_versions_integration.py:1-269
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/red_tests_0_2_8255_gil0.txt:1-19
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/red_tests_0_2_8255_gil1.txt:1-27
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/cleanup_and_remove_spell_callers_0_2_8255.txt:1-41
  - src/melder/aether/spellbook/spellbook.py:4427-4568
  - src/melder/aether/conduit/conduit.py:6212-6264
  - src/melder/aether/spellbook/spell.py:1597-1663
  IMPACT: The ENTRY_GATE's patch exists and the validation step precedes the code; what remains before any src edit
    is the owner's word on the exact edits and melder_0's answer on spell.py (M1-34).
  NEXT: Put the exact edits and the message wording to the owner; claim spell.py from melder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
