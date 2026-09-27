"""Public meld trim: Conduit.meld reads the meld door's fast entry for automatic id melds - anchored edits.

Usage: python apply_conduit_trim_edits.py <tree_root> [--check]

Also documents the three fast-door readers (Meld registry docstring) and adds component tests. Each anchor
must match exactly once (either line ending) or nothing is written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

CONDUIT = "src/melder/aether/conduit/conduit.py"
MELD = "src/melder/aether/conduit/meld/meld.py"
TESTS = "tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py"

BODY_OLD = '''        self.check_cleaned()

        meld_component = self._meld
        if spell is not None and spell_id is not None:
            raise ValueError("meld accepts either `spell` or `spell_id`, not both.")
'''

BODY_NEW = '''        if self._cleaned:
            self.check_cleaned()

        meld_component = self._meld
        # Warm automatic id lane (2026-09-26): the dominant call - an id meld on an automatic
        # conduit - reads the meld door's fast-door entry here, saving the door frame and keyword
        # marshaling on a hit (solo meld 209 -> 111 ns on 3.14t). The guard ladder and both arms
        # mirror `ConduitMeld.meld` exactly (`Meld._fast_meld_doors` lists every reader); only
        # guard reads sit inside the AttributeError try, so a constructor's own AttributeError is
        # never swallowed. A miss continues in the door's positional id lane; every other call
        # shape keeps the path below.
        if (
            type(spell_id) is str
            and spell is None
            and spellframe is None
            and binding_name is None
            and not self.__dynamic_environment__
        ):
            fast_entry = meld_component._fast_meld_doors.get(spell_id)
            if fast_entry is not None:
                (
                    door_spell,
                    captured_context,
                    captured_epoch,
                ) = fast_entry
                fast_executor = None
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
                    if override is None:
                        instance = fast_executor(meld_component)
                    else:
                        instance = fast_executor(meld_component, override)[0]
                    spellbook = meld_component._spellbook
                    if spellbook._cache_emit_required:
                        spellbook._emit_cache_file_if_required()
                    return instance
            if override is None:
                return meld_component.meld(spell_id)
            return meld_component.meld(spell_id, spell_override=override)

        if spell is not None and spell_id is not None:
            raise ValueError("meld accepts either `spell` or `spell_id`, not both.")
'''

DOC_OLD = '''            - `spell_id=` is forwarded directly into the internal positional ID
              fast lane and never enters human-name normalization.
'''
DOC_NEW = DOC_OLD + '''            - On an automatic conduit an id meld (plain, or with a non-empty dict
              override) is served here from the meld door's fast-door entry when
              every fast-door guard holds (2026-09-26); results are identical to
              the door's, and any miss continues in the door's id lane.
'''

MELD_DOC_OLD = "      live `_overrides_executor` slot instead. Cardinality is bounded by\n"
MELD_DOC_NEW = (
    "      live `_overrides_executor` slot instead. Three readers apply one guard\n"
    "      ladder and must stay identical: `ConduitMeld.meld`, `SpellSpaceMeld.meld`\n"
    "      and `Conduit.meld` (automatic id melds). Cardinality is bounded by\n"
)

TEST_TAIL_OLD = '''        spy = _install_lane_spy(space._meld)
            assert space.meld(spell_id=spell_id, override={"value": 6}).value == 6
            assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()
'''
TEST_TAIL_NEW = TEST_TAIL_OLD + '''

def test_component_conduit_and_door_fast_arms_serve_the_same_results() -> None:
    """
    Purpose:
        Verify the Conduit-level id lane and the meld door's fast arm agree.
    Contract:
        - Plain and dict-override melds through `conduit.meld(spell_id=...)`
          (Conduit arm) and `conduit._meld.meld(spell_id, ...)` (door arm) are
          both served without the normal-lane pool read.
        - `unique` reuse returns the one stored instance on both; override
          payloads apply on both.
    """
    spellbook = _make_spellbook()
    unique_id = spellbook.bind(
        spell=_SharedUniqueService,
        existence=Existence.unique,
        permissions="create",
    )
    override_id = spellbook.bind(
        spell=_OverridableService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        stored = conduit.meld(spell_id=unique_id)
        conduit.meld(spell_id=override_id)
        spy = _install_lane_spy(conduit._meld)
        assert conduit.meld(spell_id=unique_id) is stored
        assert conduit._meld.meld(unique_id) is stored
        assert conduit.meld(spell_id=override_id, override={"value": 8}).value == 8
        assert conduit._meld.meld(override_id, spell_override={"value": 9}).value == 9
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_conduit_id_meld_raises_canonical_error_after_cleanup() -> None:
    """
    Purpose:
        Verify the cleaned-conduit guard on the keyword id call shape.
    Contract:
        - `meld(spell_id=...)`, plain or with an override, on a cleaned conduit
          raises the canonical `check_cleaned` RuntimeError.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_OverridableService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    conduit.meld(spell_id=spell_id)
    conduit.permanent_cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        conduit.meld(spell_id=spell_id)
    with pytest.raises(RuntimeError, match="cleaned"):
        conduit.meld(spell_id=spell_id, override={"value": 1})


