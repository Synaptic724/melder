"""Regression: each collection member builds its own many-existence dependencies.

A `many` dependency reached through two members of a collection used to be ONE object shared by both
members, because every member of a collection socket sat on the same compiler path. `Existence.many`
promises a new object per consumer; shared existences stay shared.
"""

from collections.abc import Iterator
from typing import Any, Dict, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Config:
    """A dependency that may be bound shared or many."""


class Leaf:
    """A many dependency of every member, with its own many dependency."""

    def __init__(self, config: Config) -> None:
        """Store the config."""
        self.config = config


class IMember:
    """Frame type for collection members."""


class MemberA(IMember):
    """First collection member."""

    def __init__(self, leaf: Leaf) -> None:
        """Store the leaf."""
        self.leaf = leaf


class MemberB(IMember):
    """Second collection member."""

    def __init__(self, leaf: Leaf) -> None:
        """Store the leaf."""
        self.leaf = leaf


class MemberC(IMember):
    """Third collection member."""

    def __init__(self, leaf: Leaf) -> None:
        """Store the leaf."""
        self.leaf = leaf


class Holder:
    """A plain (non-collection) consumer of the collection owner, to test depth."""

    def __init__(self, members: list[IMember]) -> None:
        """Store the members."""
        self.members = members


class Root:
    """Root over a collection and a second collection of the same frame through a holder."""

    def __init__(self, members: list[IMember], holder: Holder) -> None:
        """Store both."""
        self.members = members
        self.holder = holder


@pytest.fixture
def book() -> Iterator[Spellbook]:
    """Own one isolated world with disk caching disabled."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(aetheric_frame="collection-many")
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook._aetheric_frame_configuration.with_system_caching_enabled(False)
    try:
        yield spellbook
    finally:
        spellbook.cleanup()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def _conjure(spellbook: Spellbook, config_existence: Existence) -> Conduit:
    """Bind the world (Config under `config_existence`, everything else many) and conjure it."""
    bindings: List[Tuple[Any, Existence, Dict[str, Any]]] = [
        (Config, config_existence, {}),
        (Leaf, Existence.many, {}),
        (MemberA, Existence.many, {"spellframe": IMember, "binding_name": "a"}),
        (MemberB, Existence.many, {"spellframe": IMember, "binding_name": "b"}),
        (MemberC, Existence.many, {"spellframe": IMember, "binding_name": "c"}),
        (Holder, Existence.many, {}),
        (Root, Existence.many, {}),
    ]
    for spell, existence, extra in bindings:
        spellbook.bind(spell=spell, existence=existence, permissions="create", **extra)
    return spellbook.conjure()


def _members(root: Root) -> List[IMember]:
    """Return the members of both collections, root collection first."""
    return list(root.members) + list(root.holder.members)


def _distinct(objects: List[Any]) -> int:
    """Count distinct objects by identity."""
    return len({id(item) for item in objects})


@pytest.mark.parametrize("config_existence", [Existence.many, Existence.unique_per_conduit])
def test_each_collection_member_builds_its_own_many_dependency(
        book: Spellbook,
        config_existence: Existence,
) -> None:
    """Every member of every collection gets a new Leaf; nothing many is shared between members."""
    root = _conjure(book, config_existence).meld(Root)

    members = _members(root)
    assert [type(member).__name__ for member in members] == ["MemberA", "MemberB", "MemberC"] * 2
    assert _distinct(members) == 6
    assert _distinct([member.leaf for member in members]) == 6


def test_many_config_below_members_is_one_object_per_leaf(book: Spellbook) -> None:
    """A many dependency two levels below the collection is also built per member."""
    root = _conjure(book, Existence.many).meld(Root)

    configs = [member.leaf.config for member in _members(root)]
    assert _distinct(configs) == 6


def test_shared_config_below_members_stays_one_object(book: Spellbook) -> None:
    """A shared existence below the members is still shared: the fix only splits many."""
    root = _conjure(book, Existence.unique_per_conduit).meld(Root)

    configs = [member.leaf.config for member in _members(root)]
    assert _distinct(configs) == 1


def test_second_meld_builds_new_many_objects(book: Spellbook) -> None:
    """Many stays many across melds: a second meld shares no member or leaf with the first."""
    conduit = _conjure(book, Existence.many)
    first = _members(conduit.meld(Root))
    second = _members(conduit.meld(Root))

    assert _distinct(first + second) == 12
    assert _distinct([member.leaf for member in first + second]) == 12
