"""Fast-door component tests for the override arm - anchored edits.

Usage: python apply_fastdoor_test_edits.py <tree_root> [--check]

The "skipped for override payloads" test pinned the old contract; it flips to "serves dict payloads". New cases
cover override-only entry building, full-lane payload shapes, guard trips, identical errors on both lanes, a
many_only key-set plan and a spellspace meld. Engine: apply_s3b1_edits.py (either line ending per anchor).
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

TARGET = "tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py"

OLD_TEST = '''def test_component_fast_door_skipped_for_override_payloads() -> None:
    """
    Purpose:
        Verify caller override payloads always take the normal lane.
    Contract:
        - Override melds construct with the override payload applied.
        - A poisoned fast-door entry is not executed by an override meld.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_OverridableService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        plain = conduit.meld(spell_id=spell_id)
        assert plain.value == 0
        assert spell_id in conduit._meld._fast_meld_doors

        spy = _install_lane_spy(conduit._meld)
        overridden = conduit.meld(spell_id=spell_id, override={"value": 7})
        assert overridden.value == 7
        # Override payloads always take the normal lane (the fast lane cannot
        # apply overrides), proven by the spell-id-pool read.
        assert spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()
'''

NEW_TEST = '''def test_component_fast_door_serves_dict_override_payloads() -> None:
    """
    Purpose:
        Verify an id-string meld with a dict override payload is served by the
        fast lane once an entry exists (override arm, 2026-09-26).
    Contract:
        - The override meld applies the payload and returns before the
          normal-lane spell-id-pool read.
        - A later plain meld still rides the plain fast arm with defaults.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_OverridableService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        plain = conduit.meld(spell_id=spell_id)
        assert plain.value == 0
        assert spell_id in conduit._meld._fast_meld_doors

        spy = _install_lane_spy(conduit._meld)
        overridden = conduit.meld(spell_id=spell_id, override={"value": 7})
        assert overridden.value == 7
        # The override arm reads the same entry and returns before the pool read.
        assert not spy.normal_lane_entered
        assert conduit.meld(spell_id=spell_id).value == 0
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()
'''

TAIL_ANCHOR = '''            assert next_space.meld(spell_id=marker_id) is second
    finally:
        conduit.permanent_cleanup()
'''

APPENDED = TAIL_ANCHOR + '''

class _OverrideLeaf:
    """
    Purpose:
        Dependency of `_OverrideRoot` for override fast-lane tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Returns:
            None.
        """
        self.marker = object()


class _OverrideRoot:
    """
    Purpose:
        many_only root whose dependency an override supplies.
    Contract:
        - `leaf` is the injected or supplied `_OverrideLeaf`.
    """

    def __init__(self, leaf: _OverrideLeaf) -> None:
        """
        Purpose:
            Record the dependency for identity assertions.
        Args:
            leaf: Injected or override-supplied leaf.
        Returns:
            None.
        """
        self.leaf = leaf


def _make_overridable_conduit() -> tuple:
    """
    Purpose:
        Build a non-dynamic spellbook with one `many` `_OverridableService`.
    Returns:
        tuple: (spellbook, spell_id, conduit).
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_OverridableService,
        existence=Existence.many,
        permissions="create",
    )
    return spellbook, spell_id, spellbook.conjure(name="root")


def test_component_fast_door_override_only_callers_build_the_entry() -> None:
    """
    Purpose:
        Verify a successful full-lane override meld builds the fast-door entry.
    Contract:
        - The first override meld runs the full lane and leaves an entry.
        - The second override meld is served by the fast lane with its own
          payload applied.
    """
    spellbook, spell_id, conduit = _make_overridable_conduit()
    try:
        first = conduit.meld(spell_id=spell_id, override={"value": 3})
        assert first.value == 3
        assert spell_id in conduit._meld._fast_meld_doors

        spy = _install_lane_spy(conduit._meld)
        second = conduit.meld(spell_id=spell_id, override={"value": 4})
        assert second.value == 4
        assert second is not first
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_override_lane_leaves_tuple_and_empty_payloads_to_full_lane() -> None:
    """
    Purpose:
        Verify payloads that need normalization keep the full lane.
    Contract:
        - A tuple payload (root positional arguments) and an empty dict (no
          overrides) are served by the full lane with today's results.
    """
    spellbook, spell_id, conduit = _make_overridable_conduit()
    try:
        conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)

        assert conduit.meld(spell_id=spell_id, override=(5,)).value == 5
        assert spy.normal_lane_entered

        spy.normal_lane_entered = False
        assert conduit.meld(spell_id=spell_id, override={}).value == 0
        assert spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


