"""Existing-object fast path (flag shape): fast-door entries carry an existing-object flag - anchored edits.

Usage: python apply_existing_flag_edits.py <tree_root> [--check]

Entries become `(spell, captured_context, captured_epoch, existing_object_entry)`; the four entry builders set the bool
to `target_spell.user_created_object is not None`. The guard ladder is unchanged. At the call site of the plain arm of
ConduitMeld.meld, SpellSpaceMeld.meld and Conduit.meld a flagged hit takes `door_spell.user_created_object` instead
of calling the existing-creation door (whose whole body is that read); unflagged hits call the executor as before. Override arms unpack and ignore
the flag. Also documents the entry shape (Meld registry docstring, __init__ comment and type, both door docstrings,
Conduit.meld) and adds component tests. Each anchor must match exactly once (either line ending) or nothing is
written. Engine: apply_s3b1_edits.py. Supersedes apply_existing_shortcut_edits.py (slot shape, measured and rejected).
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

CONDUIT = "src/melder/aether/conduit/conduit.py"
CONDUIT_MELD = "src/melder/aether/conduit/meld/conduit_meld.py"
SPACE_MELD = "src/melder/aether/conduit/meld/spellspace_meld.py"
MELD = "src/melder/aether/conduit/meld/meld.py"
TESTS = "tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py"

# ---------------------------------------------------------------- both front doors
PLAIN_UNPACK_OLD = '''                        captured_epoch,
                    ) = fast_entry
                    fast_executor = None
                    try:
                        # Guard ladder (live reads only):
'''
PLAIN_UNPACK_NEW = '''                        captured_epoch,
                        existing_object_entry,
                    ) = fast_entry
                    fast_executor = None
                    try:
                        # Guard ladder (live reads only):
'''

OVERRIDE_UNPACK_OLD = '''                        captured_epoch,
                    ) = fast_entry
                    fast_executor = None
                    try:
                        if (
'''
OVERRIDE_UNPACK_NEW = '''                        captured_epoch,
                        _existing_object_entry,
                    ) = fast_entry
                    fast_executor = None
                    try:
                        if (
'''

FLAG_CALL = '''                        if existing_object_entry:
                            # Existing object (2026-09-26): the door's whole
                            # body is this read, so it is done here without
                            # the door frame (unguarded, as in the door).
                            instance = door_spell.user_created_object
                        else:
                            instance = fast_executor(self)
'''

CM_CALL_OLD = '''                        # Instance-only door: no (instance, created) tuple is
                        # allocated and discarded on the warm fast lane.
                        instance = fast_executor(self)
'''
CM_CALL_NEW = ('''                        # Instance-only door: no (instance, created) tuple is
                        # allocated and discarded on the warm fast lane.
''' + FLAG_CALL)

SM_CALL_OLD = '''                        # Instance-only door: no (instance, created)
                        # tuple on the warm fast lane.
                        instance = fast_executor(self)
'''
SM_CALL_NEW = ('''                        # Instance-only door: no (instance, created)
                        # tuple on the warm fast lane.
''' + FLAG_CALL)

ENTRY_TAIL_NEW = '''                    self._fast_meld_doors[fast_door_key] = (
                        target_spell,
                        creation_context,
                        door_epoch_at_entry,
                        # Existing-object flag (2026-09-26): warm hits of a
                        # flagged entry return the bound object. A bool, not
                        # the object, so a stale entry never keeps it alive.
                        target_spell.user_created_object is not None,
                    )
'''
ENTRY_TAIL_OLD = '''                    self._fast_meld_doors[fast_door_key] = (
                        target_spell,
                        creation_context,
                        door_epoch_at_entry,
                    )
'''
PLAIN_BUILD_OLD = "                    # is the in-place rebuild.\n" + ENTRY_TAIL_OLD
PLAIN_BUILD_NEW = "                    # is the in-place rebuild.\n" + ENTRY_TAIL_NEW
OVERRIDE_BUILD_OLD = "                    # gets an entry, so the plain fast lane cannot skip it.\n" + ENTRY_TAIL_OLD
OVERRIDE_BUILD_NEW = "                    # gets an entry, so the plain fast lane cannot skip it.\n" + ENTRY_TAIL_NEW

ENTRY_DOC_OLD = "memoized `(spell, context, epoch)` entry"
ENTRY_DOC_NEW = "memoized `(spell, context, epoch, existing-object flag)` entry"

DOOR_DOC_OLD = '''              payloads and empty dicts always take the full lane.
'''
DOOR_DOC_NEW = '''              payloads and empty dicts always take the full lane.
            - A warm plain id-string meld of an existing-object spell (entry
              flag set when the entry is built) returns the spell's
              `user_created_object` without calling the existing-creation door
              (2026-09-26); that door returns the same slot, so results are
              identical. Override payloads on an existing object still reach
              the override door and its refusal.
'''

# ---------------------------------------------------------------- Conduit.meld arm
CONDUIT_UNPACK_OLD = '''                    captured_epoch,
                ) = fast_entry
                fast_executor = None
                try:
                    if (
                        not meld_component._meld_hooks
'''
CONDUIT_UNPACK_NEW = '''                    captured_epoch,
                    existing_object_entry,
                ) = fast_entry
                fast_executor = None
                try:
                    if (
                        not meld_component._meld_hooks
'''

CONDUIT_CALL_OLD = '''                if fast_executor is not None:
                    if override is None:
                        instance = fast_executor(meld_component)
'''
CONDUIT_CALL_NEW = '''                if fast_executor is not None:
                    if override is None:
                        if existing_object_entry:
                            # Existing object (2026-09-26): its door's whole body is this
                            # read, so it is done here without the door frame.
                            instance = door_spell.user_created_object
                        else:
                            instance = fast_executor(meld_component)
'''

CONDUIT_DOC_OLD = '''              every fast-door guard holds (2026-09-26); results are identical to
              the door's, and any miss continues in the door's id lane.
'''
CONDUIT_DOC_NEW = '''              every fast-door guard holds (2026-09-26); results are identical to
              the door's, and any miss continues in the door's id lane. A plain
              id meld of an existing-object spell returns its bound object there
              without calling the existing-creation door.
'''

# ---------------------------------------------------------------- Meld registry
MELD_CLASS_DOC_OLD = '''      `(spell, captured_context, captured_epoch)` tuples
      used by the concrete doors' guarded warm fast lane. `captured_epoch`
'''
MELD_CLASS_DOC_NEW = '''      `(spell, captured_context, captured_epoch, existing_object_entry)`
      tuples used by the concrete doors' guarded warm fast lane. `captured_epoch`
'''

MELD_DOC_OLD = '''      live `_overrides_executor` slot instead. Three readers apply one guard
      ladder and must stay identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld`
      and `Conduit.meld` (automatic id melds). Cardinality is bounded by
'''
MELD_DOC_NEW = '''      live `_overrides_executor` slot instead. `existing_object_entry` is
      True when the spell holds a bound object (`user_created_object`); the
      plain arm then returns that object without the door call (2026-09-26),
      since the existing-creation door returns the same slot. The flag keeps
      the check off every other spell's warm path, and it is a bool rather
      than the object so a stale entry never keeps a removed object alive.
      Three readers apply one guard ladder and both arms and must stay
      identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld` and
      `Conduit.meld` (automatic id melds). Cardinality is bounded by
'''

MELD_INIT_OLD = '''        # melds. Entries are (spell, captured_context, creations_store)
        # tuples built by the concrete doors only after one full normal-lane
        # meld succeeded for that spell id, and validated per hit by a live
'''
MELD_INIT_NEW = '''        # melds. Entries are (spell, captured_context, captured_epoch,
        # existing_object_entry) tuples built by the concrete doors only after
        # one full normal-lane meld succeeded for that spell id, and validated
        # per hit by a live
'''
MELD_TYPE_OLD = "            Tuple[Spell, CreationContext, int],\n"
MELD_TYPE_NEW = "            Tuple[Spell, CreationContext, int, bool],\n"

TEST_IMPORT_OLD = '''from melder.aether.spellbook.spellbook import Spellbook
'''
TEST_IMPORT_NEW = '''from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
'''

TEST_TAIL_OLD = '''        with pytest.raises(ValueError, match="not both"):
            conduit.meld(_OverridableService, spell_id=spell_id)
    finally:
        conduit.permanent_cleanup()
'''
TEST_TAIL_NEW = TEST_TAIL_OLD + '''

class _ExistingService:
    """
    Purpose:
        Pre-built object bound as an existing-object spell.
    Contract:
        - Instances are distinguishable by identity; melds return the bound
          object itself.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Create a plain object for binding as an existing creation.
        Returns:
            None.
        """
        self.value = 0


def _bind_existing_and_conjure() -> tuple:
    """
    Purpose:
        Build a non-dynamic conduit with one existing-object spell.
    Contract:
        - The object is bound with `Existence.unique`, as existing-object spells
          require.
    Returns:
        tuple: `(spellbook, spell_id, conduit, existing_object)`.
    """
    spellbook = _make_spellbook()
    existing = _ExistingService()
    spell_id = spellbook.bind(
        spell=existing,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    return spellbook, spell_id, conduit, existing


def _poison_no_override_door(meld_door: object, spell_id: str) -> None:
    """
    Purpose:
        Replace the warm context's no-override slot with a raising stub.
    Contract:
        - Uses the context captured in the door's fast-door entry, so any call
          into the no-override door for this spell raises AssertionError; a
          served meld therefore proves the door was not entered.
    Args:
        meld_door: Meld front door holding the warm entry.
        spell_id: Spell id whose context slot is replaced.
    Returns:
        None.
    """
    context = meld_door._fast_meld_doors[spell_id][1]

    def _door_must_not_run(meld: object) -> object:
        """Fail the test if the existing-object fast lane enters the door."""
        raise AssertionError("existing-object fast lane entered the no-override door")

    context._no_overrides_instance_executor = _door_must_not_run


def test_component_fast_door_existing_object_skips_the_door_on_all_readers() -> None:
    """
    Purpose:
        Verify warm existing-object melds return the bound object without the door.
    Contract:
        - After one cold meld per door, `conduit.meld(spell_id=...)` (Conduit arm),
          `conduit._meld.meld(spell_id)` (ConduitMeld arm) and `space.meld(...)`
          (SpellSpaceMeld arm) return the bound object by identity while the
          context's no-override door raises if entered, and none of them reads
          the normal-lane spell-id pool.
    """
    spellbook, spell_id, conduit, existing = _bind_existing_and_conjure()
    try:
        assert conduit.meld(spell_id=spell_id) is existing
        with conduit.enter_spellspace() as space:
            assert space.meld(spell_id=spell_id) is existing
            assert spell_id in space._meld._fast_meld_doors
            _poison_no_override_door(conduit._meld, spell_id)
            _poison_no_override_door(space._meld, spell_id)
            conduit_spy = _install_lane_spy(conduit._meld)
            space_spy = _install_lane_spy(space._meld)
            assert conduit.meld(spell_id=spell_id) is existing
            assert conduit._meld.meld(spell_id) is existing
            assert space.meld(spell_id=spell_id) is existing
            assert not conduit_spy.normal_lane_entered
            assert not space_spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_existing_object_override_keeps_the_refusal() -> None:
    """
    Purpose:
        Verify an override on a warm existing object is still refused.
    Contract:
        - With a warm entry, a dict override payload raises the existing-object
          MeldExecutionError from the override door; with the entry removed the
          full lane raises the same type and message.
        - Plain melds keep returning the bound object afterwards.
    """
    spellbook, spell_id, conduit, existing = _bind_existing_and_conjure()
    try:
        assert conduit.meld(spell_id=spell_id) is existing
        assert spell_id in conduit._meld._fast_meld_doors
        with pytest.raises(MeldExecutionError, match="already exists") as fast_lane:
            conduit.meld(spell_id=spell_id, override={"value": 1})
        del conduit._meld._fast_meld_doors[spell_id]
        with pytest.raises(MeldExecutionError, match="already exists") as full_lane:
            conduit.meld(spell_id=spell_id, override={"value": 1})
        assert str(fast_lane.value) == str(full_lane.value)
        assert conduit.meld(spell_id=spell_id) is existing
        assert existing.value == 0
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_existing_object_guard_trips_on_spell_hooks() -> None:
    """
    Purpose:
        Verify spell hooks still bypass the existing-object fast lane.
    Contract:
        - After a pre-cast hook attaches, the meld runs the hooks lane (pool
          read), fires the hook and returns the bound object.
        - After the hook detaches and the stale entry is dropped, warm melds are
          served from the fast lane again.
    """
    spellbook, spell_id, conduit, existing = _bind_existing_and_conjure()
    try:
        assert conduit.meld(spell_id=spell_id) is existing
        spy = _install_lane_spy(conduit._meld)
        hook_calls: list[str] = []
        spell = spellbook._spell_id_pool[spell_id]
        spell._set_hooks(pre_hooks=[lambda: hook_calls.append("pre")])
        assert conduit.meld(spell_id=spell_id) is existing
        assert hook_calls == ["pre"]
        assert spy.normal_lane_entered

        spell._set_hooks(pre_hooks=[])
        del conduit._meld._fast_meld_doors[spell_id]
        assert conduit.meld(spell_id=spell_id) is existing
        warm_spy = _install_lane_spy(conduit._meld)
        assert conduit.meld(spell_id=spell_id) is existing
        assert not warm_spy.normal_lane_entered
        assert hook_calls == ["pre"]
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_existing_object_removed_spell_fails_like_the_full_lane() -> None:
    """
    Purpose:
        Verify a removed existing-object spell is never served from a stale entry.
    Contract:
        - After `cleanup_and_remove_spell`, a meld with the old entry still in
          the registry raises the same exception type and message as the full
          lane with the entry removed; the bound object is not returned.
    """
    spellbook, spell_id, conduit, existing = _bind_existing_and_conjure()
    try:
        assert conduit.meld(spell_id=spell_id) is existing
        assert spell_id in conduit._meld._fast_meld_doors
        spellbook.cleanup_and_remove_spell(spell_id)
        with pytest.raises(Exception) as stale_entry:
            conduit.meld(spell_id=spell_id)
        conduit._meld._fast_meld_doors.pop(spell_id, None)
        with pytest.raises(Exception) as full_lane:
            conduit.meld(spell_id=spell_id)
        assert type(stale_entry.value) is type(full_lane.value)
        assert str(stale_entry.value) == str(full_lane.value)
    finally:
        conduit.permanent_cleanup()
'''

EDITS = {
    CONDUIT_MELD: [
        ("replace", PLAIN_UNPACK_OLD, PLAIN_UNPACK_NEW),
        ("replace", OVERRIDE_UNPACK_OLD, OVERRIDE_UNPACK_NEW),
        ("replace", CM_CALL_OLD, CM_CALL_NEW),
        ("replace", PLAIN_BUILD_OLD, PLAIN_BUILD_NEW),
        ("replace", OVERRIDE_BUILD_OLD, OVERRIDE_BUILD_NEW),
        ("replace", ENTRY_DOC_OLD, ENTRY_DOC_NEW),
        ("replace", DOOR_DOC_OLD, DOOR_DOC_NEW),
    ],
    SPACE_MELD: [
        ("replace", PLAIN_UNPACK_OLD, PLAIN_UNPACK_NEW),
        ("replace", OVERRIDE_UNPACK_OLD, OVERRIDE_UNPACK_NEW),
        ("replace", SM_CALL_OLD, SM_CALL_NEW),
        ("replace", PLAIN_BUILD_OLD, PLAIN_BUILD_NEW),
        ("replace", OVERRIDE_BUILD_OLD, OVERRIDE_BUILD_NEW),
        ("replace", ENTRY_DOC_OLD, ENTRY_DOC_NEW),
        ("replace", DOOR_DOC_OLD, DOOR_DOC_NEW),
    ],
    CONDUIT: [
        ("replace", CONDUIT_UNPACK_OLD, CONDUIT_UNPACK_NEW),
        ("replace", CONDUIT_CALL_OLD, CONDUIT_CALL_NEW),
        ("replace", CONDUIT_DOC_OLD, CONDUIT_DOC_NEW),
    ],
    MELD: [
        ("replace", MELD_CLASS_DOC_OLD, MELD_CLASS_DOC_NEW),
        ("replace", MELD_DOC_OLD, MELD_DOC_NEW),
        ("replace", MELD_INIT_OLD, MELD_INIT_NEW),
        ("replace", MELD_TYPE_OLD, MELD_TYPE_NEW),
    ],
    TESTS: [
        ("replace", TEST_IMPORT_OLD, TEST_IMPORT_NEW),
        ("replace", TEST_TAIL_OLD, TEST_TAIL_NEW),
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
