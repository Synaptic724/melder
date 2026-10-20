"""Unit contracts for the managed site of key-set plans (managed_spell_quantity S5, 2026-10-15).

A step of `Existence.managed_spell_quantity` is leased from its pool: an inline pop, else a miss that reserves a
place, builds its children and the object (recording disposal-bearing `many` children with the object) and gives
the place back when the build fails. A lease taken for a holder that is never built goes back to its pool (F9).
Winning keys on the managed site's own parameters build a fresh object that is not pooled; a winning key on its
consumer's parameter removes the site.
"""

import threading
from collections import Counter
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import pytest

from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
    SitePlanRuntimeHelpers,
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.utilities.custom_exceptions.managed_spell_exhausted_error import ManagedSpellExhaustedError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError

Key = Tuple[str, Optional[int]]


class Store:
    """A root creations store with the attributes emitted plans read and write, and its managed pools."""

    def __init__(self) -> None:
        """Start empty."""
        self._creations: Dict[str, Any] = {}
        self._slot_guards: Dict[str, threading.RLock] = {}
        self._managed_quantities: Dict[str, ManagedSpellQuantity] = {}
        self.registered: List[Tuple[str, Any]] = []
        self.adoptions: List[Tuple[str, Any, Tuple[Tuple[str, Any], ...]]] = []

    def slot_guard(self, spell_id: str) -> threading.RLock:
        """Return one RLock per slot."""
        return self._slot_guards.setdefault(spell_id, threading.RLock())

    def add_creation(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                     disposal_methods: Optional[List[str]] = None) -> None:
        """Publish one singleton."""
        self._creations[key] = item

    def register_many(self, key: str, item: Any, disposal_methods: List[str]) -> None:
        """Record one disposal-bearing many instance."""
        self.registered.append((key, item))

    def adopt_children(self, holder_key: str, holder: Any, children: Tuple[Tuple[str, Any], ...]) -> None:
        """Record one adoption an emitted shared miss made."""
        self.adoptions.append((holder_key, holder, children))

    def get_managed_quantity(self, spell_id: str) -> Optional[ManagedSpellQuantity]:
        """Return the pool held under one spell_id, as `Creations.get_managed_quantity` does."""
        return self._managed_quantities.get(spell_id)


class Built:
    """One constructed object: its spell, its operands and the lifecycle calls made on it."""

    def __init__(self, name: str, args: Tuple[Any, ...], kwargs: Dict[str, Any],
                 journal: List[Tuple[str, str]], fail_close: bool) -> None:
        """Keep the operands and the shared journal."""
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self._journal = journal
        self._fail_close = fail_close

    def close(self) -> None:
        """Disposal method: journal the call, then raise when the world says so."""
        self._journal.append(("close", self.name))
        if self._fail_close:
            raise RuntimeError(f"{self.name} close failed")


