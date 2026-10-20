"""
Unit tests - the Rift room lookups by spell_id answer exactly that spell (@@SINCE@@).

The owner's rule (2026-10-17): a spell_id and a SpellIndex are separate things, and a lookup by spell_id - or by a
source id, `spellbook_id:spell_id`, which names one - never answers with another version of the spell's index. The
command surfaces kept two such swaps until @@SINCE@@: the capability and codegen rooms' `get_spell_by_source_id`
resolved the record's index and returned the spell the index had active, and the static room's `get_spell_by_id`
(now `get_spell_by_spell_id`) and `get_spell_by_source_id` returned the live object of whichever published record
of the index melded first. The room command was renamed `get_spell_by_spell_id` with the Conduit lookup, with no
alias.

The doubles publish a record for each of two versions of one index - `sha-new`, the version the index has active,
and `sha-old`, a version it does not - so a path that turns the request into its index can be told apart from one
that answers the version named. (Nexus itself publishes only the version an index has active; the doubles break
that agreement on purpose.) Each exact test asks for `sha-old`.
"""

from types import SimpleNamespace
from typing import Any, Optional

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.nexus.rift.command_system.capability_command_system import CapabilityCommandSystem
from melder.nexus.rift.command_system.command_system import CommandSystem
from melder.nexus.rift.command_system.static_command_system import StaticCommandSystem


def _make_spell_record(
        *,
        spell_id: str,
        spell_index_id: str = "lineage-1",
        owner_conduit_id: Optional[str] = "ops-conduit",
        existence: Existence = Existence.unique,
) -> SimpleNamespace:
    """Return a published-record double of one version in the Book `ops-spellbook`."""
    return SimpleNamespace(
        origin_spellbook_id="ops-spellbook",
        frame_name="ops",
        owner_conduit_id=owner_conduit_id,
        spell_id=spell_id,
        spell_index_id=spell_index_id,
        spell_name="OpsSpell",
        binding_name="ops_spell",
        existence=existence,
    )


class _Projection:
    """
    The room's command projection of frame `ops`: its published records and its compiled ACL.

    `sha-new` (the index's active version) is published before `sha-old`, so a walk over the index's records meets
    the active version first.
    """

    def __init__(self) -> None:
        """Publish both versions of `lineage-1` and open the frame, the index and the owner conduit."""
        self.frame_descriptor = SimpleNamespace(
            spell_records_by_key={
                "ops-spellbook:sha-new": _make_spell_record(spell_id="sha-new"),
                "ops-spellbook:sha-old": _make_spell_record(spell_id="sha-old"),
            },
            conduit_records_by_id={},
        )
        self.compiled_access_surface = SimpleNamespace(
            command_frame_enabled=True,
            enabled_conduit_ids=("ops-conduit",),
            enabled_spell_index_ids=("lineage-1",),
        )


def _make_room_doubles(projection: _Projection) -> dict[str, Any]:
    """Return the rift, space and workstation doubles a command system is built with."""
    rift = SimpleNamespace(
        _get_required_command_projection=lambda frame_name: projection,
        _get_default_runtime_frame_name=lambda: "ops",
    )
    space = SimpleNamespace(
        space_id="space-1",
        get_default_runtime_frame_name=lambda: "ops",
        rift_gate=None,
        memory_system=None,
    )
    workstation = SimpleNamespace(get_target=lambda: None)
    return {"rift": rift, "space": space, "workstation": workstation}


class _OwnerBook:
    """The owner Spellbook double: its spell_id lookup knows both versions, each by its own spell_id."""

    def __init__(self, spells_by_spell_id: dict[str, object]) -> None:
        """Keep the spells the lookup answers."""
        self._spells_by_spell_id = spells_by_spell_id

    def find_spell_by_spell_id(self, spell_id: str) -> Optional[object]:
        """Return the spell that owns `spell_id`, or None."""
        return self._spells_by_spell_id.get(spell_id)


class _OwnerRoot:
    """
    The owner root conduit double.

    Its Book answers each spell_id with its own spell; `get_spell_by_index_id` answers the spell the index has active
    (the index path); `meld_existing_spell` answers each spell_id with its own live object and records what was asked.
    """

    def __init__(self, *, spells: dict[str, object], live_objects: dict[str, object]) -> None:
        """Keep the Book's spells and the store's live objects, keyed by spell_id."""
        self._spellbook = _OwnerBook(spells)
        self._live_objects = live_objects
        self.melded_spell_ids: list[str] = []

    def get_spell_by_index_id(self, spell_index_id: str) -> object:
        """Return the spell index `lineage-1` has active: `sha-new`."""
        return self._spellbook.find_spell_by_spell_id("sha-new")

    def meld_existing_spell(self, *, spell: str) -> object:
        """Return the live object of `spell`, or raise ValueError when it has none."""
        self.melded_spell_ids.append(spell)
        if spell not in self._live_objects:
            raise ValueError("Spell '{0}' is not live.".format(spell))
        return self._live_objects[spell]


