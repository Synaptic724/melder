"""
Unit contracts for the door-held root of the normal site plan (0.2.73).

WHAT IS BEING CLAIMED
---------------------
A CreationContext route door holds its root's slot guard from its recheck until
the normal plan returns. For the "unique_per_conduit" and "spellspace" routes the
normal plan therefore builds the root without taking that guard a second time,
while every other site, every other root, every override key-set plan and every
plan emitted without a door route keep their guard. The root still rechecks its
store after its children are built.

These tests drive `SitePlanLowering.emit` and `SitePlanOverrideRuntime` with
recording stand-in stores, so the lock discipline of the emitted code is observed
directly. The real doors and real stores are covered by
tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py.
"""

import threading
from collections import Counter
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_override_runtime import (
    SitePlanOverrideRuntime,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)

Event = Tuple[str, str]
Key = Tuple[str, Optional[int]]


class RecordingLock:
    """A build-lock stand-in that records every acquire and release in a shared event list."""

    def __init__(self, name: str, events: List[Event]) -> None:
        """
        Keep the slot name and the event list.

        Args:
            name: Spell id of the slot this lock guards.
            events: Shared, ordered event log.
        """
        self._name: str = name
        self._events: List[Event] = events

    def __enter__(self) -> "RecordingLock":
        """Record the acquire."""
        self._events.append(("acquire", self._name))
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Record the release; exceptions propagate."""
        self._events.append(("release", self._name))


class RecordingStore:
    """A creations store with the attributes emitted plans read and write, and recording slot guards."""

    def __init__(self, events: List[Event]) -> None:
        """
        Start empty.

        Args:
            events: Shared, ordered event log for guard and disposal activity.
        """
        self._events: List[Event] = events
        self._creations: Dict[str, Any] = {}
        self._slot_guards: Dict[str, RecordingLock] = {}

    def slot_guard(self, spell_id: str) -> RecordingLock:
        """Return one recording lock per slot, created on first use."""
        return self._slot_guards.setdefault(spell_id, RecordingLock(spell_id, self._events))

    def add_creation(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                     disposal_methods: Optional[List[str]] = None) -> None:
        """Publish one singleton and record the disposal-bearing registration."""
        self._creations[key] = item
        self._events.append(("add_creation", key))


class ClusterFacade:
    """The `_cluster_creations` stand-in: resolves to one fixed leader store."""

    def __init__(self, store: RecordingStore) -> None:
        """
        Keep the leader store.

        Args:
            store: The store every resolution returns.
        """
        self._store: RecordingStore = store

    def resolved_store(self) -> RecordingStore:
        """Return the leader store."""
        return self._store


def logging_spell(spell_id: str, events: List[Event], existence: Existence,
                  owner_store: Optional[RecordingStore] = None,
                  disposal: Tuple[str, ...] = ()) -> SimpleNamespace:
    """
    Build a fake spell whose constructor records its build in `events`.

    Args:
        spell_id: Id, name and selected id of the spell.
        events: Shared, ordered event log.
        existence: The spell's Existence.
        owner_store: The `unique` owner store, when the test routes one.
        disposal: Declared disposal method names.

    Returns:
        SimpleNamespace: The fake spell.
    """

    def construct(*args: Any, **kwargs: Any) -> SimpleNamespace:
        events.append(("build", spell_id))
        return SimpleNamespace(name=spell_id, args=args, kwargs=kwargs)

    return SimpleNamespace(
        spell=construct,
        spell_id=spell_id,
        spell_index=SimpleNamespace(selected_spell_id=spell_id),
        spell_name=spell_id,
        is_class_spell=True,
        is_method_spell=False,
        is_lambda_spell=False,
        is_existing_creation=False,
        has_disposal_methods=bool(disposal),
        disposal_method_names=list(disposal),
        existence=existence,
        _lock=threading.RLock(),
        _owner_creations=owner_store,
    )


def plan_step(key: Key, spell: SimpleNamespace, *deps: Tuple[str, Tuple[Key, ...]]) -> SitePlanStep:
    """Build one step view (no collections, contract payload or lock hint)."""
    return SitePlanStep(
        instance_key=key,
        spell=spell,
        existence=spell.existence,
        dependency_resolution_order=tuple(deps),
        collection_param_names=frozenset(),
        uses_positional_override=False,
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        use_spell_lock_hint=False,
    )


def socket(spell_id: str, name: str, position: int, optional: bool = False) -> SpellSocketDescriptor:
    """Build one Phase-3 socket descriptor."""
    return SpellSocketDescriptor(
        spell_id=spell_id, param_name=name, position=position, socket_kind=SocketKind.NORMAL,
        is_collection=False, is_optional=optional, target_spell_ids=(), parameter_kind="POSITIONAL_OR_KEYWORD",
    )


class World:
    """Root(s: S, limit=3) where S is a unique_per_conduit child; the root's Existence varies per test."""

    def __init__(self, root_existence: Existence, root_disposal: Tuple[str, ...] = ()) -> None:
        """
        Build stores, spells, steps and topologies.

        Args:
            root_existence: Existence of the root spell.
            root_disposal: Disposal method names declared by the root.
        """
        self.events: List[Event] = []
        self.conduit_store = RecordingStore(self.events)
        self.space_store = RecordingStore(self.events)
        self.lineage_store = RecordingStore(self.events)
        self.cluster_store = RecordingStore(self.events)
        self.owner_store = RecordingStore(self.events)
        self.child = logging_spell("s", self.events, Existence.unique_per_conduit)
        self.root = logging_spell("root", self.events, root_existence, self.owner_store, root_disposal)
        self.steps = (
            plan_step(("s", None), self.child),
            plan_step(("root", None), self.root, ("s", (("s", None),))),
        )
        self.topologies = {
            "root": SpellLocalTopology("root", (socket("root", "s", 0), socket("root", "limit", 1, optional=True))),
            "s": SpellLocalTopology("s", ()),
        }
        self.root._spellbook = SimpleNamespace(
            _spell_system_states=SimpleNamespace(get_local_topology_by_id=self.topologies.get)
        )

    def meld(self) -> SimpleNamespace:
        """Return a meld stand-in exposing every store route the lowering reads."""
        return SimpleNamespace(
            _conduit_creations=self.conduit_store,
            _spellspace_creations=self.space_store,
            _root_creations=self.lineage_store,
            _cluster_creations=ClusterFacade(self.cluster_store),
        )

    def normal_plan(self, door_route_key: Optional[str]) -> Callable[[Any], Any]:
        """Emit and compile the normal plan for one door route key."""
        graph = SitePlanLowering.build_site_graph(
            root_spell_id="root", root_instance_key=("root", None), steps=self.steps,
            topology_for=self.topologies.get,
        )
        source, namespace, _ = SitePlanLowering.emit(
            steps=self.steps, site_graph=graph, resolution=OverrideKeyResolver.resolve(graph, ()),
            root_instance_key=("root", None), root_spell_id="root", root_spell_name="root", arity=0,
            normal_mode=True, door_route_key=door_route_key,
        )
        graph.cleanup()
        exec(compile(source, "<test>", "exec"), namespace)
        plan: Callable[[Any], Any] = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
        return plan