class World:
    """One plan's spells, steps and topologies; the owner store holds the managed pools."""

    def __init__(self) -> None:
        """Start with no spell."""
        self.built: Counter = Counter()
        self.journal: List[Tuple[str, str]] = []
        self.raising: Dict[str, BaseException] = {}
        self.hooks: Dict[str, Callable[[], None]] = {}
        self.failing_close: Set[str] = set()
        self.owner_store = Store()
        self.conduit_store = Store()
        self.spells: Dict[str, SimpleNamespace] = {}
        self.steps: List[SitePlanStep] = []
        self.topologies: Dict[str, SpellLocalTopology] = {}

    def _factory(self, name: str) -> Callable[..., Built]:
        """Return a constructor that runs its hook, raises when asked, then counts the build."""

        def construct(*args: Any, **kwargs: Any) -> Built:
            hook = self.hooks.get(name)
            if hook is not None:
                hook()
            error = self.raising.get(name)
            if error is not None:
                raise error
            self.built[name] += 1
            return Built(name, args, kwargs, self.journal, name in self.failing_close)

        return construct

    def spell(self, name: str, existence: Existence = Existence.many, *, disposal: Tuple[str, ...] = (),
              mode: ManagedSpellMode = ManagedSpellMode.elastic, limit: Optional[int] = None,
              timeout: Optional[float] = None, dynamic: bool = False, owned: bool = True,
              pooled: bool = True) -> SimpleNamespace:
        """Register one fake spell; a managed one gets a real pool in the owner store unless asked not to."""
        managed = existence is Existence.managed_spell_quantity
        if managed and limit is None:
            limit = 256 if mode is ManagedSpellMode.elastic else 1
        spell = SimpleNamespace(
            spell=self._factory(name),
            spell_id=name,
            spell_index=SimpleNamespace(selected_spell_id=name),
            spell_name=name,
            binding_name=None,
            aetheric_frame="default",
            is_class_spell=True,
            is_method_spell=False,
            is_lambda_spell=False,
            is_existing_creation=False,
            has_disposal_methods=bool(disposal),
            disposal_method_names=list(disposal),
            existence=existence,
            managed_spell_mode=mode if managed else None,
            managed_spell_limit=limit,
            managed_spell_timeout_seconds=timeout,
            managed_spell_reset_methods=(),
            _lock=threading.RLock(),
            _owner_creations=self.owner_store if owned else None,
            _dynamic_environment=dynamic,
        )
        if managed and owned and pooled:
            self.owner_store._managed_quantities[name] = ManagedSpellQuantity(spell=spell, owner_conduit_id="root")
        self.spells[name] = spell
        return spell

    def step(self, key: Key, *deps: Tuple[str, Tuple[Key, ...]], plain: Tuple[str, ...] = (),
             unresolved: Tuple[str, ...] = (), collections: Tuple[str, ...] = (), lock_hint: bool = False) -> None:
        """Add one step; the spell's topology (dependencies, then plain, then unresolved) is made once."""
        spell = self.spells[key[0]]
        self.steps.append(SitePlanStep(
            instance_key=key,
            spell=spell,
            existence=spell.existence,
            dependency_resolution_order=tuple(deps),
            collection_param_names=frozenset(collections),
            uses_positional_override=False,
            contract_positional_override=None,
            has_contract_payload=False,
            contract_payload=None,
            use_spell_lock_hint=lock_hint,
        ))
        if key[0] in self.topologies:
            return
        sockets: List[SpellSocketDescriptor] = []
        names = [name for name, _ in deps] + list(plain) + list(unresolved)
        for position, name in enumerate(names):
            sockets.append(SpellSocketDescriptor(
                spell_id=key[0], param_name=name, position=position,
                socket_kind=SocketKind.UNRESOLVED_INPUT if name in unresolved else SocketKind.NORMAL,
                is_collection=name in collections, is_optional=name in plain, target_spell_ids=(),
                parameter_kind="POSITIONAL_OR_KEYWORD",
            ))
        topology = SpellLocalTopology(key[0], tuple(sockets))
        self.topologies[key[0]] = topology
        if unresolved:
            spell._spell_system_states = SimpleNamespace(get_local_topology=lambda index: topology)

    def plan(self, root: Key, keys: Tuple[str, ...] = (), *, arity: int = 0,
             door_route_key: Optional[str] = None) -> Tuple[Callable[..., Any], str, Dict[str, Any]]:
        """Emit and compile one plan (normal mode for the empty key set); return it, its source and namespace."""
        steps = tuple(self.steps)
        graph = SitePlanLowering.build_site_graph(
            root_spell_id=root[0], root_instance_key=root, steps=steps, topology_for=self.topologies.get,
        )
        try:
            resolution = OverrideKeyResolver.resolve(graph, keys, arity)
            source, namespace, _ = SitePlanLowering.emit(
                steps=steps, site_graph=graph, resolution=resolution, root_instance_key=root,
                root_spell_id=root[0], root_spell_name=root[0], arity=arity,
                normal_mode=not keys and not arity, door_route_key=door_route_key,
            )
        finally:
            graph.cleanup()
        exec(compile(source, "<test>", "exec"), namespace)
        return namespace[SitePlanLowering.PLAN_FUNCTION_NAME], source, namespace

    def meld(self) -> SimpleNamespace:
        """Return the meld a plan reads its stores from (no spellspace)."""
        return SimpleNamespace(_conduit_creations=self.conduit_store, _spellspace_creations=None)

    def pool(self, name: str) -> ManagedSpellQuantity:
        """Return one managed spell's pool."""
        return self.owner_store._managed_quantities[name]

    def idle(self, name: str) -> int:
        """Return how many objects one managed spell's pool holds idle."""
        return self.pool(name).describe()["idle_count"]


class FakePool:
    """A pool stand-in for the return helpers: records put-backs or raises the given failure."""

    def __init__(self, spell_name: str, failure: Optional[Exception] = None) -> None:
        """Keep the name the helpers report and the failure to raise."""
        self.spell_name = spell_name
        self.returned: List[Any] = []
        self._failure = failure

    def put_back(self, obj: Any) -> None:
        """Record the object, or raise the failure."""
        if self._failure is not None:
            raise self._failure
        self.returned.append(obj)


