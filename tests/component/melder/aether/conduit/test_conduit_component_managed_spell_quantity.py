"""
Component: melds dispense managed objects through emitted plans (STORY-2026-10-15-managed_dispense_codegen).

Through a real Spellbook and root conduit: a direct meld leases from the spell's pool and reuses what was released,
holders receive leases by injection (one per path; a `unique` holder keeps its own), limited_quantity refuses and
queue waits through melds, a holder that fails to construct gives its lease back, overrides take no lease or build
fresh, a trim disposes the object with the children recorded for it, activation hooks run on every lease, and
`Conduit.managed_spell_meld` returns a lease that gives the object back.
"""
import threading
from collections.abc import Iterator
from typing import Any, Dict, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_lease import ManagedSpellLease
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.managed_spell_exhausted_error import ManagedSpellExhaustedError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
)


class Child:
    """A `many` dependency of Connection with a disposal method."""

    journal: List[str] = []

    def close(self) -> None:
        """Record one disposal."""
        Child.journal.append("child-close")


class Connection:
    """The managed target: counts builds, records resets and disposals."""

    built: int = 0
    journal: List[str] = []

    def __init__(self, dsn: str = "default") -> None:
        """
        Count the build and keep the data source name.

        Args:
            dsn: Data source name; overrides supply it.
        """
        Connection.built += 1
        self.dsn = dsn

    def reset(self) -> None:
        """Record one reset."""
        Connection.journal.append("reset")

    def close(self) -> None:
        """Record one disposal."""
        Connection.journal.append("close")


class ChildConnection:
    """A managed target with a disposal-bearing `many` child."""

    def __init__(self, child: Child) -> None:
        """
        Keep the child.

        Args:
            child: The child built for this object.
        """
        self.child = child

    def close(self) -> None:
        """Record one disposal."""
        Child.journal.append("connection-close")


class Request:
    """A `many` holder of one lease."""

    def __init__(self, connection: Connection) -> None:
        """
        Keep the connection.

        Args:
            connection: The leased connection.
        """
        self.connection = connection


class Service:
    """A `unique` holder of one lease."""

    def __init__(self, connection: Connection) -> None:
        """
        Keep the connection.

        Args:
            connection: The leased connection.
        """
        self.connection = connection


class Refusing:
    """A `many` holder whose constructor raises after receiving its lease."""

    def __init__(self, connection: Connection) -> None:
        """
        Refuse the build.

        Args:
            connection: The leased connection.

        Raises:
            ValueError: Always.
        """
        raise ValueError("refused")


def _reset_aether() -> None:
    """Install a fresh Aether (and with it a fresh registry) for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """A fresh Aether and empty journals per test."""
    _reset_aether()
    Connection.built = 0
    Connection.journal = []
    Child.journal = []
    yield
    _reset_aether()


def _book(dynamic: bool = False) -> Spellbook:
    """
    A Book with one phase worker in an automatic (or dynamic) world.

    Args:
        dynamic: Build a dynamic world.

    Returns:
        Spellbook: The Book.
    """
    configuration = SpellbookConfiguration(aether_frame="default")
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        configuration.load_default_dictionary()
        set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    if dynamic:
        configuration.finalize()
    return Spellbook(aetheric_frame="default", configuration=configuration)


def _root(dynamic: bool = False, **managed: Any) -> Conduit:
    """
    A root with Connection managed and Request, Service and Refusing as holders.

    Args:
        dynamic: Build a dynamic world.
        **managed: Extra bind keywords for Connection.

    Returns:
        Conduit: The conjured root.
    """
    book = _book(dynamic)
    book.bind(
        spell=Connection, existence=Existence.managed_spell_quantity, permissions="create",
        disposal_method_names=["close"], **managed,
    )
    book.bind(spell=Request, existence=Existence.many, permissions="create")
    book.bind(spell=Service, existence=Existence.unique, permissions="create")
    book.bind(spell=Refusing, existence=Existence.many, permissions="create")
    return book.conjure(name="managed-root", dynamic=dynamic)


def _pool(cls: type = Connection) -> Dict[str, Any]:
    """Return the one pool snapshot ReleaseManagedSpell describes for `cls`."""
    (entry,) = ReleaseManagedSpell().describe(cls)
    return entry


def _teardown(root: Conduit) -> None:
    """Tear the root and its Book down."""
    book = root.spellbook
    root.cleanup()
    book.cleanup()


def test_direct_meld_reuses_a_released_object() -> None:
    """A released object is the next meld's object; nothing new is built."""
    root = _root()
    try:
        first = root.meld(spell=Connection)
        ReleaseManagedSpell().release(first)
        assert root.meld(spell=Connection) is first
        assert Connection.built == 1 and (_pool()["count"], _pool()["idle_count"]) == (1, 0)
    finally:
        _teardown(root)