@pytest.mark.parametrize("trip", ["spell_hooks", "meld_hooks", "validation"])
def test_component_fast_door_override_lane_guard_trips_fall_to_full_lane(trip: str) -> None:
    """
    Purpose:
        Verify every fast-door guard also protects the override arm.
    Contract:
        - After the trip, an override meld takes the full lane (pool read),
          applies its payload and fires the attached hook when one exists.
    """
    spellbook, spell_id, conduit = _make_overridable_conduit()
    try:
        conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)
        calls: list = []
        if trip == "spell_hooks":
            spellbook._spell_id_pool[spell_id]._set_hooks(
                pre_hooks=[lambda: calls.append("pre")],
            )
        elif trip == "meld_hooks":
            meld = conduit._meld
            if meld._meld_hooks is None:
                meld._meld_hooks = {}
            # In-place mutation: the live `not self._meld_hooks` guard sees it.
            meld._meld_hooks["on_meld_pre_resolve"] = [
                lambda target: calls.append(target)
            ]
        else:
            spellbook._set_spellbook_validation_required(True)

        overridden = conduit.meld(spell_id=spell_id, override={"value": 9})
        assert overridden.value == 9
        assert spy.normal_lane_entered
        assert len(calls) == (0 if trip == "validation" else 1)
    finally:
        if trip == "validation":
            spellbook._set_spellbook_validation_required(False)
        conduit.permanent_cleanup()


def test_component_fast_door_override_lane_guard_trips_on_context_invalidation() -> None:
    """
    Purpose:
        Verify context invalidation sends override melds to the full lane,
        which rebuilds the entry against the new context.
    Contract:
        - After `Spell._cleanup_creation_context()` with the production
          resolution regating, the override meld reads the pool and applies
          its payload.
        - The rebuilt entry pins the new context and serves the next override
          meld on the fast lane.
    """
    spellbook, spell_id, conduit = _make_overridable_conduit()
    try:
        conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)
        spell = spellbook._spell_id_pool[spell_id]
        spell._cleanup_creation_context()
        spell.resolution_required = True
        spell.resolution_complete = False

        assert conduit.meld(spell_id=spell_id, override={"value": 2}).value == 2
        assert spy.normal_lane_entered
        assert conduit._meld._fast_meld_doors[spell_id][1] is spell._creation_context

        spy.normal_lane_entered = False
        assert conduit.meld(spell_id=spell_id, override={"value": 3}).value == 3
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_override_lane_keeps_override_errors() -> None:
    """
    Purpose:
        Verify a bad override key fails identically on the full and fast lanes.
    Contract:
        - Before any success there is no entry, so the first bad meld runs the
          full lane and builds no entry.
        - After a plain meld builds the entry, the same bad meld runs the fast
          lane and raises the same exception type and message.
        - The spell stays usable afterwards.
    """
    spellbook, spell_id, conduit = _make_overridable_conduit()
    try:
        with pytest.raises(Exception) as full_lane:
            conduit.meld(spell_id=spell_id, override={"nosuch": 1})
        assert spell_id not in conduit._meld._fast_meld_doors

        conduit.meld(spell_id=spell_id)
        spy = _install_lane_spy(conduit._meld)
        with pytest.raises(Exception) as fast_lane:
            conduit.meld(spell_id=spell_id, override={"nosuch": 1})
        assert not spy.normal_lane_entered
        assert type(fast_lane.value) is type(full_lane.value)
        assert str(fast_lane.value) == str(full_lane.value)
        assert conduit.meld(spell_id=spell_id, override={"value": 1}).value == 1
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_override_lane_serves_key_set_plans() -> None:
    """
    Purpose:
        Verify a many_only root's key-set plan runs through the override arm.
    Contract:
        - The supplied leaf is used by identity, on the fast lane.
    """
    spellbook = _make_spellbook()
    spellbook.bind(spell=_OverrideLeaf, existence=Existence.many, permissions="create")
    root_id = spellbook.bind(spell=_OverrideRoot, existence=Existence.many, permissions="create")
    conduit = spellbook.conjure(name="root")
    try:
        injected = conduit.meld(spell_id=root_id)
        assert isinstance(injected.leaf, _OverrideLeaf)

        spy = _install_lane_spy(conduit._meld)
        supplied = _OverrideLeaf()
        assert conduit.meld(spell_id=root_id, override={"leaf": supplied}).leaf is supplied
        assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()


def test_component_fast_door_override_lane_serves_spellspace_melds() -> None:
    """
    Purpose:
        Verify the SpellSpaceMeld front door has the same override arm.
    Contract:
        - Inside a spellspace, an override meld after a plain meld is served by
          the space's fast lane with its payload applied.
    """
    spellbook, spell_id, conduit = _make_overridable_conduit()
    try:
        with conduit.enter_spellspace() as space:
            assert space.meld(spell_id=spell_id).value == 0
            assert spell_id in space._meld._fast_meld_doors
            spy = _install_lane_spy(space._meld)
            assert space.meld(spell_id=spell_id, override={"value": 6}).value == 6
            assert not spy.normal_lane_entered
    finally:
        conduit.permanent_cleanup()
'''

EDITS = [("replace", OLD_TEST, NEW_TEST), ("replace", TAIL_ANCHOR, APPENDED)]


def main() -> None:
    """Check every edit, then write (unless --check)."""
    path = pathlib.Path(sys.argv[1]) / TARGET
    check = "--check" in sys.argv[2:]
    data = path.read_bytes().decode("utf-8")
    for edit in EDITS:
        data = _apply_one(data, edit, TARGET)
    compile(data, TARGET, "exec")
    if not check:
        path.write_bytes(data.encode("utf-8"))
    print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
