"""S6: align the architecture patch, link the S6 patch docs (story, artifact board) and add the mapping note.

Run from the repository root: python s6_patch_links_mapping.py <NOW>
"""
import pathlib
import sys

NOW = sys.argv[1]
ROOT = pathlib.Path("context_compass")
PATCH_DIR = "system_docs/patches/active/managed_spell_quantity_2026_10_15"
ARCH = ROOT / PATCH_DIR / "architecture_patch.md"
STORY = ROOT / "tickets/stories/2026-10-15_managed_ownership_transfer_story.md"
BOARD = ROOT / "artifact_board.md"
EPIC_TICKET = "tickets/epics/2026-10-14_managed_spell_quantity_epic.md"
T = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"


def replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, (old[:60], text.count(old))
    return text.replace(old, new, 1)


arch = ARCH.read_text(encoding="utf-8")
arch = replace_once(
    arch,
    "| TransferOfOwnership | pools move as rows; no-move keeps the old pool for rollback only | S6 |",
    "| TransferOfOwnership, Creations | pools move as rows; no-move keeps the old pool for rollback only; the owner stamp"
    " follows the lineage (stamped parked members re-stamped; a rollback stamps back and discards a pool a stamp"
    " composed, `discard_managed_quantity`) | S6 |",
)
arch = replace_once(
    arch,
    "8. An ownership transfer disposes nothing: moving carries the same pool object with its idle objects, children and\n"
    "   count; not moving keeps the old pool only for rollback; rollback restores it.",
    "8. An ownership transfer disposes nothing: moving carries the same pool object with its idle objects, children and\n"
    "   count; not moving keeps the old pool only for rollback; rollback restores it. The owner stamp follows the\n"
    "   lineage: every member that carries one names the target's store after the transfer and its old store after a\n"
    "   failed one, and a pool a stamp composed is discarded by the rollback (S6).",
)
arch = replace_once(
    arch,
    "- Internal: `Creations._managed_quantities`, `Creations.ensure_managed_quantity`, the `managed` extract row; the",
    "- Internal: `Creations._managed_quantities`, `Creations.ensure_managed_quantity`,\n"
    "  `Creations.discard_managed_quantity` (S6), the `managed` extract row; the",
)
arch = replace_once(
    arch,
    "| 8 | S6 unit and integration: move, no move, rollback, parked members, releases after the move |",
    "| 8 | S6 unit and integration: move, no move, rollback, parked members, owner stamps both ways, releases after the"
    " move |",
)
ARCH.write_text(arch, encoding="utf-8")

story = STORY.read_text(encoding="utf-8")
story = replace_once(
    story,
    "  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_ownership_transfer.md\n",
    "  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_ownership_transfer.md\n"
    "  - system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_ownership_transfer.md\n",
)
story = replace_once(
    story,
    "- [ ] Component patch and mapping note.",
    "- [x] Component patch and mapping note.",
)
MAPPING = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Entry gate met: the component and code-description patches are written and linked (architecture patch
    aligned: the TransferOfOwnership row, invariant 8, the interface deltas, coverage row 8). Mapping, patch section ->
    implementation -> validation:
    (1) component After 1 (the flip's stamp) -> `_stamp_owner`, `_restamp`, `_discard_composed_pool`; the flip's
    direct `_add_owned_conduit` call becomes `self._restamp(spell_obj)` -> unit: stamp-back registered before the
    stamp, discard registered only for a managed version whose pool the stamp composed; integration D, E, F.
    (2) component After 2 (parked members) -> `_migrate_inactive_members` calls `_restamp` for each moved member with
    `_owner_creations` set, after its map rollback -> unit: stamped re-stamped, unstamped skipped, rollback stamps
    back; integration B, G.
    (3) interface delta (discard) -> `Creations.discard_managed_quantity(spell_id, pool)` -> unit: identity,
    unregister, cleaned store, maps untouched, second call, concurrent calls.
    (4) code-description Rollback (order) -> no extra code (registration order) -> unit: the reverse-order trace;
    integration D, E.
    (5) state delta (no-move parked pools) -> behaviour as documented -> integration: no move with a parked managed
    version notched in: lease from the target's pool, release by class ambiguous, `conduit=` works.
    (6) validation -> the transfer suites (unit, component, integration) and the whole tree, both GIL modes.
  EVIDENCE:
  - context_compass/{PATCH_DIR}/component_patch_managed_ownership_transfer.md:1-80
  - context_compass/{PATCH_DIR}/code_description_patch_managed_ownership_transfer.md:1-53
  - context_compass/{PATCH_DIR}/architecture_patch.md:1-112
  - {T}:1383-1665
  IMPACT: Every src edit of S6 maps to a patch section and a test; nothing in rows, locks or public surface changes.
  NEXT: Red tests: the unit file beside test_transfer_of_ownership.py, the discard tests, the integration file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""
story = replace_once(story, "\n## Closure Confirmation", "\n" + MAPPING + "\n## Closure Confirmation")
story = replace_once(
    story,
    "- Next: the S6 component and code-description patches and the mapping note, then red tests.",
    "- Next: red tests (unit beside test_transfer_of_ownership.py, the discard tests, the integration file).",
)
story = replace_once(
    story,
    "\n- Updated: ",
    "\n- Updated: " + NOW + "\n- Updated-was: ",
)
lines = story.split("\n")
lines = [ln for ln in lines if not ln.startswith("- Updated-was: ")]
story = "\n".join(lines)
STORY.write_text(story, encoding="utf-8")

board = BOARD.read_text(encoding="utf-8")
anchor = "<!-- END USER-DEFINED: active_artifacts -->"
rows = (
    f"| {EPIC_TICKET} | {PATCH_DIR}/component_patch_managed_ownership_transfer.md | patch_doc | active |"
    f" promote_to_documentation | S6 (in progress): the owner stamp follows the lineage - the flip's stamp-back,"
    f" stamped parked members re-stamped, composed pools discarded on rollback, `discard_managed_quantity`; promote"
    f" at S7. | {NOW} | REQUIRED |\n"
    f"| {EPIC_TICKET} | {PATCH_DIR}/code_description_patch_managed_ownership_transfer.md | patch_doc | active |"
    f" promote_to_documentation | S6 (in progress): execute's stamps, the rollback order, the discard's identity"
    f" check and edge semantics; promote at S7. | {NOW} | REQUIRED |\n"
)
board = replace_once(board, anchor, rows + anchor)
BOARD.write_text(board, encoding="utf-8")
print("ok")
