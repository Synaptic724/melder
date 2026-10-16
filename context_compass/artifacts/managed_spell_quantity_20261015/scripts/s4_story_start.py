"""S4 start: the story goes in_progress, its boundary names every file the registry touches, and the U11 reads
are recorded. Every anchor must match exactly once or nothing is written."""
import pathlib
import sys

NOW = sys.argv[1]
STORY = pathlib.Path("tickets/stories/2026-10-15_release_managed_spell_story.md")
text = STORY.read_text(encoding="utf-8")

REPLACEMENTS = [
    ("- Status: ready\n", "- Status: in_progress\n"),
    ("- Updated: 2026-10-15T09:29:51Z\n", f"- Updated: {NOW}\n"),
    (
        '''- EXECUTION_BOUNDARY: src/melder/aether/conduit/creations/release_managed_spell.py (new),
  src/melder/aether/conduit/creations/managed_spell_lease.py (new), src/melder/aether/conduit/creations/creations.py
  (register on take, unregister on give-up), src/melder/__init__.py (exports and its workflow map); their tests.
''',
        '''- EXECUTION_BOUNDARY: src/melder/aether/conduit/creations/release_managed_spell.py (new),
  src/melder/aether/conduit/creations/managed_spell_lease.py (new), src/melder/aether/conduit/creations/creations.py
  (register on take, unregister on give-up), src/melder/aether/aether.py (constructs, owns and cleans the
  singleton), src/melder/aether/conduit/creations/managed_spell_quantity.py (`managed_class`),
  src/melder/aether/spellbook/bind/spell_index.py (a cleanup-safe selected-version probe for the resolver),
  src/melder/__init__.py (exports and its workflow map); their tests, tests/unit/melder/test_package_public_surface.py.
''',
    ),
    (
        '''- from_state: draft
- to_state: ready
- transition_reason: ready once S3 lands.
''',
        f'''- from_state: ready
- to_state: in_progress
- transition_reason: S3 landed and closed (0.2.8243, {NOW[:10]}); S4 starts with U11.
''',
    ),
    (
        '''  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md
''',
        '''  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_release_managed_spell.md
''',
    ),
]

NOTE_ANCHOR = '''  IMPACT: Fixes the registry shape before S3's Creations hooks.
  NEXT: Start after S3 closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
'''
NOTE = NOTE_ANCHOR + f'''
- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U11 read in source on 0.2.8243. Aether is a class-level double-checked singleton (`_instance`, a class
    `_lock`, `_initialized`); `__init__` builds the hosted roots once under that lock in a fixed order - Crystallizer,
    AetherUtilitySystem, LoadGate, the aetheric Mediator, MutationResearch, Nexus - and rolls its bookkeeping back on
    failure; `cleanup()` tears down the gate, the plane, the frames, then Crystallizer, MutationResearch, the
    configuration, Nexus and the utility system, and resets `_instance`/`_initialized` in a `finally`. Each hosted root
    repeats the shape: `_instance`, a class lock (`_singleton_lock` or `_lock`), `_initialized`, a once-only `__init__`
    under it, a `cleanup()` that resets the singleton bookkeeping at its end, and a classmethod
    `_reset_singleton_for_tests()` that cleans the instance (tolerating a half-built husk) and clears the bookkeeping
    in a `finally`. Nexus refuses a first construction without its host (`ValueError`, bookkeeping reset); Aether
    passes `aether=self`. Fixtures reset Aether, whose cleanup cleans what it hosts. Also read: the resolver's inputs -
    `Spell._spell_index_unless_cleaned`, `SpellIndex.selected_spell_id` (a lock-free read of a field `cleanup` deletes,
    so a racing cleanup surfaces AttributeError), the root id a lesser carries (`Conduit._root_conduit_id`, the root's
    own id on a root), and the package root (a deliberate flat facade by owner ruling 2026-07-19; the no-export-wiring
    law holds below it).
  EVIDENCE:
  - src/melder/aether/aether.py:116-390
  - src/melder/aether/aether_utility_system.py:63-175
  - src/melder/nexus/nexus.py:134-380
  - src/melder/nexus/nexus.py:516-549
  - src/melder/aether/spellbook/spell.py:907-937
  - src/melder/aether/spellbook/bind/spell_index.py:118-165
  - src/melder/aether/spellbook/bind/spell_index.py:323-357
  - src/melder/__init__.py:1-271
  - context_compass/system_docs/patches/active/melder_init_composition_2026_07_19/architecture_patch.md:6-38
  IMPACT: ReleaseManagedSpell copies the hosted-root shape and requires its host on first construction (`aether=`);
    Aether builds it last and cleans it right after the frames, whose stores unregister their pools first. The
    resolver needs a cleanup-safe selected-version probe on SpellIndex. The root exports follow the root ruling
    (user-held surfaces, front-facing enums and user-catchable errors reach it), so the lease joins the three names
    the epic listed.
  NEXT: Write the S4 component and code-description patches and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
'''

for old, new in REPLACEMENTS + [(NOTE_ANCHOR, NOTE)]:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor matched {count} times, nothing written:\n{old[:160]}")
    text = text.replace(old, new)

STORY.write_text(text, encoding="utf-8")
print("story started", NOW)
