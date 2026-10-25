"""
Integration: a version staged with `bind_inactive` before `conjure` melds after a notch exactly as one staged after
it (STORY-2026-10-16-parked_versions_wired_at_conjure, 0.2.8248).

Conjure wires every version its Book owns: the active ones as before and, since 0.2.8248, the parked ones with the
owner stamp a post-conjure `bind_inactive` applies. Until then a version parked before conjure had no
CreationContextFactory, and after a notch its first meld raised "Spell has no configured CreationContextFactory."
for every existence. Each test runs a dynamic world twice - the version staged before conjure and after it - and
expects the same outcome from both.

Both versions are bound under one string spellframe, 'service', and the default binding name: every version of an
index is bound the way its first version was (2026-10-25).
"""
from collections.abc import Iterator
from typing import Any, Callable, Dict, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

pytestmark = pytest.mark.integration


class ServiceA:
    """The version bound active."""


class ServiceB:
    """The version staged with `bind_inactive` and notched in."""


def make_service_a() -> ServiceA:
    """
    The function spell bound active.

    Returns:
        ServiceA: A new object.
    """
    return ServiceA()


def make_service_b() -> ServiceB:
    """
    The function spell staged and notched in.

    Returns:
        ServiceB: A new object.
    """
    return ServiceB()


class _Family:
    """One way to bind the two versions: the targets, their existence and the managed options."""

    def __init__(
            self,
            name: str,
            existence: Existence,
            make_targets: Callable[[], Tuple[Any, Any]],
            options: Dict[str, Any],
    ) -> None:
        """
        Describe a family.

        Args:
            name: The test id.
            existence: The existence both versions are bound with.
            make_targets: Returns (active target, staged target), fresh per world.
            options: Extra bind keywords (the managed options).
        """
        self.name: str = name
        self.existence: Existence = existence
        self.make_targets: Callable[[], Tuple[Any, Any]] = make_targets
        self.options: Dict[str, Any] = options


class _World:
    """A dynamic root whose index holds an active version and a staged one."""

    def __init__(self, family: _Family, *, staged_before_conjure: bool) -> None:
        """
        Bind the active version, stage the second one before or after conjure, and conjure.

        Args:
            family: How to bind the two versions.
            staged_before_conjure: Stage on the Book before `conjure` (True) or on the root after it (False).
        """
        active_target, staged_target = family.make_targets()
        self.staged_target: Any = staged_target
        configuration = SpellbookConfiguration(aether_frame="default")
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        configuration.finalize()
        self.book: Spellbook = Spellbook(aetheric_frame="default", configuration=configuration)
        self.active_id: str = self.book.bind(
            spell=active_target, existence=family.existence, permissions="create", spellframe="service",
            **family.options,
        )
        self.index: Any = self.book.find_spell_by_spell_id(self.active_id).spell_index
        if staged_before_conjure:
            self.staged_id: str = self.book.bind_inactive(
                spell=staged_target, spell_index=self.index, existence=family.existence, permissions="create",
                spellframe="service", **family.options,
            )
            self.root: Conduit = self.book.conjure(dynamic=True, name="root")
        else:
            self.root = self.book.conjure(dynamic=True, name="root")
            self.staged_id = self.root.bind_inactive(
                spell=staged_target, spell_index=self.index, existence=family.existence, permissions="create",
                spellframe="service", **family.options,
            )

    def notch_to_staged(self) -> None:
        """Make the staged version the index's active member."""
        staged = self.book._get_owned_spell(self.staged_id)
        self.root.notch_spell(spell_index=self.index, spell=staged)

    def close(self) -> None:
        """Tear the root and the Book down."""
        self.root.cleanup()
        self.book.cleanup()


def _families() -> List[_Family]:
    """
    Every family the fix covers: the four class existences, an existing object and a function.

    Returns:
        List[_Family]: Fresh family descriptions, in test-id order.
    """
    return [
        _Family("unique", Existence.unique, lambda: (ServiceA, ServiceB), {}),
        _Family("unique_per_conduit", Existence.unique_per_conduit, lambda: (ServiceA, ServiceB), {}),
        _Family("many", Existence.many, lambda: (ServiceA, ServiceB), {}),
        _Family(
            "managed_spell_quantity", Existence.managed_spell_quantity, lambda: (ServiceA, ServiceB),
            {"managed_spell_limit": 4},
        ),
        _Family("existing_object", Existence.unique, lambda: (ServiceA(), ServiceB()), {}),
        _Family("function", Existence.unique, lambda: (make_service_a, make_service_b), {}),
    ]