CHILD_EVENTS: List[Event] = [("acquire", "s"), ("build", "s"), ("release", "s")]


@pytest.mark.parametrize(
    ("door_route_key", "root_existence", "store_name"),
    [
        pytest.param("unique_per_conduit", Existence.unique_per_conduit, "conduit_store", id="unique_per_conduit"),
        pytest.param("spellspace", Existence.unique_per_spell_space, "space_store", id="spellspace"),
    ],
)
def test_door_held_root_is_built_without_its_own_guard(
        door_route_key: str, root_existence: Existence, store_name: str) -> None:
    """The eligible root builds and publishes with no acquire of its own; its child still takes its guard once."""
    world = World(root_existence)
    plan = world.normal_plan(door_route_key)
    result = plan(world.meld())
    assert world.events == CHILD_EVENTS + [("build", "root")]
    assert getattr(world, store_name)._creations["root"] is result
    world.events.clear()
    assert plan(world.meld()) is result
    assert world.events == []


@pytest.mark.parametrize(
    ("door_route_key", "root_existence"),
    [
        pytest.param(None, Existence.unique_per_conduit, id="no_route-per_conduit"),
        pytest.param(None, Existence.unique_per_spell_space, id="no_route-spellspace"),
        pytest.param("unique_per_conduit", Existence.unique_per_spell_space, id="route_mismatch-spellspace_root"),
        pytest.param("spellspace", Existence.unique_per_conduit, id="route_mismatch-per_conduit_root"),
        pytest.param("lineage", Existence.unique_per_conduit_lineage, id="lineage"),
        pytest.param("cluster", Existence.unique_per_conduit_cluster, id="cluster"),
        pytest.param("unique", Existence.unique, id="unique"),
    ],
)
def test_root_guard_is_kept_unless_route_and_existence_match(
        door_route_key: Optional[str], root_existence: Existence) -> None:
    """Without a matching eligible door route the root takes its own guard around its build, as before."""
    world = World(root_existence)
    world.normal_plan(door_route_key)(world.meld())
    assert world.events == CHILD_EVENTS + [("acquire", "root"), ("build", "root"), ("release", "root")]


