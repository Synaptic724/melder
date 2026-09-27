"""Existing-object shortcut: the three warm-lane readers return `user_created_object` - anchored edits.

Usage: python apply_existing_shortcut_edits.py <tree_root> [--check]

In the plain arm of ConduitMeld.meld, SpellSpaceMeld.meld and Conduit.meld, after the unchanged guards, an
existing-object spell's `user_created_object` is returned without calling the existing-creation door (which
returns that same slot). Documents it in the three docstrings and the Meld registry docstring, and adds
component tests. Each anchor must match exactly once (either line ending) or nothing is written.
Engine: apply_s3b1_edits.py.
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

# ---------------------------------------------------------------- door front doors (plain arm)
DOOR_INIT_OLD = '''                    fast_executor = None
                    try:
                        # Guard ladder (live reads only):
'''
DOOR_INIT_NEW = '''                    existing_instance = None
                    fast_executor = None
                    try:
                        # Guard ladder (live reads only):
'''

EXISTING_COMMENT = '''                            # Existing objects (2026-09-26): the existing-
                            # creation door only returns this spell's
                            # `user_created_object` (set once at bind, deleted
                            # at spell cleanup, which the guards above already
                            # miss on), so the slot is returned here and the
                            # door call is skipped. Other spells hold None and
                            # take their executor.
                            existing_instance = door_spell.user_created_object
                            if existing_instance is None:
'''

EXISTING_RETURN = '''                    if existing_instance is not None:
                        if self._spellbook._cache_emit_required:
                            self._spellbook._emit_cache_file_if_required()
                        return existing_instance
'''

CM_ARM_OLD = '''                            # a captured reference would pin the cold-door
                            # wrapper forever.
                            fast_executor = (
                                captured_context
                                ._no_overrides_instance_executor
                            )
                    except AttributeError:
                        # Lifecycle-ambiguous read: a cleaned spell/switch/
                        # context has deleted slots. Treat as a guard miss so
                        # the normal lane produces the canonical error or
                        # rebuilds.
                        fast_executor = None
                    if fast_executor is not None:
'''
CM_ARM_NEW = ('''                            # a captured reference would pin the cold-door
                            # wrapper forever.
''' + EXISTING_COMMENT + '''                                fast_executor = (
                                    captured_context
                                    ._no_overrides_instance_executor
                                )
                    except AttributeError:
                        # Lifecycle-ambiguous read: a cleaned spell/switch/
                        # context has deleted slots. Treat as a guard miss so
                        # the normal lane produces the canonical error or
                        # rebuilds.
                        fast_executor = None
''' + EXISTING_RETURN + '''                    if fast_executor is not None:
''')

SM_ARM_OLD = '''                            # a captured reference would pin the cold-door
                            # wrapper forever.
                            fast_executor = (
                                captured_context._no_overrides_instance_executor
                            )
                    except AttributeError:
                        # Lifecycle-ambiguous read: a cleaned spell/switch/
                        # context has deleted slots. Treat as a guard miss so
                        # the normal lane produces the canonical error or
                        # rebuilds.
                        fast_executor = None
                    if fast_executor is not None:
'''
SM_ARM_NEW = ('''                            # a captured reference would pin the cold-door
                            # wrapper forever.
''' + EXISTING_COMMENT + '''                                fast_executor = (
                                    captured_context._no_overrides_instance_executor
                                )
                    except AttributeError:
                        # Lifecycle-ambiguous read: a cleaned spell/switch/
                        # context has deleted slots. Treat as a guard miss so
                        # the normal lane produces the canonical error or
                        # rebuilds.
                        fast_executor = None
''' + EXISTING_RETURN + '''                    if fast_executor is not None:
''')

DOOR_DOC_OLD = '''              payloads and empty dicts always take the full lane.
'''
DOOR_DOC_NEW = '''              payloads and empty dicts always take the full lane.
            - A warm plain id-string meld of an existing-object spell returns
              the spell's `user_created_object` from the fast lane without
              calling the existing-creation door (2026-09-26); that door
              returns the same slot, so results are identical. Override
              payloads on an existing object still reach the override door
              and its refusal.
'''

# ---------------------------------------------------------------- Conduit.meld arm
CONDUIT_ARM_OLD = '''                fast_executor = None
                try:
                    if (
                        not meld_component._meld_hooks
                        and door_spell._door_epoch == captured_epoch
                        and door_spell._creation_context is captured_context
                        and not meld_component._spellbook._spellbook_validation_required
                    ):
                        # Slots are read per hit: hydration swaps them in place.
                        if override is None:
                            fast_executor = captured_context._no_overrides_instance_executor
                        elif type(override) is dict and override:
                            fast_executor = captured_context._overrides_executor
                except AttributeError:
                    # Cleaned spell/context: guard miss; the door decides.
                    fast_executor = None
                if fast_executor is not None:
'''
CONDUIT_ARM_NEW = '''                existing_instance = None
                fast_executor = None
                try:
                    if (
                        not meld_component._meld_hooks
                        and door_spell._door_epoch == captured_epoch
                        and door_spell._creation_context is captured_context
                        and not meld_component._spellbook._spellbook_validation_required
                    ):
                        # Slots are read per hit: hydration swaps them in place. An existing
                        # object is returned from its slot without the door call (the
                        # existing-creation door returns that same slot; 2026-09-26).
                        if override is None:
                            existing_instance = door_spell.user_created_object
                            if existing_instance is None:
                                fast_executor = captured_context._no_overrides_instance_executor
                        elif type(override) is dict and override:
                            fast_executor = captured_context._overrides_executor
                except AttributeError:
                    # Cleaned spell/context: guard miss; the door decides.
                    fast_executor = None
                if existing_instance is not None:
                    spellbook = meld_component._spellbook
                    if spellbook._cache_emit_required:
                        spellbook._emit_cache_file_if_required()
                    return existing_instance
                if fast_executor is not None:
'''

CONDUIT_DOC_OLD = '''              every fast-door guard holds (2026-09-26); results are identical to
              the door's, and any miss continues in the door's id lane.
'''
CONDUIT_DOC_NEW = '''              every fast-door guard holds (2026-09-26); results are identical to
              the door's, and any miss continues in the door's id lane. A plain
              id meld of an existing-object spell returns its bound object there
              without calling the existing-creation door.
'''

MELD_DOC_OLD = '''      live `_overrides_executor` slot instead. Three readers apply one guard
      ladder and must stay identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld`
      and `Conduit.meld` (automatic id melds). Cardinality is bounded by
'''
MELD_DOC_NEW = '''      live `_overrides_executor` slot instead. The plain arm returns an
      existing-object spell's `user_created_object` without the door call
      (2026-09-26): its existing-creation door returns that same slot.
      Three readers apply one guard ladder and both arms and must stay
      identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld` and
      `Conduit.meld` (automatic id melds). Cardinality is bounded by
'''

# ---------------------------------------------------------------- tests
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
        ("replace", DOOR_INIT_OLD, DOOR_INIT_NEW),
        ("replace", CM_ARM_OLD, CM_ARM_NEW),
        ("replace", DOOR_DOC_OLD, DOOR_DOC_NEW),
    ],
    SPACE_MELD: [
        ("replace", DOOR_INIT_OLD, DOOR_INIT_NEW),
        ("replace", SM_ARM_OLD, SM_ARM_NEW),
        ("replace", DOOR_DOC_OLD, DOOR_DOC_NEW),
    ],
    CONDUIT: [
        ("replace", CONDUIT_ARM_OLD, CONDUIT_ARM_NEW),
        ("replace", CONDUIT_DOC_OLD, CONDUIT_DOC_NEW),
    ],
    MELD: [("replace", MELD_DOC_OLD, MELD_DOC_NEW)],
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