def _install_owner(monkeypatch: pytest.MonkeyPatch, command_system: CommandSystem, owner: _OwnerRoot) -> None:
    """
    Point the room's Aether at a double that resolves `ops-conduit` (and every spell_id) to `owner`.

    A command system sets `_aether` on its own class when it is built, so this runs after construction.
    """
    monkeypatch.setattr(
        type(command_system),
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: owner,
            get_root_conduit_by_id=lambda conduit_id, frame_name: owner,
            _get_conduit_by_spell_id=lambda spell_id, frame_name: owner,
            _aetheric_frames={"ops": object()},
        ),
    )


def test_get_spell_by_source_id_returns_the_spell_its_record_names_not_the_index_active_spell(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The record `ops-spellbook:sha-old` answers the parked `sha-old` Spell, not the active `sha-new`."""
    old_spell, new_spell = object(), object()
    owner = _OwnerRoot(spells={"sha-old": old_spell, "sha-new": new_spell}, live_objects={})
    command_system = CapabilityCommandSystem(**_make_room_doubles(_Projection()))
    _install_owner(monkeypatch, command_system, owner)

    assert command_system.get_spell_by_source_id("ops-spellbook:sha-old", frame_name="ops") is old_spell
    assert command_system.get_spell_by_source_id("ops-spellbook:sha-new", frame_name="ops") is new_spell
    assert command_system.get_spell_by_index_id("lineage-1", frame_name="ops") is new_spell


def test_get_spell_by_spell_id_returns_the_spell_that_owns_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """`sha-old` answers its own Spell through the owner Book; the index path still answers the active one."""
    old_spell, new_spell = object(), object()
    owner = _OwnerRoot(spells={"sha-old": old_spell, "sha-new": new_spell}, live_objects={})
    command_system = CapabilityCommandSystem(**_make_room_doubles(_Projection()))
    _install_owner(monkeypatch, command_system, owner)

    assert command_system.get_spell_by_spell_id("sha-old", frame_name="ops") is old_spell
    assert command_system.get_spell_by_spell_id("sha-new", frame_name="ops") is new_spell


def test_get_spell_by_source_id_refuses_an_ownerless_record(monkeypatch: pytest.MonkeyPatch) -> None:
    """A record with no owner conduit has no Spellbook to answer from; the refusal names the source id."""
    projection = _Projection()
    projection.frame_descriptor.spell_records_by_key["ops-spellbook:sha-old"] = _make_spell_record(
        spell_id="sha-old", owner_conduit_id=None,
    )
    owner = _OwnerRoot(spells={"sha-new": object()}, live_objects={})
    command_system = CapabilityCommandSystem(**_make_room_doubles(projection))
    _install_owner(monkeypatch, command_system, owner)

    with pytest.raises(ValueError, match="Spell 'ops-spellbook:sha-old' has no owner conduit in frame 'ops'"):
        command_system.get_spell_by_source_id("ops-spellbook:sha-old", frame_name="ops")


def test_get_spell_by_source_id_refuses_a_spell_id_the_owner_book_no_longer_holds(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A stale record whose version its Book has disposed is refused, not answered with another version."""
    owner = _OwnerRoot(spells={"sha-new": object()}, live_objects={})
    command_system = CapabilityCommandSystem(**_make_room_doubles(_Projection()))
    _install_owner(monkeypatch, command_system, owner)

    with pytest.raises(
            ValueError,
            match="Spell 'ops-spellbook:sha-old' was not found in the owner spellbook for frame 'ops'",
    ):
        command_system.get_spell_by_source_id("ops-spellbook:sha-old", frame_name="ops")


def test_get_spell_by_source_id_still_enforces_the_spell_index_acl(monkeypatch: pytest.MonkeyPatch) -> None:
    """The exact path checks the record's spell-index ACL before it touches the owner."""
    projection = _Projection()
    projection.compiled_access_surface.enabled_spell_index_ids = tuple()
    owner = _OwnerRoot(spells={"sha-old": object()}, live_objects={})
    command_system = CapabilityCommandSystem(**_make_room_doubles(projection))
    _install_owner(monkeypatch, command_system, owner)

    with pytest.raises(ValueError, match="Command access to spell index 'lineage-1' is disabled in frame 'ops'"):
        command_system.get_spell_by_source_id("ops-spellbook:sha-old", frame_name="ops")


def test_static_get_spell_by_spell_id_melds_only_the_named_spell_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """The static room melds `sha-old` itself; the active `sha-new`, published first, is never melded."""
    old_object, new_object = object(), object()
    owner = _OwnerRoot(spells={}, live_objects={"sha-old": old_object, "sha-new": new_object})
    command_system = StaticCommandSystem(**_make_room_doubles(_Projection()))
    _install_owner(monkeypatch, command_system, owner)

    assert command_system.get_spell_by_spell_id("sha-old", frame_name="ops") is old_object
    assert owner.melded_spell_ids == ["sha-old"]


def test_static_get_spell_by_source_id_melds_only_the_named_record(monkeypatch: pytest.MonkeyPatch) -> None:
    """The source id `ops-spellbook:sha-old` melds that version only."""
    old_object, new_object = object(), object()
    owner = _OwnerRoot(spells={}, live_objects={"sha-old": old_object, "sha-new": new_object})
    command_system = StaticCommandSystem(**_make_room_doubles(_Projection()))
    _install_owner(monkeypatch, command_system, owner)

    assert command_system.get_spell_by_source_id("ops-spellbook:sha-old", frame_name="ops") is old_object
    assert owner.melded_spell_ids == ["sha-old"]


def test_static_lookups_by_spell_id_and_source_id_never_answer_another_version(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With `sha-old` not live and `sha-new` live, both exact lookups refuse, naming what was asked."""
    owner = _OwnerRoot(spells={}, live_objects={"sha-new": object()})
    command_system = StaticCommandSystem(**_make_room_doubles(_Projection()))
    _install_owner(monkeypatch, command_system, owner)

    with pytest.raises(ValueError, match="Spell id 'sha-old' is not live in frame 'ops'"):
        command_system.get_spell_by_spell_id("sha-old", frame_name="ops")
    with pytest.raises(ValueError, match="Spell 'ops-spellbook:sha-old' is not live in frame 'ops'"):
        command_system.get_spell_by_source_id("ops-spellbook:sha-old", frame_name="ops")
    assert owner.melded_spell_ids == ["sha-old", "sha-old"]


def test_static_lookup_by_spell_id_names_the_spell_id_for_an_unsupported_existence(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `many` version has no stored object to hand out; the refusal names the spell_id and the existence."""
    projection = _Projection()
    projection.frame_descriptor.spell_records_by_key["ops-spellbook:sha-old"] = _make_spell_record(
        spell_id="sha-old", existence=Existence.many,
    )
    owner = _OwnerRoot(spells={}, live_objects={"sha-new": object()})
    command_system = StaticCommandSystem(**_make_room_doubles(projection))
    _install_owner(monkeypatch, command_system, owner)

    with pytest.raises(ValueError, match="Spell id 'sha-old' uses unsupported static existence 'many'"):
        command_system.get_spell_by_spell_id("sha-old", frame_name="ops")
    assert owner.melded_spell_ids == []


def test_static_index_path_keeps_answering_the_live_object_of_a_record_of_the_index(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`get_spell_by_index_id` is the index path: it answers the first record of the index that has a live object."""
    new_object = object()
    owner = _OwnerRoot(spells={}, live_objects={"sha-new": new_object})
    command_system = StaticCommandSystem(**_make_room_doubles(_Projection()))
    _install_owner(monkeypatch, command_system, owner)

    assert command_system.get_spell_by_index_id("lineage-1", frame_name="ops") is new_object
    assert owner.melded_spell_ids == ["sha-new"]


@pytest.mark.parametrize("room_class", (CapabilityCommandSystem, StaticCommandSystem))
def test_rooms_advertise_get_spell_by_spell_id_and_keep_no_old_name(room_class: type) -> None:
    """Both rooms advertise the renamed command, and neither carries the old name (no alias)."""
    command_system = room_class(**_make_room_doubles(_Projection()))

    supported = command_system.list_supported_command_methods()
    assert "get_spell_by_spell_id" in supported
    assert "get_spell_by_id" not in supported
    with pytest.raises(AttributeError):
        command_system.get_spell_by_id("sha-old", frame_name="ops")
