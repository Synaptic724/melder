"""
Contract probes for the managed spell pool lessons (intermediate 42-48). Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_managed_spell_probes.py -v

WHY THIS FILE EXISTS
--------------------
The example law (`UX_and_AIX_experiences/AGENTS.md`) lets a lesson assert only behaviour
verified in source or proven by a probe row. These probes pin each behaviour the
managed lessons rely on through the public `melder` surface - the three pool modes, the
lease and release verbs, reset methods, request scopes, root teardown, a settings rebind
and an ownership transfer - so a change in any of them fails here with a name, not as a
lesson's bare assertion. The evidence behind each row is the lifecycle map of
STORY-2026-10-18-managed_spell_lifecycle_map (probe_managed_lifecycle.py, 19 cases).

Every test runs in a fresh world: the conftest fixture resets the hosted roots and
Aether before and after each test, and each test cleans the conduits and books it made.
"""
import threading
import time
from typing import Any, Dict, Iterator, List, Tuple

import pytest

import melder as md


# ----------------------------------------------------------------------------------------
# Probe classes
# ----------------------------------------------------------------------------------------
class Resource:
    """A pooled object with an observable disposal method (`close`)."""

    def __init__(self) -> None:
        """Start open."""
        self.closed: bool = False

    def close(self) -> None:
        """Mark the object disposed."""
        self.closed = True


class Resettable:
    """A pooled object that records the reset calls the pool makes."""

    def __init__(self) -> None:
        """Start with no reset calls and no state."""
        self.calls: List[str] = []
        self.state: List[str] = []
        self.closed: bool = False

    def first(self) -> None:
        """First reset: clears the state."""
        self.state.clear()
        self.calls.append("first")

    def second(self) -> None:
        """Second reset."""
        self.calls.append("second")

    def close(self) -> None:
        """Disposal method."""
        self.closed = True


class Breakable:
    """A pooled object whose reset raises once broken."""

    def __init__(self) -> None:
        """Start intact and open."""
        self.broken: bool = False
        self.closed: bool = False

    def reset(self) -> None:
        """Refuse to reset a broken object."""
        if self.broken:
            raise ValueError("broken")

    def close(self) -> None:
        """Disposal method."""
        self.closed = True


class NotManaged:
    """A plain `many` spell."""


class Handler:
    """A `many` consumer that receives a pooled Resource and releases it at its disposal."""

    def __init__(self, resource: Resource) -> None:
        """Keep the leased resource."""
        self.resource: Resource = resource
        self.finished: bool = False

    def finish(self) -> None:
        """Give the resource back once."""
        if self.finished:
            return
        self.finished = True
        md.ReleaseManagedSpell().release(self.resource)


class Scoped:
    """A `unique_per_conduit` spell."""


class DependsOnScoped:
    """A managed spell that depends on a shorter-lived spell."""

    def __init__(self, scoped: Scoped) -> None:
        """Keep the scoped dependency."""
        self.scoped: Scoped = scoped


# ----------------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------------
def pool_counts(cls: type) -> Tuple[int, int, int]:
    """Return (alive, idle, out) for the one pool of a managed class."""
    (snapshot,) = md.ReleaseManagedSpell().describe(cls)
    return snapshot["count"], snapshot["idle_count"], snapshot["out_count"]


@pytest.fixture
def make_root() -> Iterator[Any]:
    """Build roots from bind specs and clean every root and book afterwards.

    Each call binds `(cls, kwargs)` pairs into a fresh Spellbook and conjures it;
    `dynamic=True` settles the world dynamic for the rebind and transfer probes.
    """
    made: List[Tuple[md.Spellbook, md.Conduit]] = []

    def build(*binds: Tuple[type, Dict[str, Any]], dynamic: bool = False, name: str = "") -> md.Conduit:
        configuration = md.SpellbookConfiguration()
        configuration.with_defaults()
        book = md.Spellbook(configuration=configuration)
        for cls, kwargs in binds:
            book.bind(spell=cls, **kwargs)
        conduit = book.conjure(dynamic=True, name=name) if dynamic else book.conjure()
        made.append((book, conduit))
        return conduit

    yield build
    for book, conduit in reversed(made):
        if not conduit.cleaned:
            conduit.cleanup()
        book.cleanup()


def managed(**options: Any) -> Dict[str, Any]:
    """Return fresh bind options for a managed spell: the existence plus `options`.

    Every call builds a new dict, so no probe can leak options into another.
    """
    return {"existence": md.Existence.managed_spell_quantity, **options}