def test_door_route_key_outside_normal_mode_is_refused() -> None:
    """A door route key only describes the normal plan; an override plan request carrying one is refused."""
    world = World(Existence.unique_per_conduit)
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=("root", None), steps=world.steps,
        topology_for=world.topologies.get,
    )
    with pytest.raises(RuntimeError, match="normal-mode plan"):
        SitePlanLowering.emit(
            steps=world.steps, site_graph=graph, resolution=OverrideKeyResolver.resolve(graph, ("limit",)),
            root_instance_key=("root", None), root_spell_id="root", root_spell_name="root", arity=0,
            door_route_key="unique_per_conduit",
        )
    graph.cleanup()


def test_runtime_applies_the_door_route_to_the_normal_plan_only() -> None:
    """With a door route the normal plan skips the root guard; an override key-set plan still takes it."""
    world = World(Existence.unique_per_conduit)
    runtime = SitePlanOverrideRuntime(
        steps=world.steps, root_spell=world.root, root_instance_key=("root", None),
        door_route_key="unique_per_conduit",
    )
    runtime.execute_normal(world.meld())
    assert world.events == CHILD_EVENTS + [("build", "root")]
    world.events.clear()
    del world.conduit_store._creations["root"]
    overridden = runtime.execute_with_overrides(world.meld(), {"limit": 5})
    assert overridden.kwargs["limit"] == 5
    assert world.events == [("acquire", "root"), ("build", "root"), ("release", "root")]
    runtime.cleanup()


def test_runtime_without_a_door_route_keeps_the_root_guard() -> None:
    """The default (no door route) keeps today's re-entrant root guard in the normal plan."""
    world = World(Existence.unique_per_conduit)
    runtime = SitePlanOverrideRuntime(steps=world.steps, root_spell=world.root, root_instance_key=("root", None))
    runtime.execute_normal(world.meld())
    assert world.events == CHILD_EVENTS + [("acquire", "root"), ("build", "root"), ("release", "root")]
    runtime.cleanup()


def test_door_held_root_returns_an_instance_published_while_its_children_were_built() -> None:
    """
    The root still rechecks after its children: an instance published meanwhile (as a same-thread nested meld
    would) is returned and the root is not constructed a second time.
    """
    world = World(Existence.unique_per_spell_space)
    published = SimpleNamespace(name="published-by-nested-meld")

    def child_that_publishes_the_root(*args: Any, **kwargs: Any) -> SimpleNamespace:
        world.events.append(("build", "s"))
        world.space_store._creations["root"] = published
        return SimpleNamespace(name="s")

    world.child.spell = child_that_publishes_the_root
    result = world.normal_plan("spellspace")(world.meld())
    assert result is published
    assert world.events == CHILD_EVENTS
    assert world.space_store._creations["root"] is published


def test_door_held_disposal_bearing_root_still_registers_through_add_creation() -> None:
    """A door-held root with disposal methods publishes through `add_creation` (cleaned-store refusal intact)."""
    world = World(Existence.unique_per_conduit, root_disposal=("close",))
    result = world.normal_plan("unique_per_conduit")(world.meld())
    assert world.events == CHILD_EVENTS + [("build", "root"), ("add_creation", "root")]
    assert world.conduit_store._creations["root"] is result


def test_eligible_routes_are_exactly_the_per_scope_ones() -> None:
    """Only the two per-scope routes, each with its own existence, are door-held; the map is the whole rule."""
    from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
        SitePlanEmission,
    )

    assert SitePlanEmission.DOOR_HELD_ROOT_EXISTENCE == {
        "unique_per_conduit": Existence.unique_per_conduit,
        "spellspace": Existence.unique_per_spell_space,
    }
    assert Counter(SitePlanEmission.DOOR_HELD_ROOT_EXISTENCE.values()) == Counter(
        {Existence.unique_per_conduit: 1, Existence.unique_per_spell_space: 1}
    )