def test_meld_by_name_and_by_id_lease_from_the_same_pool() -> None:
    """Every meld door of the spell leases from its one pool."""
    root = _root()
    try:
        first = root.meld("Connection")
        ReleaseManagedSpell().release(first)
        assert root.meld(spell_id=_pool()["spell_id"]) is first
    finally:
        _teardown(root)


def test_many_holder_gets_its_own_lease_on_every_meld() -> None:
    """Two Requests, two leases."""
    root = _root()
    try:
        first, second = root.meld(spell=Request), root.meld(spell=Request)
        assert first.connection is not second.connection
        assert (_pool()["count"], _pool()["out_count"]) == (2, 2)
    finally:
        _teardown(root)


def test_unique_holder_keeps_its_lease_for_its_life() -> None:
    """The stored Service is reused; its connection is leased once."""
    root = _root()
    try:
        service = root.meld(spell=Service)
        assert root.meld(spell=Service) is service
        assert (_pool()["count"], _pool()["out_count"], Connection.built) == (1, 1, 1)
    finally:
        _teardown(root)


def test_released_object_is_injected_into_the_next_holder() -> None:
    """A release by any holder feeds the next injection."""
    root = _root()
    try:
        request = root.meld(spell=Request)
        ReleaseManagedSpell().release(request.connection)
        assert root.meld(spell=Request).connection is request.connection
        assert Connection.built == 1
    finally:
        _teardown(root)


def test_limited_quantity_refuses_through_meld_at_its_limit_until_a_release() -> None:
    """limited_quantity 1: the second meld refuses; after a release it is served."""
    root = _root(managed_spell_mode=ManagedSpellMode.limited_quantity, managed_spell_limit=1)
    try:
        first = root.meld(spell=Connection)
        with pytest.raises(ManagedSpellExhaustedError):
            root.meld(spell=Request)
        ReleaseManagedSpell().release(first)
        assert root.meld(spell=Request).connection is first
        assert Connection.built == 1
    finally:
        _teardown(root)


def test_queue_meld_waits_and_is_served_by_a_release() -> None:
    """queue 1: a second meld waits; the release serves it the same object."""
    root = _root(
        managed_spell_mode=ManagedSpellMode.queue, managed_spell_limit=1, managed_spell_timeout_seconds=10.0,
    )
    try:
        first = root.meld(spell=Connection)
        received: List[Any] = []
        waiter = threading.Thread(target=lambda: received.append(root.meld(spell=Connection)))
        waiter.start()
        ReleaseManagedSpell().release(first)
        waiter.join(timeout=15)
        assert received == [first] and Connection.built == 1
    finally:
        _teardown(root)


def test_queue_meld_raises_the_exhaustion_error_at_its_timeout() -> None:
    """queue 1 with a short timeout: the second meld raises; nothing was built."""
    root = _root(
        managed_spell_mode=ManagedSpellMode.queue, managed_spell_limit=1, managed_spell_timeout_seconds=0.05,
    )
    try:
        root.meld(spell=Connection)
        with pytest.raises(ManagedSpellExhaustedError):
            root.meld(spell=Connection)
        assert Connection.built == 1
    finally:
        _teardown(root)


def test_failed_holder_gives_its_lease_back() -> None:
    """Refusing raises after its lease: the connection is idle again and serves the next meld unbuilt."""
    root = _root()
    try:
        with pytest.raises(MeldExecutionError):
            root.meld(spell=Refusing)
        assert (_pool()["count"], _pool()["idle_count"]) == (1, 1)
        root.meld(spell=Connection)
        assert Connection.built == 1
    finally:
        _teardown(root)


def test_override_of_the_holders_parameter_takes_no_lease() -> None:
    """Supplying Request's connection removes the managed site."""
    root = _root()
    try:
        supplied = Connection("given")
        assert root.meld(spell=Request, override={"connection": supplied}).connection is supplied
        assert _pool()["count"] == 0
    finally:
        _teardown(root)


def test_override_of_the_managed_spells_own_parameter_builds_a_fresh_object() -> None:
    """A key on Connection's own parameter builds it fresh with that value: not pooled, not counted."""
    root = _root()
    try:
        request = root.meld(spell=Request, override={"connection>dsn": "replica"})
        assert request.connection.dsn == "replica"
        assert root.meld(spell=Connection, override={"dsn": "primary"}).dsn == "primary"
        assert _pool()["count"] == 0
    finally:
        _teardown(root)


def test_trim_disposes_the_object_and_its_recorded_children() -> None:
    """Elastic with limit 1: the second idle object is evicted with its child."""
    book = _book()
    book.bind(spell=Child, existence=Existence.many, permissions="create", disposal_method_names=["close"])
    book.bind(
        spell=ChildConnection, existence=Existence.managed_spell_quantity, permissions="create",
        disposal_method_names=["close"], managed_spell_limit=1,
    )
    root = book.conjure(name="managed-root")
    try:
        first, second = root.meld(spell=ChildConnection), root.meld(spell=ChildConnection)
        assert first.child is not second.child and Child.journal == []
        ReleaseManagedSpell().release(first)
        ReleaseManagedSpell().release(second)
        assert Child.journal == ["connection-close", "child-close"]
        assert (_pool(ChildConnection)["count"], _pool(ChildConnection)["idle_count"]) == (1, 1)
    finally:
        _teardown(root)