# ----------------------------------------------------------------------------------------
# Composition and the elastic mode (lesson 42)
# ----------------------------------------------------------------------------------------
def test_probe_pool_exists_from_conjure_with_elastic_defaults(make_root: Any) -> None:
    """A managed spell's pool is composed at conjure, empty, elastic with limit 256."""
    conduit = make_root((Resource, managed()))
    (snapshot,) = md.ReleaseManagedSpell().describe(Resource)
    assert snapshot["mode"] == "elastic" and snapshot["limit"] == 256
    assert snapshot["timeout_seconds"] is None
    assert pool_counts(Resource) == (0, 0, 0)
    assert not conduit.has_live_creation("Resource")


def test_probe_release_makes_the_object_idle_and_the_newest_is_leased_first(make_root: Any) -> None:
    """A release keeps the object open and idle; the next meld takes the newest idle object."""
    conduit = make_root((Resource, managed()))
    first = conduit.meld("Resource")
    second = conduit.meld("Resource")
    assert first is not second and pool_counts(Resource) == (2, 0, 2)
    assert conduit.has_live_creation("Resource")
    md.ReleaseManagedSpell().release(first)
    md.ReleaseManagedSpell().release(second)
    assert pool_counts(Resource) == (2, 2, 0) and not first.closed
    assert conduit.meld("Resource") is second


def test_probe_elastic_small_limit_destroys_the_oldest_idle_object(make_root: Any) -> None:
    """Elastic never refuses; with limit 2 a third release destroys the oldest idle object."""
    conduit = make_root((Resource, managed(managed_spell_limit=2, disposal_method_names=["close"])))
    objects = [conduit.meld("Resource") for _ in range(3)]
    assert pool_counts(Resource) == (3, 0, 3)
    for obj in objects:
        md.ReleaseManagedSpell().release(obj)
    assert [obj.closed for obj in objects] == [True, False, False]
    assert pool_counts(Resource) == (2, 2, 0)


def test_probe_root_teardown_disposes_idle_objects_and_unregisters_the_pool(make_root: Any) -> None:
    """Root teardown runs disposal on idle objects only and removes the class from the registry."""
    conduit = make_root((Resource, managed(disposal_method_names=["close"])))
    idle = conduit.meld("Resource")
    out = conduit.meld("Resource")
    md.ReleaseManagedSpell().release(idle)
    conduit.cleanup()
    assert idle.closed and not out.closed
    assert md.ReleaseManagedSpell().describe(Resource) == ()


# ----------------------------------------------------------------------------------------
# limited_quantity and queue (lessons 43-44)
# ----------------------------------------------------------------------------------------
def test_probe_limited_quantity_refuses_at_its_limit_and_builds_nothing(make_root: Any) -> None:
    """At the limit with nothing idle the meld raises ManagedSpellExhaustedError; count is unchanged."""
    conduit = make_root((Resource, managed(managed_spell_mode="limited_quantity", managed_spell_limit=2)))
    held = [conduit.meld("Resource"), conduit.meld("Resource")]
    with pytest.raises(md.ManagedSpellExhaustedError) as refused:
        conduit.meld("Resource")
    error = refused.value
    assert isinstance(error, md.MeldExecutionError)
    assert (error.mode, error.limit, error.timeout_seconds) == ("limited_quantity", 2, None)
    assert "Release one with ReleaseManagedSpell().release(obj)" in str(error)
    assert pool_counts(Resource) == (2, 0, 2)
    md.ReleaseManagedSpell().release(held[0])
    assert conduit.meld("Resource") is held[0]


def test_probe_release_all_gives_every_object_back(make_root: Any) -> None:
    """release_all attempts every object; the pool then holds them idle."""
    conduit = make_root((Resource, managed(managed_spell_mode="limited_quantity", managed_spell_limit=2)))
    md.ReleaseManagedSpell().release_all([conduit.meld("Resource"), conduit.meld("Resource")])
    assert pool_counts(Resource) == (2, 2, 0)


