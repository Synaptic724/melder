"""S5: record the door compiler read (FACT) and the U7 decision in the story."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STORY = ROOT / "tickets/stories/2026-10-15_managed_dispense_codegen_story.md"
NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The door compiler read whole and U7 answered. Doors are template factories compiled once at import, one per
    (route, lane, fast bit): `_build_no_overrides_lines` / `_build_with_overrides_lines` emit each route's body and
    the four `_..._TEMPLATE_BY_ROUTE[...]` tables select them; an unknown route raises "Unsupported CreationContext
    ... route key". The `many` route only calls the plan (`instance = _no_overrides_executor(meld)`, created True;
    with overrides `_execute_with_overrides(meld, overrides)`), and its fast and non-fast bodies are the same lines.
    U7: the hooks lane's `created` flag gates the spell's activation hooks and the `on_meld_activation` meld hook
    (ConduitMeld and SpellSpaceMeld run them only when `created` is True). DECISION: the `managed` route gets the
    `many` bodies under its own route key and source names, so `created` is True on every lease - a lease hands the
    object to a new holder after its resets, so activation hooks run for reused objects too; telling a pop from a
    build would need the plan to report it on the warm path. Template sources are module-level strings compiled by
    `get_or_compile_executor_code`, so adding a route adds entries and changes no existing template's source.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:7-191
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:279-495
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-883
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:1160-1229
  - src/melder/aether/conduit/meld/conduit_meld.py:687-726
  IMPACT: B7's door line is settled (U7 closed): eight new template objects (four lanes x fast bit share the many
    bodies) and table rows for "managed"; no existing template changes.
  NEXT: Read the two `_is_shared_existence` strategies, solo discovery, the generalized manifest and the hydrator.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
story = STORY.read_text(encoding="utf-8")
anchor = "## Closure Confirmation"
assert story.count(anchor) == 1
STORY.write_text(story.replace(anchor, NOTE + anchor), encoding="utf-8")
print("noted", NOW)