def _root_world(**options: Any) -> World:
    """One managed root M."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity, **options)
    world.step(("m", None))
    return world


def _consumer_world(consumer: Existence = Existence.many, **options: Any) -> World:
    """R(m: M): M managed, R `many` unless asked."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity, **options)
    world.spell("r", consumer)
    world.step(("m", 1))
    world.step(("r", None), ("m", (("m", 1),)))
    return world


def _two_lease_world(**second: Any) -> World:
    """R(a: M1, b: M2): two managed sites feeding one many holder."""
    world = World()
    world.spell("m1", Existence.managed_spell_quantity)
    world.spell("m2", Existence.managed_spell_quantity, **second)
    world.spell("r")
    world.step(("m1", 1))
    world.step(("m2", 2))
    world.step(("r", None), ("a", (("m1", 1),)), ("b", (("m2", 2),)))
    return world


def _chain_world() -> World:
    """M1(m2: M2): a managed root holding a managed dependency."""
    world = World()
    world.spell("m2", Existence.managed_spell_quantity)
    world.spell("m1", Existence.managed_spell_quantity)
    world.step(("m2", 1))
    world.step(("m1", None), ("m2", (("m2", 1),)))
    return world


def _children_world(disposal: Tuple[str, ...] = ("close",)) -> World:
    """M(x: X): a managed root with one `many` child."""
    world = World()
    world.spell("x", disposal=disposal)
    world.spell("m", Existence.managed_spell_quantity)
    world.step(("x", 1))
    world.step(("m", None), ("x", (("x", 1),)))
    return world


# --- Emitted shapes ---------------------------------------------------------------------------------------------


def test_root_lease_pops_the_pool_bound_as_a_plan_constant() -> None:
    """An automatic owner's pool is bound at emission: the warm lease is `pp0()` and no store is read."""
    world = _root_world()
    _, source, namespace = world.plan(("m", None))
    assert "v0 = pp0()" in source
    assert "except IndexError:" in source
    assert "_owner_creations" not in source
    assert namespace["h0"] is world.pool("m")


def test_dynamic_owner_reads_its_pool_on_every_creation() -> None:
    """In a dynamic environment a transfer can move the pool, so the plan reads it per creation."""
    world = _root_world(dynamic=True)
    plan, source, namespace = world.plan(("m", None))
    assert "h0 = spells[0]._owner_creations._managed_quantities[sid0]" in source
    assert "v0 = h0._idle.pop()" in source
    assert "h0" not in namespace and "pp0" not in namespace
    assert plan(world.meld()).name == "m"
    assert world.pool("m").count == 1


def test_unowned_version_raises_the_missing_pool_error() -> None:
    """A version with no owner store has no pool: the named error, nothing built."""
    world = _root_world(owned=False)
    plan, _, _ = world.plan(("m", None))
    with pytest.raises(MeldExecutionError, match="Managed spell 'm' has no pool to lease from"):
        plan(world.meld())
    assert world.built == Counter()


def test_owner_store_without_the_pool_raises_the_missing_pool_error() -> None:
    """An owner store holding no pool under the id reads per creation and raises the named error."""
    world = _root_world(pooled=False)
    plan, source, _ = world.plan(("m", None))
    assert "_managed_quantities[sid0]" in source
    with pytest.raises(MeldExecutionError, match="its owner store holds no pool for this version"):
        plan(world.meld())


def test_plan_without_a_managed_site_binds_no_managed_helper() -> None:
    """A plan with no managed step keeps today's namespace and source."""
    world = World()
    world.spell("x")
    world.spell("r", Existence.unique_per_conduit)
    world.step(("x", 1))
    world.step(("r", None), ("x", (("x", 1),)))
    _, source, namespace = world.plan(("r", None))
    assert not {"_return_leases", "_return_unused_leases", "_raise_missing_managed_pool"} & set(namespace)
    assert "reserve" not in source and "_return" not in source


def test_managed_plan_binds_the_three_runtime_helpers() -> None:
    """A plan with a leasing site binds the return helpers and the missing-pool error."""
    world = _root_world()
    _, _, namespace = world.plan(("m", None))
    assert namespace["_return_leases"] is SitePlanRuntimeHelpers.return_leases
    assert namespace["_return_unused_leases"] is SitePlanRuntimeHelpers.return_unused_leases
    assert namespace["_raise_missing_managed_pool"] is SitePlanRuntimeHelpers.raise_missing_managed_pool


