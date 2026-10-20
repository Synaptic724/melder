"""S5: record the lowering read (FACT) in the story."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STORY = ROOT / "tickets/stories/2026-10-15_managed_dispense_codegen_story.md"
NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: site_plan_lowering.py read whole on 0.2.8244. `SitePlanLowering.emit` keeps the demanded steps (a parameter
    with a winning key demands nothing, so a managed site feeding an overridden parameter is never emitted) and hands
    them to `SitePlanEmission`, which classifies each step shared or not by one list, `_shared = [existence is not
    many]` - a managed step would fall into "shared" today and hit `_route`'s RuntimeError. `_place` homes the root
    and every shared site with a winning key at top level and every other step at the lowest context common to its
    consumers (a shared consumer's context is its own `_miss{{i}}`), then computes each miss's outer values.
    `_emit_context` emits a context's children: shared -> `_emit_shared_hit` (store route or the S9 owner-store
    constant `c{{i}}`, `v = c._creations.get(sid)`, P2 when pinned, `_miss{{i}}` call) and `_emit_miss` (unresolved
    check, children first, then the guard - none for a door-held root - recheck, construction, publication through
    `add_creation` or the dict write, `adopt_children` for its disposal-bearing many children); many ->
    `_emit_many` (construction, then `<store>.register_many(sid, v, dm)` where store is `many_store` at top level
    and `c{{i}}` in a miss). `_emit_construct` emits a direct call wrapped in `try/except Exception ->
    _raise_meld_construction_error`, or the generic helper with a dict literal, or the supplied-values helper on a
    masked copy. Normal mode drops `ov` everywhere; `_owner_store_constant` is the S9 rule (unique, automatic
    owner, owner store set).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:568-728
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:880-958
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1117-1234
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1513
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1516-1666
  IMPACT: The managed site is a third kind beside shared and many: placed like shared (its own miss, so its children
    build only on a miss) with a pop-or-miss hit; its miss reserves, builds children into a local `kids{{i}}` list
    instead of `register_many`, constructs, and `abandon`s on failure / `adopt`s on success; with its own winning keys
    it constructs fresh like a many step. Its consumer's construction (and any lease after the first) needs the F9
    put-back on failure. Every non-managed path stays as emitted today if the new kind only adds branches.
  NEXT: Read creation_runtime_door_compiler.py whole (U7: the hooks lane's `created` flag).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
story = STORY.read_text(encoding="utf-8")
anchor = "## Closure Confirmation"
assert story.count(anchor) == 1
STORY.write_text(story.replace(anchor, NOTE + anchor), encoding="utf-8")
print("noted", NOW)