def test_probe_queue_hands_the_released_object_to_a_waiting_meld(make_root: Any) -> None:
    """At the limit a queue meld waits; a release hands it the released object."""
    conduit = make_root(
        (Resource, managed(managed_spell_mode="queue", managed_spell_limit=1, managed_spell_timeout_seconds=5.0)),
    )
    held = conduit.meld("Resource")
    received: List[Resource] = []
    waiter = threading.Thread(target=lambda: received.append(conduit.meld("Resource")))
    waiter.start()
    time.sleep(0.1)
    assert waiter.is_alive() and not received
    md.ReleaseManagedSpell().release(held)
    waiter.join(timeout=5.0)
    assert not waiter.is_alive() and received and received[0] is held


def test_probe_queue_refuses_at_its_timeout(make_root: Any) -> None:
    """A queue meld that waits past managed_spell_timeout_seconds raises, naming the queue policy."""
    conduit = make_root(
        (Resource, managed(managed_spell_mode=md.ManagedSpellMode.queue, managed_spell_limit=1,
                           managed_spell_timeout_seconds=0.2)),
    )
    conduit.meld("Resource")
    began = time.monotonic()
    with pytest.raises(md.ManagedSpellExhaustedError) as refused:
        conduit.meld("Resource")
    assert time.monotonic() - began >= 0.2
    assert (refused.value.mode, refused.value.limit, refused.value.timeout_seconds) == ("queue", 1, 0.2)


# ----------------------------------------------------------------------------------------
# Reset methods (lesson 45)
# ----------------------------------------------------------------------------------------
def test_probe_resets_run_in_order_on_every_release(make_root: Any) -> None:
    """The named reset methods run in order on release; the next lease gets the reset object."""
    conduit = make_root((Resettable, managed(managed_spell_reset_methods=["first", "second"])))
    obj = conduit.meld("Resettable")
    obj.state.append("dirty")
    md.ReleaseManagedSpell().release(obj)
    assert obj.calls == ["first", "second"] and obj.state == []
    assert conduit.meld("Resettable") is obj


def test_probe_a_raising_reset_destroys_the_object_and_propagates(make_root: Any) -> None:
    """A raising reset runs the disposal methods, frees the place and re-raises from the release."""
    conduit = make_root(
        (Breakable, managed(managed_spell_reset_methods=["reset"], disposal_method_names=["close"])),
    )
    obj = conduit.meld("Breakable")
    obj.broken = True
    with pytest.raises(ValueError, match="broken"):
        md.ReleaseManagedSpell().release(obj)
    assert obj.closed and pool_counts(Breakable) == (0, 0, 0)
    assert conduit.meld("Breakable") is not obj


# ----------------------------------------------------------------------------------------
# Leases (lesson 46)
# ----------------------------------------------------------------------------------------
def test_probe_managed_spell_meld_lease_releases_at_block_exit(make_root: Any) -> None:
    """The `with` block of managed_spell_meld leases the object and releases it on exit."""
    conduit = make_root((Resource, managed()))
    with conduit.managed_spell_meld(Resource) as obj:
        assert isinstance(obj, Resource) and pool_counts(Resource) == (1, 0, 1)
    assert pool_counts(Resource) == (1, 1, 0)


def test_probe_a_lease_releases_once_and_then_refuses_its_object(make_root: Any) -> None:
    """release() twice is one release; lease.object raises RuntimeError after it."""
    conduit = make_root((Resource, managed()))
    lease = conduit.managed_spell_meld("Resource")
    assert isinstance(lease, md.ManagedSpellLease) and not lease.released
    lease.release()
    lease.release()
    assert lease.released and pool_counts(Resource) == (1, 1, 0)
    with pytest.raises(RuntimeError):
        lease.object


def test_probe_a_raising_block_still_releases_and_is_not_suppressed(make_root: Any) -> None:
    """The lease's exit releases even when the block raised, and never swallows the error."""
    conduit = make_root((Resource, managed()))
    with pytest.raises(ConnectionError):
        with conduit.managed_spell_meld(Resource):
            raise ConnectionError("block failed")
    assert pool_counts(Resource) == (1, 1, 0)


def test_probe_managed_wraps_an_object_already_held(make_root: Any) -> None:
    """ReleaseManagedSpell().managed(obj) leases a melded object and releases it on exit."""
    conduit = make_root((Resource, managed()))
    held = conduit.meld("Resource")
    with md.ReleaseManagedSpell().managed(held) as same:
        assert same is held
    assert pool_counts(Resource) == (1, 1, 0)


def test_probe_managed_spell_meld_refuses_another_existence(make_root: Any) -> None:
    """managed_spell_meld of a spell that is not managed raises ValueError before melding."""
    conduit = make_root((NotManaged, {"existence": md.Existence.many}))
    with pytest.raises(ValueError, match="leases a managed spell"):
        conduit.managed_spell_meld("NotManaged")