def test_lease_is_taken_right_before_its_consumer_is_built() -> None:
    """R(m: M, b: B): B is built first, then M is leased, then R - nothing runs between lease and use."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("b")
    world.spell("r")
    world.step(("m", 1))
    world.step(("b", 2))
    world.step(("r", None), ("m", (("m", 1),)), ("b", (("b", 2),)))
    _, source, _ = world.plan(("r", None))
    assert source.index("v1 = t1(") < source.index("v0 = pp0()") < source.index("v2 = t2(")


def test_leasing_site_with_two_consumers_is_refused_at_emission() -> None:
    """A managed site is per path; one key feeding two consumers is an emission error."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("a")
    world.spell("r")
    world.step(("m", 1))
    world.step(("a", 2), ("m", (("m", 1),)))
    world.step(("r", None), ("m", (("m", 1),)), ("a", (("a", 2),)))
    with pytest.raises(RuntimeError, match="consumers"):
        world.plan(("r", None))


def test_override_plan_passes_ov_through_the_managed_miss() -> None:
    """An override plan's managed miss takes `ov` like every miss."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("r")
    world.step(("m", 1))
    world.step(("r", None), ("m", (("m", 1),)), plain=("limit",))
    plan, source, _ = world.plan(("r", None), ("limit",))
    assert "_miss0(meld, ov, h0)" in source
    holder = plan(world.meld(), {"limit": 4})
    assert holder.kwargs["limit"] == 4 and holder.kwargs["m"].name == "m"


# --- The root lease ---------------------------------------------------------------------------------------------


def test_root_lease_builds_into_a_reserved_place_on_an_empty_pool() -> None:
    """An empty pool misses: one place reserved, the object built and handed out."""
    world = _root_world()
    plan, _, _ = world.plan(("m", None))
    assert plan(world.meld()).name == "m"
    assert (world.pool("m").count, world.idle("m"), world.built["m"]) == (1, 0, 1)


def test_released_object_is_leased_again_without_a_build() -> None:
    """A put-back object is the next lease."""
    world = _root_world()
    plan, _, _ = world.plan(("m", None))
    first = plan(world.meld())
    world.pool("m").put_back(first)
    assert plan(world.meld()) is first
    assert world.built["m"] == 1


def test_limited_pool_at_its_limit_refuses_before_building() -> None:
    """limited_quantity at its limit raises the exhaustion error and builds nothing."""
    world = _root_world(mode=ManagedSpellMode.limited_quantity, limit=1)
    plan, _, _ = world.plan(("m", None))
    plan(world.meld())
    with pytest.raises(ManagedSpellExhaustedError):
        plan(world.meld())
    assert (world.built["m"], world.pool("m").count) == (1, 1)


def test_constant_pool_torn_down_with_its_root_fails_at_reserve() -> None:
    """A retired pool's drained deque misses and `reserve` raises the pool's own error."""
    world = _root_world()
    plan, _, _ = world.plan(("m", None))
    world.pool("m").cleanup()
    with pytest.raises(RuntimeError, match="was torn down with its root conduit"):
        plan(world.meld())
    assert world.built == Counter()


def test_miss_returns_an_object_reserve_serves_without_building() -> None:
    """When `reserve` serves an idle object the miss returns it unbuilt."""
    world = _root_world(mode=ManagedSpellMode.limited_quantity, limit=1)
    plan, _, namespace = world.plan(("m", None))
    first = plan(world.meld())
    pool = world.pool("m")
    pool.put_back(first)
    assert namespace["_miss0"](world.meld(), pool) is first
    assert (world.built["m"], pool.count) == (1, 1)


def test_queue_lease_waits_and_is_served_by_a_release() -> None:
    """A queue lease at its limit waits; the release serves it the same object, no build."""
    world = _root_world(mode=ManagedSpellMode.queue, limit=1, timeout=10.0)
    plan, _, _ = world.plan(("m", None))
    first = plan(world.meld())
    received: List[Any] = []
    waiter = threading.Thread(target=lambda: received.append(plan(world.meld())))
    waiter.start()
    world.pool("m").put_back(first)
    waiter.join(timeout=15)
    assert received == [first] and world.built["m"] == 1


# --- Holders and the return of leases (F9) ----------------------------------------------------------------------


def test_many_consumer_receives_a_leased_object() -> None:
    """R(m: M): R is built with the pool's object; a released object is injected again."""
    world = _consumer_world()
    plan, _, _ = world.plan(("r", None))
    leased = plan(world.meld()).kwargs["m"]
    assert leased.name == "m" and (world.pool("m").count, world.idle("m")) == (1, 0)
    world.pool("m").put_back(leased)
    assert plan(world.meld()).kwargs["m"] is leased


