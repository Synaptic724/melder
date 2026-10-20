"""S4 patch gate: the mapping note on the story and the two patch-doc rows on the artifact board."""
import pathlib
import sys

NOW = sys.argv[1]


def apply(path: pathlib.Path, replacements: list) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path}: anchor matched {count} times, nothing written:\n{old[:200]}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print("updated", path)


STORY_ANCHOR = '''  NEXT: Write the S4 component and code-description patches and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
'''
STORY_NOTE = STORY_ANCHOR + f'''
- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch-section -> implementation -> validation mapping (read after the architecture patch). Singleton shape
    -> `ReleaseManagedSpell.__new__` / `__init__(aether=)` / `cleanup` / `_reset_singleton_for_tests` /
    `_live_instance`, built last in `Aether.__init__` and cleaned after the frames -> unit: one instance, the Aether
    owns it, a bare first construction is refused, cleanup and reset clear it, a cleaned registry refuses. Registry
    state and register/unregister -> copy-on-write maps under the leaf lock -> unit: idempotent, re-key on a changed
    class, holding root on restore, unregister after cleanup does nothing. release / the cold resolver / managed /
    release_all / describe -> unit: the fast path and every branch and text. The lease -> `ManagedSpellLease` ->
    test_managed_spell_lease.py. Creations hooks -> ensure registers, extract and cleanup unregister, restore swaps ->
    Creations unit tests. `managed_class` and `SpellIndex._is_selected_unless_cleaned` -> unit. Root exports ->
    `melder/__init__.py` -> the public-surface suite. Concurrency -> a multithreaded file. Integration -> a real
    Spellbook (conjure and post-conjure bind register, teardown empties the registry, releases by class, spell id and
    conduit). A routing-cost probe. Red first, both GIL modes.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:1-106
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md:1-82
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_release_managed_spell.md:1-46
  IMPACT: The S4 patch gate is met: both patches exist, are linked, and every section maps to code and a test.
  NEXT: Write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
'''

ARTIFACT_ANCHOR = "<!-- END USER-DEFINED: active_artifacts -->\n"
ARTIFACT_ROWS = (
    "| tickets/stories/2026-10-15_release_managed_spell_story.md | system_docs/patches/active/"
    "managed_spell_quantity_2026_10_15/component_patch_release_managed_spell.md | patch_doc | active | "
    "promote_to_documentation | S4: the ReleaseManagedSpell singleton (Aether-owned), register/unregister following "
    "the stores, release and its resolver, managed, release_all, describe, the lease, the root exports. | "
    f"{NOW} | REQUIRED |\n"
    "| tickets/stories/2026-10-15_release_managed_spell_story.md | system_docs/patches/active/"
    "managed_spell_quantity_2026_10_15/code_description_patch_release_managed_spell.md | patch_doc | active | "
    "promote_to_documentation | S4: the registry's state, publication protocol, control flow, edge semantics and "
    f"invariants. | {NOW} | REQUIRED |\n"
    + ARTIFACT_ANCHOR
)

apply(pathlib.Path("tickets/stories/2026-10-15_release_managed_spell_story.md"), [(STORY_ANCHOR, STORY_NOTE)])
apply(pathlib.Path("artifact_board.md"), [(ARTIFACT_ANCHOR, ARTIFACT_ROWS)])