# ----------------------------------------------------------------------------------------
# Injection, request scopes and teardown (lesson 47)
# ----------------------------------------------------------------------------------------
def test_probe_each_injection_leases_and_a_request_scope_returns_it(make_root: Any) -> None:
    """Every injection is its own lease; a lesser scope's exit disposes the handlers, which release."""
    root = make_root(
        (Resource, managed(disposal_method_names=["close"])),
        (Handler, {"existence": md.Existence.many, "disposal_method_names": ["finish"]}),
    )
    with root.enter_lesser_conduit() as request:
        first = request.meld("Handler")
        second = request.meld("Handler")
        assert first.resource is not second.resource and pool_counts(Resource) == (2, 0, 2)
    assert first.finished and second.finished and pool_counts(Resource) == (2, 2, 0)


def test_probe_release_after_root_teardown_is_refused(make_root: Any) -> None:
    """After root teardown the registry no longer knows the class (ValueError); a lease raises RuntimeError."""
    root = make_root((Resource, managed(disposal_method_names=["close"])))
    melded = root.meld("Resource")
    lease = root.managed_spell_meld("Resource")
    root.cleanup()
    with pytest.raises(ValueError, match="not a managed spell class in any live root"):
        md.ReleaseManagedSpell().release(melded)
    with pytest.raises(RuntimeError, match="torn down with its root conduit"):
        lease.release()
    assert not melded.closed


def test_probe_root_teardown_cleans_pools_before_root_held_consumers(make_root: Any) -> None:
    """A root-held consumer that releases at its own disposal meets a pool already gone.

    Pins the teardown order the lesson warns about: the root store cleans its pools
    before its disposable registry, so the consumer's release fails and the root's
    teardown raises its disposal failures after finishing.
    """
    root = make_root(
        (Resource, managed()),
        (Handler, {"existence": md.Existence.many, "disposal_method_names": ["finish"]}),
    )
    handler = root.meld("Handler")
    with pytest.raises(ExceptionGroup):
        root.cleanup()
    assert handler.finished and not handler.resource.closed


def test_probe_purge_does_not_touch_a_pool(make_root: Any) -> None:
    """Conduit.purge returns 0 for a managed spell; SpellSpace.purge refuses it."""
    conduit = make_root((Resource, managed()))
    md.ReleaseManagedSpell().release(conduit.meld("Resource"))
    assert conduit.purge("Resource") == 0
    with conduit.enter_spellspace() as space:
        with pytest.raises(RuntimeError, match="Cannot purge spell"):
            space.purge("Resource")
    assert pool_counts(Resource) == (1, 1, 0)


# ----------------------------------------------------------------------------------------
# Registry routing and bind refusals
# ----------------------------------------------------------------------------------------
def test_probe_release_routing_refusals(make_root: Any) -> None:
    """Non-managed class, non-str spell_id, unmatched filter and a non-class describe are refused."""
    conduit = make_root((Resource, managed()), (NotManaged, {"existence": md.Existence.many}))
    with pytest.raises(ValueError, match="not a managed spell class"):
        md.ReleaseManagedSpell().release(conduit.meld("NotManaged"))
    obj = conduit.meld("Resource")
    with pytest.raises(TypeError, match="spell_id must be a str"):
        md.ReleaseManagedSpell().release(obj, spell_id=7)
    with pytest.raises(ValueError, match="No pool of managed class"):
        md.ReleaseManagedSpell().release(obj, spell_id="0" * 64)
    with pytest.raises(TypeError, match="describe takes a class"):
        md.ReleaseManagedSpell().describe("Resource")
    md.ReleaseManagedSpell().release(obj, conduit=conduit)
    assert pool_counts(Resource) == (1, 1, 0)


def _factory() -> Resource:
    """A function target, which a managed binding refuses."""
    return Resource()