def _family(name: str) -> _Family:
    """
    Return one family by its test id.

    Args:
        name: The family's test id.

    Returns:
        _Family: The family.
    """
    return next(family for family in _families() if family.name == name)


def _reset_world() -> None:
    """Fresh Aether and utility-system singletons, and the release registry Aether builds with them."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """Isolate each test behind fresh singletons."""
    _reset_world()
    yield
    _reset_world()


@pytest.mark.parametrize("staged_before_conjure", [True, False], ids=["staged_before_conjure", "staged_after"])
@pytest.mark.parametrize("family", _families(), ids=[family.name for family in _families()])
def test_a_staged_version_melds_after_a_notch(family: _Family, staged_before_conjure: bool) -> None:
    """
    After a notch, the staged version melds whether it was staged before or after conjure: a new ServiceB from a class
    or a function, the staged object itself for an existing object.
    """
    world = _World(family, staged_before_conjure=staged_before_conjure)
    try:
        world.notch_to_staged()
        melded = world.root.meld(spell_id=world.staged_id)
        if family.name == "existing_object":
            assert melded is world.staged_target
        else:
            assert isinstance(melded, ServiceB)
    finally:
        world.close()


@pytest.mark.parametrize("staged_before_conjure", [True, False], ids=["staged_before_conjure", "staged_after"])
@pytest.mark.parametrize("family", _families(), ids=[family.name for family in _families()])
def test_before_its_notch_a_staged_version_is_not_meldable_by_id(family: _Family, staged_before_conjure: bool) -> None:
    """
    Wiring does not put a staged version on the resolution surface: before its notch a meld of its id raises KeyError
    while the active version melds, whichever moment it was staged at.
    """
    world = _World(family, staged_before_conjure=staged_before_conjure)
    try:
        with pytest.raises(KeyError, match="No spell found with spell_id"):
            world.root.meld(spell_id=world.staged_id)
        assert world.root.meld(spell_id=world.active_id) is not None
    finally:
        world.close()


@pytest.mark.parametrize("staged_before_conjure", [True, False], ids=["staged_before_conjure", "staged_after"])
def test_a_staged_existing_object_is_not_registered_in_the_store(staged_before_conjure: bool) -> None:
    """
    A staged existing object is wired, not registered: the root's store holds the active object only, before and
    after the notch, whichever moment it was staged at.
    """
    family = _family("existing_object")
    world = _World(family, staged_before_conjure=staged_before_conjure)
    try:
        store = world.root._creations._creations
        assert world.active_id in store and world.staged_id not in store
        world.notch_to_staged()
        assert world.root.meld(spell_id=world.staged_id) is world.staged_target
        assert world.staged_id not in store
    finally:
        world.close()


def test_a_managed_version_staged_before_conjure_has_its_pool_from_conjure() -> None:
    """
    Conjure gives a managed version staged before it its pool in the root's store and a registry entry; after the
    notch, `managed_spell_meld` leases from that pool and the release puts the object back.
    """
    family = _family("managed_spell_quantity")
    world = _World(family, staged_before_conjure=True)
    try:
        pool = world.root._creations.get_managed_quantity(world.staged_id)
        assert pool is not None and pool.count == 0
        rows = ReleaseManagedSpell().describe(ServiceB)
        assert [row["spell_id"] for row in rows] == [world.staged_id]
        world.notch_to_staged()
        with world.root.managed_spell_meld(spell_id=world.staged_id) as leased:
            assert isinstance(leased, ServiceB)
            assert (pool.count, pool.idle_count) == (1, 0)
        assert (pool.count, pool.idle_count) == (1, 1)
        assert world.root.meld(spell_id=world.staged_id) is leased
    finally:
        world.close()