def test_each_injection_path_takes_its_own_lease() -> None:
    """Two parameters fed by one managed spell get two objects (one site per path)."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("r")
    world.step(("m", 1))
    world.step(("m", 2))
    world.step(("r", None), ("first", (("m", 1),)), ("second", (("m", 2),)))
    plan, _, _ = world.plan(("r", None))
    holder = plan(world.meld())
    assert holder.kwargs["first"] is not holder.kwargs["second"]
    assert world.pool("m").count == 2


def test_raising_consumer_returns_its_lease_to_the_pool() -> None:
    """A holder whose constructor raises gives its lease back; the object stays alive and idle."""
    world = _consumer_world()
    world.raising["r"] = ValueError("holder failed")
    plan, _, _ = world.plan(("r", None))
    with pytest.raises(MeldExecutionError):
        plan(world.meld())
    assert (world.pool("m").count, world.idle("m"), world.built["r"]) == (1, 1, 0)


def test_failed_sibling_build_returns_the_lease_taken_before_it() -> None:
    """R(a: M1, b: M2): M2's build raises, M1's lease goes back, M2's place is freed."""
    world = _two_lease_world()
    world.raising["m2"] = ValueError("second failed")
    plan, _, _ = world.plan(("r", None))
    with pytest.raises(MeldExecutionError):
        plan(world.meld())
    assert (world.pool("m1").count, world.idle("m1")) == (1, 1)
    assert (world.pool("m2").count, world.idle("m2")) == (0, 0)


def test_exhausted_sibling_returns_the_lease_taken_before_it() -> None:
    """R(a: M1, b: M2): M2 refuses at its limit, M1's lease goes back."""
    world = _two_lease_world(mode=ManagedSpellMode.limited_quantity, limit=1)
    world.pool("m2").reserve()
    plan, _, _ = world.plan(("r", None))
    with pytest.raises(ManagedSpellExhaustedError):
        plan(world.meld())
    assert world.idle("m1") == 1 and world.built["m2"] == 0


def test_failed_return_is_a_note_on_the_propagating_error() -> None:
    """A put-back that fails while the holder's error propagates becomes a note on that error."""
    world = _consumer_world()
    plan, _, _ = world.plan(("r", None))
    world.hooks["r"] = world.pool("m").cleanup
    world.raising["r"] = ValueError("holder failed")
    with pytest.raises(MeldExecutionError) as caught:
        plan(world.meld())
    notes = getattr(caught.value, "__notes__", [])
    assert any(note.startswith("Returning an object leased from managed spell 'm' failed:") for note in notes)


def test_shared_consumer_is_built_with_a_lease_and_stored() -> None:
    """U(m: M) per conduit: U is built with M's object and published."""
    world = _consumer_world(Existence.unique_per_conduit)
    plan, source, _ = world.plan(("r", None))
    holder = plan(world.meld())
    assert world.conduit_store._creations["r"] is holder
    assert holder.kwargs["m"].name == "m" and world.pool("m").count == 1
    assert "_return_unused_leases" in source


def test_stored_shared_consumer_takes_no_new_lease() -> None:
    """A stored holder is reused without touching the pool."""
    world = _consumer_world(Existence.unique_per_conduit)
    plan, _, _ = world.plan(("r", None))
    holder = plan(world.meld())
    assert plan(world.meld()) is holder
    assert (world.pool("m").count, world.idle("m"), world.built["m"]) == (1, 0, 1)


def test_shared_consumer_losing_its_cold_race_returns_its_lease() -> None:
    """Another meld publishes U first: the plan returns that U and puts its unused lease back."""
    world = _consumer_world(Existence.unique_per_conduit)
    plan, _, _ = world.plan(("r", None))
    winner = object()
    world.hooks["m"] = lambda: world.conduit_store._creations.__setitem__("r", winner)
    assert plan(world.meld()) is winner
    assert (world.pool("m").count, world.idle("m"), world.built["r"]) == (1, 1, 0)


def test_lost_race_return_failures_raise_one_group() -> None:
    """After a lost race every unused lease is tried, then the failures are raised as one group."""
    world = _consumer_world(Existence.unique_per_conduit)
    plan, _, _ = world.plan(("r", None))
    pool = world.pool("m")

    def race() -> None:
        world.conduit_store._creations["r"] = object()
        pool.cleanup()

    world.hooks["m"] = race
    with pytest.raises(ExceptionGroup, match="another meld finished first") as caught:
        plan(world.meld())
    assert len(caught.value.exceptions) == 1
    assert "managed spell 'm'" in str(caught.value.exceptions[0])