def test_component_conduit_id_meld_rejects_spell_and_spell_id_together() -> None:
    """
    Purpose:
        Verify the Conduit-level lane leaves the mutual-exclusion check intact.
    Contract:
        - Passing both `spell` and `spell_id` still raises ValueError, even with a
          warm fast-door entry.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_OverridableService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        conduit.meld(spell_id=spell_id)
        with pytest.raises(ValueError, match="not both"):
            conduit.meld(_OverridableService, spell_id=spell_id)
    finally:
        conduit.permanent_cleanup()
'''

FACADE = "tests/unit/melder/aether/conduit/test_conduit_facade.py"
NO_ENTRY = (
    "    # The mock door has no warm fast-door entry, so the automatic id lane calls it.\n"
    "    conduit_lesser._meld._fast_meld_doors = {}\n"
)
FACADE_EDITS = [
    ("replace",
     "        - `spell_id=` becomes the internal positional spell value.\n",
     "        - `spell_id=` becomes the internal positional spell value; with no warm\n"
     "          fast-door entry the automatic id lane calls the door positionally\n"
     "          (2026-09-26), with no keyword marshaling.\n"),
    ("replace",
     '    conduit_lesser._meld = MagicMock()\n'
     '    conduit_lesser._meld.meld.return_value = "result"\n'
     '\n'
     '    result = conduit_lesser.meld(spell_id="sha-1")\n'
     '\n'
     '    assert result == "result"\n'
     '    conduit_lesser._meld.meld.assert_called_once_with(\n'
     '        "sha-1",\n'
     '        spell_name=None,\n'
     '        spellframe=None,\n'
     '        binding_name=None,\n'
     '        spell_override=None,\n'
     '    )\n',
     '    conduit_lesser._meld = MagicMock()\n'
     + NO_ENTRY +
     '    conduit_lesser._meld.meld.return_value = "result"\n'
     '\n'
     '    result = conduit_lesser.meld(spell_id="sha-1")\n'
     '\n'
     '    assert result == "result"\n'
     '    conduit_lesser._meld.meld.assert_called_once_with("sha-1")\n'),
    ("replace",
     '    conduit_lesser._meld = MagicMock()\n'
     '    conduit_lesser._meld.meld.return_value = "result"\n'
     '    conduit_lesser.register_conduit_hooks(\n',
     '    conduit_lesser._meld = MagicMock()\n'
     + NO_ENTRY +
     '    conduit_lesser._meld.meld.return_value = "result"\n'
     '    conduit_lesser.register_conduit_hooks(\n'),
    ("replace",
     '    conduit_lesser._meld = MagicMock()\n'
     '    conduit_lesser._meld.meld.return_value = "result"\n'
     '    conduit_lesser._conduit_hooks = {}\n',
     '    conduit_lesser._meld = MagicMock()\n'
     + NO_ENTRY +
     '    conduit_lesser._meld.meld.return_value = "result"\n'
     '    conduit_lesser._conduit_hooks = {}\n'),
]

EDITS = {
    CONDUIT: [("replace", BODY_OLD, BODY_NEW), ("replace", DOC_OLD, DOC_NEW)],
    MELD: [("replace", MELD_DOC_OLD, MELD_DOC_NEW)],
    TESTS: [("replace", TEST_TAIL_OLD, TEST_TAIL_NEW)],
    FACADE: FACADE_EDITS,
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
