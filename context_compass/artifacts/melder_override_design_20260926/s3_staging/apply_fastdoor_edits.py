"""Override melds use the fast meld door (ConduitMeld, SpellSpaceMeld) - anchored edits.

Usage: python apply_fastdoor_edits.py <tree_root> [--check]

A non-empty dict payload on an id-string meld reads the existing fast-door entry through the same guard
ladder and calls the live override door; the full lane's override branch also builds the entry. Each anchor
must match exactly once (either line ending) or nothing is written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

MELD_DIR = "src/melder/aether/conduit/meld/"


def _override_arm(fast_comment: str) -> str:
    """Return the fast-lane source for an id-string meld with a non-empty dict payload."""
    return (
        fast_comment
        + "            elif type(spell_override) is dict and spell_override:\n"
        "                # Override fast lane (2026-09-26): a non-empty dict payload\n"
        "                # rides the same entry and guard ladder as the plain lane\n"
        "                # above and calls the live override door. The full lane's\n"
        "                # normalization returns such payloads as-is, and every gate\n"
        "                # it would run is immutable per version or covered by these\n"
        "                # guards (see `Meld._fast_meld_doors`). List/tuple payloads\n"
        "                # and empty dicts need normalization: full lane.\n"
        "                fast_entry = self._fast_meld_doors.get(spell)\n"
        "                if fast_entry is not None:\n"
        "                    (\n"
        "                        door_spell,\n"
        "                        captured_context,\n"
        "                        captured_epoch,\n"
        "                    ) = fast_entry\n"
        "                    fast_executor = None\n"
        "                    try:\n"
        "                        if (\n"
        "                            not self._meld_hooks\n"
        "                            and door_spell._door_epoch == captured_epoch\n"
        "                            and door_spell._creation_context is captured_context\n"
        "                            and not self._spellbook._spellbook_validation_required\n"
        "                        ):\n"
        "                            # Read per hit: hydration swaps the slot in place.\n"
        "                            fast_executor = captured_context._overrides_executor\n"
        "                    except AttributeError:\n"
        "                        # Cleaned spell/context: guard miss; the full lane\n"
        "                        # produces the canonical error or rebuilds.\n"
        "                        fast_executor = None\n"
        "                    if fast_executor is not None:\n"
        "                        instance = fast_executor(self, spell_override)[0]\n"
        "                        if self._spellbook._cache_emit_required:\n"
        "                            self._spellbook._emit_cache_file_if_required()\n"
        "                        return instance\n"
        "            fast_door_key = spell\n"
    )


OVERRIDE_BRANCH_OLD = (
    "            else:\n"
    "                instance = creation_context._overrides_executor(\n"
    "                    self,\n"
    "                    override_map,\n"
    "                )[0]\n"
    "            # Hot path: inline the staged-cache flag check; the emit helper is\n"
)
OVERRIDE_BRANCH_NEW = (
    "            else:\n"
    "                instance = creation_context._overrides_executor(\n"
    "                    self,\n"
    "                    override_map,\n"
    "                )[0]\n"
    "                if fast_door_key is not None and target_spell._mutation_override is None:\n"
    "                    # Same posture as the no-override arm (non-dynamic, no\n"
    "                    # hooks, success), so one entry serves both fast arms. A\n"
    "                    # stored mutation override (dynamic spells only) never\n"
    "                    # gets an entry, so the plain fast lane cannot skip it.\n"
    "                    self._fast_meld_doors[fast_door_key] = (\n"
    "                        target_spell,\n"
    "                        creation_context,\n"
    "                        door_epoch_at_entry,\n"
    "                    )\n"
    "            # Hot path: inline the staged-cache flag check; the emit helper is\n"
)

CONDUIT_FAST_END = (
    "                    if fast_executor is not None:\n"
    "                        # Instance-only door: no (instance, created) tuple is\n"
    "                        # allocated and discarded on the warm fast lane.\n"
    "                        instance = fast_executor(self)\n"
    "                        if self._spellbook._cache_emit_required:\n"
    "                            self._spellbook._emit_cache_file_if_required()\n"
    "                        return instance\n"
)
SPACE_FAST_END = (
    "                    if fast_executor is not None:\n"
    "                        # Instance-only door: no (instance, created)\n"
    "                        # tuple on the warm fast lane.\n"
    "                        instance = fast_executor(self)\n"
    "                        if self._spellbook._cache_emit_required:\n"
    "                            self._spellbook._emit_cache_file_if_required()\n"
    "                        return instance\n"
)
DOC_SPACE_OLD = (
    "              doors are always honored. Any guard miss falls back to this\n"
    "              normal lane and rebuilds the entry on success, so fast-lane\n"
    "              results are always identical to normal-lane results.\n"
)
DOC_SPACE_NEW = DOC_SPACE_OLD + (
    "            - An id-string meld with a non-empty dict override payload uses\n"
    "              the same entry and guards and calls the live override door\n"
    "              (2026-09-26); the full lane's override branch also builds the\n"
    "              entry when the spell holds no mutation override. List/tuple\n"
    "              payloads and empty dicts always take the full lane.\n"
)

EDITS = {
    MELD_DIR + "conduit_meld.py": [
        ("replace", CONDUIT_FAST_END + "            fast_door_key = spell\n", _override_arm(CONDUIT_FAST_END)),
        ("replace", OVERRIDE_BRANCH_OLD, OVERRIDE_BRANCH_NEW),
        ("replace", DOC_SPACE_OLD, DOC_SPACE_NEW),
    ],
    MELD_DIR + "spellspace_meld.py": [
        ("replace", SPACE_FAST_END + "            fast_door_key = spell\n", _override_arm(SPACE_FAST_END)),
        ("replace", OVERRIDE_BRANCH_OLD, OVERRIDE_BRANCH_NEW),
        ("replace", DOC_SPACE_OLD, DOC_SPACE_NEW),
    ],
    MELD_DIR + "meld.py": [
        ("replace",
         "      first execution. Cardinality is bounded by construction because\n"
         "      entries are inserted only after a successful normal-lane meld, so the\n"
         "      keyspace is the bound-spell registry, not caller input. The registry\n"
         "      is deleted in `cleanup()`.\n",
         "      first execution. The override arm (2026-09-26) reads the same entry\n"
         "      for an id-string meld with a non-empty dict payload and calls the\n"
         "      live `_overrides_executor` slot instead. Cardinality is bounded by\n"
         "      construction because entries are inserted only after a successful\n"
         "      full-lane meld (no-override or override branch, never for a spell\n"
         "      holding a mutation override), so the keyspace is the bound-spell\n"
         "      registry, not caller input. The registry is deleted in `cleanup()`.\n"),
    ],
}


def main() -> None:
    """Check every edit, then write (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        data = (root / rel).read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[root / rel] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