def test_pinned_shared_consumer_refusal_returns_its_lease() -> None:
    """A pinned holder found stored at its recheck refuses (P2) and its lease goes back."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("r", Existence.unique_per_conduit)
    world.step(("m", 1))
    world.step(("r", None), ("m", (("m", 1),)), plain=("limit",))
    plan, _, _ = world.plan(("r", None), ("limit",))
    world.hooks["m"] = lambda: world.conduit_store._creations.__setitem__("r", object())
    with pytest.raises(MeldExecutionError, match="already exists"):
        plan(world.meld(), {"limit": 3})
    assert world.idle("m") == 1


def test_door_held_root_leases_inside_its_unguarded_miss() -> None:
    """A door-held per-conduit root takes no guard of its own; its lease group is unchanged."""
    world = _consumer_world(Existence.unique_per_conduit)
    plan, source, _ = world.plan(("r", None), door_route_key="unique_per_conduit")
    assert "with " not in source
    holder = plan(world.meld())
    assert world.conduit_store._creations["r"] is holder and holder.kwargs["m"].name == "m"


def test_unique_holder_leases_inside_its_spell_lock_guard() -> None:
    """R(u: U(m: M)), U `unique` with the lock hint: U leases once and is reused."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("u", Existence.unique)
    world.spell("r")
    world.step(("m", 1))
    world.step(("u", None), ("m", (("m", 1),)), lock_hint=True)
    world.step(("r", None), ("u", (("u", None),)))
    plan, source, _ = world.plan(("r", None))
    assert "with spells[1]._lock:" in source
    first = plan(world.meld())
    assert plan(world.meld()).kwargs["u"] is first.kwargs["u"]
    assert world.owner_store._creations["u"] is first.kwargs["u"] and world.pool("m").count == 1


def test_managed_holder_leases_its_managed_dependency_on_a_miss() -> None:
    """M1(m2: M2): a missed M1 leases M2 inside its own miss."""
    world = _chain_world()
    plan, _, _ = world.plan(("m1", None))
    assert plan(world.meld()).kwargs["m2"].name == "m2"
    assert (world.pool("m1").count, world.pool("m2").count) == (1, 1)


def test_raising_managed_holder_returns_its_lease_and_its_place() -> None:
    """M1's constructor raises: M2's object goes back, M1's place is freed."""
    world = _chain_world()
    world.raising["m1"] = ValueError("holder failed")
    plan, _, _ = world.plan(("m1", None))
    with pytest.raises(MeldExecutionError):
        plan(world.meld())
    assert (world.pool("m1").count, world.pool("m2").count, world.idle("m2")) == (0, 1, 1)


def test_pooled_managed_holder_is_leased_without_leasing_its_dependency_again() -> None:
    """A released M1 keeps its M2: the next lease touches only M1's pool."""
    world = _chain_world()
    plan, _, _ = world.plan(("m1", None))
    holder = plan(world.meld())
    world.pool("m1").put_back(holder)
    assert plan(world.meld()) is holder
    assert (world.pool("m2").count, world.idle("m2"), world.built["m2"]) == (1, 0, 1)


# --- Children of a managed object -------------------------------------------------------------------------------


def test_managed_miss_records_disposal_bearing_children_with_the_object() -> None:
    """M(x: X): X is recorded with M's object (never registered in a store) and disposed with it."""
    world = _children_world()
    plan, source, _ = world.plan(("m", None))
    obj = plan(world.meld())
    assert "kids1.append((v0, dm0))" in source
    assert world.conduit_store.registered == [] and world.owner_store.registered == []
    pool = world.pool("m")
    assert pool.describe()["children_recorded"] == 1
    pool.put_back(obj)
    pool.cleanup()
    assert world.journal == [("close", "x")]


def test_raising_managed_constructor_disposes_the_children_built_for_it() -> None:
    """M's constructor raises: the place is freed and X is disposed."""
    world = _children_world()
    world.raising["m"] = ValueError("object failed")
    plan, _, _ = world.plan(("m", None))
    with pytest.raises(MeldExecutionError):
        plan(world.meld())
    assert world.journal == [("close", "x")] and world.pool("m").count == 0


def test_raising_child_gives_the_reserved_place_back() -> None:
    """X raises: M is never built and its place is freed."""
    world = _children_world()
    world.raising["x"] = ValueError("child failed")
    plan, _, _ = world.plan(("m", None))
    with pytest.raises(MeldExecutionError):
        plan(world.meld())
    assert (world.pool("m").count, world.built["m"]) == (0, 0)


def test_child_disposal_failure_becomes_a_note_on_the_build_error() -> None:
    """A child that fails to dispose during the abandon adds a note to the build's error."""
    world = _children_world()
    world.failing_close.add("x")
    world.raising["m"] = ValueError("object failed")
    plan, _, _ = world.plan(("m", None))
    with pytest.raises(MeldExecutionError) as caught:
        plan(world.meld())
    notes = getattr(caught.value, "__notes__", [])
    assert any("Disposing a child built for the failed object of managed spell 'm'" in note for note in notes)