def test_activation_hooks_run_on_every_lease() -> None:
    """The managed door reports `created=True`: a reused object passes the activation hooks again."""
    book = _book()
    activated: List[Any] = []
    book.bind(
        spell=Connection, existence=Existence.managed_spell_quantity, permissions="create",
        activation_hooks=[activated.append],
    )
    root = book.conjure(name="managed-root")
    try:
        first = root.meld(spell=Connection)
        ReleaseManagedSpell().release(first)
        root.meld(spell=Connection)
        assert activated == [first, first]
    finally:
        _teardown(root)


def test_managed_spell_meld_with_block_gives_the_object_back() -> None:
    """The lease's `with` releases on exit; the next meld gets the same object."""
    root = _root(managed_spell_reset_methods=["reset"])
    try:
        with root.managed_spell_meld(Connection) as connection:
            assert isinstance(connection, Connection) and _pool()["out_count"] == 1
        assert (_pool()["idle_count"], Connection.journal) == (1, ["reset"])
        assert root.meld(spell=Connection) is connection
    finally:
        _teardown(root)


def test_managed_spell_meld_with_block_releases_when_the_block_raises() -> None:
    """The block's exception propagates and the object is back in the pool."""
    root = _root()
    try:
        with pytest.raises(KeyError):
            with root.managed_spell_meld(spell=Connection):
                raise KeyError("block failed")
        assert _pool()["idle_count"] == 1
    finally:
        _teardown(root)


def test_managed_spell_meld_without_with_releases_once() -> None:
    """`release()` gives the object back once; a second call does nothing."""
    root = _root()
    try:
        lease = root.managed_spell_meld("Connection")
        assert isinstance(lease, ManagedSpellLease) and isinstance(lease.object, Connection)
        lease.release()
        lease.release()
        assert (_pool()["count"], _pool()["idle_count"]) == (1, 1)
    finally:
        _teardown(root)


def test_managed_spell_meld_by_spell_id() -> None:
    """`spell_id=` resolves the managed version directly."""
    root = _root()
    try:
        lease = root.managed_spell_meld(spell_id=_pool()["spell_id"])
        assert isinstance(lease.object, Connection)
    finally:
        _teardown(root)


def test_managed_spell_meld_refuses_a_spell_of_another_existence_before_melding() -> None:
    """A `many` target is refused with the remedy; nothing is built."""
    root = _root()
    try:
        with pytest.raises(ValueError, match="managed_spell_meld leases a managed spell; 'Request' is many"):
            root.managed_spell_meld(Request)
        assert _pool()["count"] == 0
    finally:
        _teardown(root)


def test_managed_spell_meld_refuses_spell_and_spell_id_together() -> None:
    """The two identities are exclusive, as for meld."""
    root = _root()
    try:
        with pytest.raises(ValueError, match="either `spell` or `spell_id`"):
            root.managed_spell_meld(Connection, spell_id="abc")
    finally:
        _teardown(root)


def test_managed_spell_meld_raises_the_exhaustion_error_at_the_limit() -> None:
    """limited_quantity 1 with its object out: the lease is refused."""
    root = _root(managed_spell_mode=ManagedSpellMode.limited_quantity, managed_spell_limit=1)
    try:
        root.managed_spell_meld(Connection)
        with pytest.raises(ManagedSpellExhaustedError):
            root.managed_spell_meld(Connection)
    finally:
        _teardown(root)


def test_lesser_conduit_and_spellspace_lease_from_the_roots_pool() -> None:
    """A lesser's and a spellspace's melds lease from the owning root's pool."""
    root = _root()
    try:
        lesser = root.create_lesser_conduit()
        from_lesser = lesser.meld(spell=Connection)
        ReleaseManagedSpell().release(from_lesser)
        with root.enter_spellspace() as space:
            assert space.meld(spell=Connection) is from_lesser
        lesser.cleanup()
        assert (_pool()["count"], Connection.built) == (1, 1)
    finally:
        _teardown(root)


def test_root_teardown_disposes_idle_objects_and_leaves_objects_that_are_out() -> None:
    """Teardown closes what is idle; an object still out is its holder's."""
    root = _root()
    out, idle = root.meld(spell=Connection), root.meld(spell=Connection)
    ReleaseManagedSpell().release(idle)
    _teardown(root)
    assert Connection.journal == ["close"]
    assert out.dsn == "default"


def test_dynamic_root_leases_through_the_per_creation_pool_read() -> None:
    """In a dynamic world the plan reads the pool per creation; leases and reuse behave the same."""
    root = _root(dynamic=True)
    try:
        first = root.meld(spell=Request).connection
        ReleaseManagedSpell().release(first)
        assert root.meld(spell=Service).connection is first
        assert Connection.built == 1
    finally:
        _teardown(root)