@pytest.mark.parametrize(
    ("label", "target", "kwargs", "error"),
    [
        ("option on another existence", Resource, {"existence": "many", "managed_spell_limit": 3}, ValueError),
        ("function target", _factory, managed(), TypeError),
        ("limited without a limit", Resource, managed(managed_spell_mode="limited_quantity"), ValueError),
        ("queue without a timeout", Resource, managed(managed_spell_mode="queue", managed_spell_limit=1),
         ValueError),
        ("timeout on elastic", Resource, managed(managed_spell_timeout_seconds=1.0), ValueError),
        ("limit below one", Resource, managed(managed_spell_limit=0), ValueError),
        ("unknown mode", Resource, managed(managed_spell_mode="lifo"), ValueError),
        ("reset name not a method", Resource, managed(managed_spell_reset_methods=["rinse"]), ValueError),
        ("reset names as a string", Resource, managed(managed_spell_reset_methods="close"), TypeError),
    ],
)
def test_probe_bind_refuses_malformed_managed_bindings(
        label: str, target: Any, kwargs: Dict[str, Any], error: type,
) -> None:
    """Every malformed managed binding is refused at bind, next to the mistake."""
    book = md.Spellbook()
    try:
        with pytest.raises(error):
            book.bind(spell=target, **kwargs)
    finally:
        book.cleanup()


def test_probe_a_managed_spell_cannot_depend_on_a_shorter_scope() -> None:
    """Conjure refuses a managed spell that depends on unique_per_conduit (scope ordering)."""
    book = md.Spellbook()
    try:
        book.bind(spell=Scoped, existence=md.Existence.unique_per_conduit)
        book.bind(spell=DependsOnScoped, **managed())
        with pytest.raises(md.SpellbookValidationError, match="scope_ordering_violation"):
            book.conjure()
    finally:
        book.cleanup()


def test_probe_spellbinder_as_managed_spell_quantity() -> None:
    """SpellBinder stages the managed options; the pool carries them."""
    book = md.Spellbook()
    try:
        spell_id = (
            md.SpellBinder(book)
            .bind(Resettable)
            .as_managed_spell_quantity("limited_quantity", limit=3, reset_methods=["first"])
            .finalize()
        )
        conduit = book.conjure()
        try:
            md.ReleaseManagedSpell().release(conduit.meld(spell_id=spell_id))
            (snapshot,) = md.ReleaseManagedSpell().describe(Resettable)
            assert (snapshot["mode"], snapshot["limit"], snapshot["reset_method_names"]) == (
                "limited_quantity", 3, ["first"],
            )
        finally:
            conduit.cleanup()
    finally:
        book.cleanup()


# ----------------------------------------------------------------------------------------
# Dynamic posture: settings rebind and transfer (lesson 48)
# ----------------------------------------------------------------------------------------
def test_probe_a_settings_rebind_keeps_the_spell_id_and_the_pool(make_root: Any) -> None:
    """cleanup_spell + bind with another limit keeps the spell_id, the pool and its count."""
    root = make_root(dynamic=True, name="rebind-root")
    spell_id = root.bind(spell=Resource, **managed(managed_spell_mode="limited_quantity", managed_spell_limit=1))
    out = root.meld("Resource")
    root.cleanup_spell(spell=root.get_spell_by_spell_id(spell_id))
    rebound = root.bind(spell=Resource, **managed(managed_spell_mode="limited_quantity", managed_spell_limit=3))
    (snapshot,) = md.ReleaseManagedSpell().describe(Resource)
    assert rebound == spell_id and snapshot["limit"] == 3
    assert pool_counts(Resource) == (1, 0, 1)
    md.ReleaseManagedSpell().release_all([out, root.meld("Resource"), root.meld("Resource")])
    assert pool_counts(Resource) == (3, 3, 0)


def test_probe_a_transfer_moves_the_pool_with_its_idle_objects(make_root: Any) -> None:
    """transfer_spell_ownership moves the pool to the target root; the old owner cannot meld it."""
    source = make_root((Resource, managed()), dynamic=True, name="source-root")
    target = make_root(dynamic=True, name="target-root")
    spell_id = md.ReleaseManagedSpell().describe(Resource)[0]["spell_id"]
    obj = source.meld("Resource")
    md.ReleaseManagedSpell().release(obj)
    source.link(target)
    source.transfer_spell_ownership(spell=spell_id, target_conduit=target)
    (snapshot,) = md.ReleaseManagedSpell().describe(Resource)
    assert snapshot["holding_conduit_id"] == target.id and pool_counts(Resource) == (1, 1, 0)
    assert target.meld("Resource") is obj
    with pytest.raises(KeyError):
        source.meld("Resource")


def test_probe_release_managed_spell_is_one_process_singleton() -> None:
    """ReleaseManagedSpell() returns the one registry Aether built."""
    assert md.ReleaseManagedSpell() is md.ReleaseManagedSpell()