def test_children_without_disposal_methods_are_not_recorded() -> None:
    """A child without disposal methods needs no record: no kids list, an empty abandon."""
    world = _children_world(disposal=())
    plan, source, _ = world.plan(("m", None))
    plan(world.meld())
    assert "kids" not in source and "abandon([], exc)" in source
    assert world.pool("m").describe()["children_recorded"] == 0


def test_shared_child_of_a_managed_object_publishes_to_its_own_store() -> None:
    """M(u: U) per conduit: U is published to its store, not recorded with M."""
    world = World()
    world.spell("u", Existence.unique_per_conduit)
    world.spell("m", Existence.managed_spell_quantity)
    world.step(("u", None))
    world.step(("m", None), ("u", (("u", None),)))
    plan, _, _ = world.plan(("m", None))
    obj = plan(world.meld())
    assert world.conduit_store._creations["u"] is obj.kwargs["u"]
    assert world.pool("m").describe()["children_recorded"] == 0


# --- Overrides, unresolved inputs and collections ---------------------------------------------------------------


def test_supplied_consumer_parameter_takes_no_lease() -> None:
    """A winning key on R's parameter removes the managed site: no lease, the pool untouched."""
    world = _consumer_world()
    plan, source, _ = world.plan(("r", None), ("m",))
    supplied = object()
    assert plan(world.meld(), {"m": supplied}).kwargs["m"] is supplied
    assert world.pool("m").count == 0 and "pp0" not in source


def test_keys_on_the_managed_sites_own_parameters_build_a_fresh_unpooled_object() -> None:
    """A winning key on M's own parameter builds M fresh each meld; it is never pooled or counted."""
    world = World()
    world.spell("x")
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("r")
    world.step(("x", 2))
    world.step(("m", 1), ("x", (("x", 2),)))
    world.step(("r", None), ("m", (("m", 1),)))
    plan, _, namespace = world.plan(("r", None), ("m>x",))
    first = plan(world.meld(), {"m>x": "one"}).kwargs["m"]
    second = plan(world.meld(), {"m>x": "two"}).kwargs["m"]
    assert (first.kwargs["x"], second.kwargs["x"]) == ("one", "two") and first is not second
    assert world.pool("m").count == 0 and "_return_leases" not in namespace


def test_fresh_managed_root_built_from_a_positional_payload_is_not_pooled() -> None:
    """`__args__` supplies the managed root's parameter: built fresh, never pooled."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.step(("m", None), plain=("size",))
    plan, _, _ = world.plan(("m", None), ("__args__",), arity=1)
    assert plan(world.meld(), {"__args__": [5]}).args == (5,)
    assert world.pool("m").count == 0


def test_deeper_key_under_a_leasing_site_applies_only_when_it_misses() -> None:
    """R(m: M(y: Y(x))) with `m>y>x`: a pooled M is reused whatever x is supplied."""
    world = World()
    world.spell("y")
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("r")
    world.step(("y", 2), plain=("x",))
    world.step(("m", 1), ("y", (("y", 2),)))
    world.step(("r", None), ("m", (("m", 1),)))
    plan, _, _ = world.plan(("r", None), ("m>y>x",))
    first = plan(world.meld(), {"m>y>x": "one"}).kwargs["m"]
    world.pool("m").put_back(first)
    assert plan(world.meld(), {"m>y>x": "two"}).kwargs["m"] is first
    assert first.kwargs["y"].kwargs["x"] == "one"


def test_unresolved_input_of_a_leasing_site_raises_before_taking_a_place() -> None:
    """M(work) unsupplied: the miss raises before `reserve`."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.step(("m", None), unresolved=("work",))
    plan, _, _ = world.plan(("m", None))
    with pytest.raises(UnresolvedInputError):
        plan(world.meld())
    assert world.pool("m").count == 0


def test_supplying_a_leasing_sites_unresolved_input_builds_it_fresh() -> None:
    """A key on M's unresolved input is a key on its own parameter: M is built fresh with it."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("r")
    world.step(("m", 1), unresolved=("work",))
    world.step(("r", None), ("m", (("m", 1),)))
    plan, _, _ = world.plan(("r", None), ("m>work",))
    assert plan(world.meld(), {"m>work": "job"}).kwargs["m"].kwargs["work"] == "job"
    assert world.pool("m").count == 0


def test_unresolved_input_of_a_child_raises_in_the_managed_miss_before_reserve() -> None:
    """M(x: X(work)): the miss raises for X before reserving or building anything."""
    world = World()
    world.spell("x")
    world.spell("m", Existence.managed_spell_quantity)
    world.step(("x", 1), unresolved=("work",))
    world.step(("m", None), ("x", (("x", 1),)))
    plan, _, _ = world.plan(("m", None))
    with pytest.raises(UnresolvedInputError):
        plan(world.meld())
    assert world.pool("m").count == 0 and world.built == Counter()


def test_collection_parameter_leases_each_managed_member() -> None:
    """R(items: [M, M]): two leases, one list."""
    world = World()
    world.spell("m", Existence.managed_spell_quantity)
    world.spell("r")
    world.step(("m", 1))
    world.step(("m", 2))
    world.step(("r", None), ("items", (("m", 1), ("m", 2))), collections=("items",))
    plan, _, _ = world.plan(("r", None))
    items = plan(world.meld()).kwargs["items"]
    assert [item.name for item in items] == ["m", "m"] and items[0] is not items[1]
    assert world.pool("m").count == 2


def test_failed_collection_member_returns_the_members_leased_before_it() -> None:
    """R(items: [M1, M2]): M2's build raises and M1's lease goes back."""
    world = World()
    world.spell("m1", Existence.managed_spell_quantity)
    world.spell("m2", Existence.managed_spell_quantity)
    world.spell("r")
    world.step(("m1", 1))
    world.step(("m2", 2))
    world.step(("r", None), ("items", (("m1", 1), ("m2", 2))), collections=("items",))
    world.raising["m2"] = ValueError("member failed")
    plan, _, _ = world.plan(("r", None))
    with pytest.raises(MeldExecutionError):
        plan(world.meld())
    assert world.idle("m1") == 1


# --- Runtime helpers --------------------------------------------------------------------------------------------


def test_return_leases_puts_back_taken_leases_and_skips_the_rest() -> None:
    """Taken leases go back; a lease never taken (None) is skipped; no note on success."""
    first, second = FakePool("a"), FakePool("b")
    error = ValueError("consumer failed")
    obj = object()
    SitePlanRuntimeHelpers.return_leases(error, ((first, obj), (second, None)))
    assert first.returned == [obj] and second.returned == []
    assert getattr(error, "__notes__", []) == []


def test_return_leases_records_each_failed_return_as_a_note() -> None:
    """A failing put-back becomes one note naming the spell and the failure; the others still run."""
    failing, healthy = FakePool("a", RuntimeError("torn down")), FakePool("b")
    error = ValueError("consumer failed")
    obj = object()
    SitePlanRuntimeHelpers.return_leases(error, ((failing, object()), (healthy, obj)))
    assert error.__notes__ == ["Returning an object leased from managed spell 'a' failed: torn down"]
    assert healthy.returned == [obj]


def test_return_unused_leases_tries_every_return_then_raises_one_group() -> None:
    """After a lost race every lease is tried; the failures are raised together."""
    failing, healthy = FakePool("a", RuntimeError("torn down")), FakePool("b")
    obj = object()
    with pytest.raises(ExceptionGroup) as caught:
        SitePlanRuntimeHelpers.return_unused_leases(((failing, object()), (healthy, obj)))
    assert healthy.returned == [obj]
    assert caught.value.message == "Returning objects leased for a construction another meld finished first failed"
    assert [str(failure) for failure in caught.value.exceptions] == [
        "Returning an object leased from managed spell 'a' failed: torn down"
    ]
    assert isinstance(caught.value.exceptions[0].__cause__, RuntimeError)


def test_return_unused_leases_without_failures_returns_quietly() -> None:
    """Every lease goes back and nothing is raised."""
    pool = FakePool("a")
    objects = (object(), object())
    SitePlanRuntimeHelpers.return_unused_leases(((pool, objects[0]), (pool, objects[1])))
    assert pool.returned == list(objects)


def test_raise_missing_managed_pool_names_the_spell_and_the_remedy() -> None:
    """The named error says what has no pool, why, and what to do."""
    spell = SimpleNamespace(spell_id="sid", spell_name="Logger", spell_index=SimpleNamespace(selected_spell_id="sid"))
    with pytest.raises(MeldExecutionError) as caught:
        SitePlanRuntimeHelpers.raise_missing_managed_pool(spell)
    assert "Managed spell 'Logger' has no pool to lease from: its owner root was torn down" in str(caught.value)
    assert "Meld it through a live root that owns it." in str(caught.value)
    # 0.2.8248: conjure wires a version staged before it, so staging is neither a cause nor a remedy any more.
    assert "bind_inactive" not in str(caught.value)
    assert "stage the version after conjure" not in str(caught.value)
