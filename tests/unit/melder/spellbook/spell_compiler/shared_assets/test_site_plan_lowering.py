"""Unit contracts for key-set plan lowering and the override runtime (override design S3a)."""

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
    SitePlanRuntimeHelpers,
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
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError

Key = Tuple[str, Optional[int]]


class FakeStore:
    """A creations store with the attributes emitted plans read and write."""

    def __init__(self) -> None:
        """Start empty."""
        self._creations: Dict[str, Any] = {}
        self._slot_guards: Dict[str, threading.RLock] = {}
        self.disposal_adds: List[Tuple[str, Any]] = []

    def slot_guard(self, spell_id: str) -> threading.RLock:
        """Return one RLock per slot."""
        return self._slot_guards.setdefault(spell_id, threading.RLock())

    def add_creation(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                     disposal_methods: Optional[List[str]] = None) -> None:
        """Publish one singleton and record the disposal registration."""
        self._creations[key] = item
        self.disposal_adds.append((key, item))

    def add_many_creations(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                           disposal_methods: Optional[List[str]] = None) -> None:
        """Record one disposal-bearing many instance."""
        self.disposal_adds.append((key, item))


def _factory(name: str, built: Counter) -> Callable[..., Any]:
    """Return a constructor that counts builds and keeps its arguments."""

    def construct(*args: Any, **kwargs: Any) -> SimpleNamespace:
        built[name] += 1
        return SimpleNamespace(name=name, args=args, kwargs=kwargs)

    return construct


def _spell(spell_id: str, built: Counter, existence: Existence = Existence.many,
           disposal: Tuple[str, ...] = ()) -> SimpleNamespace:
    """Build a fake spell with the attributes the lowering and the generic helpers read."""
    return SimpleNamespace(
        spell=_factory(spell_id, built),
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
        _owner_creations=FakeStore(),
    )


def _step(key: Key, spell: SimpleNamespace, *deps: Tuple[str, Tuple[Key, ...]],
          collections: Tuple[str, ...] = (), lock_hint: bool = False) -> SitePlanStep:
    """Build one step view."""
    return SitePlanStep(
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
    )


def _socket(spell_id: str, name: str, position: int, kind: str = "POSITIONAL_OR_KEYWORD",
            collection: bool = False, optional: bool = False) -> SpellSocketDescriptor:
    """Build one Phase-3 socket descriptor."""
    return SpellSocketDescriptor(
        spell_id=spell_id, param_name=name, position=position, socket_kind=SocketKind.NORMAL,
        is_collection=collection, is_optional=optional, target_spell_ids=(), parameter_kind=kind,
    )


class World:
    """Root(a: A(x: X), b: B, limit=3), all many unless a test swaps steps."""

    def __init__(self) -> None:
        """Build spells, steps and topologies."""
        self.built: Counter = Counter()
        self.spells = {name: _spell(name, self.built) for name in ("x", "a", "b", "root")}
        self.steps = (
            _step(("x", 3), self.spells["x"]),
            _step(("a", 1), self.spells["a"], ("x", (("x", 3),))),
            _step(("b", 2), self.spells["b"]),
            _step(("root", None), self.spells["root"], ("a", (("a", 1),)), ("b", (("b", 2),))),
        )
        self.topologies = {
            "root": SpellLocalTopology("root", (
                _socket("root", "a", 0), _socket("root", "b", 1), _socket("root", "limit", 2, optional=True),
            )),
            "a": SpellLocalTopology("a", (_socket("a", "x", 0),)),
            "b": SpellLocalTopology("b", ()),
            "x": SpellLocalTopology("x", ()),
        }

    def graph(self) -> Any:
        """Build the site graph from the steps."""
        return SitePlanLowering.build_site_graph(
            root_spell_id="root", root_instance_key=("root", None), steps=self.steps,
            topology_for=self.topologies.get,
        )

    def plan(self, keys: Tuple[str, ...], arity: int = 0) -> Tuple[Callable[..., Any], str]:
        """Resolve, emit and compile one plan; return it with its source."""
        graph = self.graph()
        resolution = OverrideKeyResolver.resolve(graph, keys, arity)
        source, namespace, _ = SitePlanLowering.emit(
            steps=self.steps, site_graph=graph, resolution=resolution, root_instance_key=("root", None),
            root_spell_id="root", root_spell_name="root", arity=arity,
        )
        exec(compile(source, "<test>", "exec"), namespace)
        graph.cleanup()
        return namespace[SitePlanLowering.PLAN_FUNCTION_NAME], source

    def runtime(self) -> SitePlanOverrideRuntime:
        """Build one site-plan runtime over the steps (it compiles its normal plan)."""
        root = self.spells["root"]
        root._spellbook = SimpleNamespace(
            _spell_system_states=SimpleNamespace(get_local_topology_by_id=self.topologies.get)
        )
        return SitePlanOverrideRuntime(
            steps=self.steps, root_spell=root, root_instance_key=("root", None),
        )


def test_site_graph_from_steps_is_parents_first_with_every_parameter() -> None:
    """Steps plus topologies give the S1 section: root first, dependencies later, plain params kept."""
    world = World()
    graph = world.graph()
    assert graph.sites[0].instance_key == ("root", None)
    assert [param.name for param in graph.sites[0].params] == ["a", "b", "limit"]
    order = [site.instance_key for site in graph.sites]
    assert order.index(("a", 1)) < order.index(("x", 3))
    graph.cleanup()


def test_demand_skips_everything_only_the_supplied_parameter_needed() -> None:
    """A winning key on `a` removes A and X from the demanded set (P1)."""
    world = World()
    graph = world.graph()
    resolution = OverrideKeyResolver.resolve(graph, ("a",))
    assert SitePlanLowering.demanded_instance_keys(graph, resolution) == {("root", None), ("b", 2)}
    graph.cleanup()


def test_plan_reads_supplied_value_by_key_and_builds_only_the_rest() -> None:
    """The supplied object is passed positionally; A and X are never constructed (B1)."""
    world = World()
    plan, source = world.plan(("a",))
    supplied = object()
    result = plan(None, {"a": supplied})
    assert "ov['a']" in source
    assert result.args[0] is supplied and result.args[1].name == "b"
    assert world.built == Counter({"b": 1, "root": 1})


def test_plain_parameter_override_keeps_every_dependency() -> None:
    """A plain parameter after two dependencies is passed in order; nothing is cut."""
    world = World()
    plan, _ = world.plan(("limit",))
    result = plan(None, {"limit": 9})
    assert result.args[2] == 9
    assert world.built == Counter({"x": 1, "a": 1, "b": 1, "root": 1})


def test_positional_payload_supplies_leading_parameters_and_cuts_them() -> None:
    """`__args__` of length 1 fills `a`; B is still built (B5)."""
    world = World()
    plan, _ = world.plan(("__args__",), arity=1)
    first = object()
    result = plan(None, {"__args__": [first]})
    assert result.args[0] is first and result.args[1].name == "b"
    assert world.built == Counter({"b": 1, "root": 1})


def test_extra_positional_values_pass_through_star_args() -> None:
    """A payload longer than the positional parameters is passed as `*args`."""
    world = World()
    plan, source = world.plan(("__args__",), arity=4)
    result = plan(None, {"__args__": (1, 2, 3, 4)})
    assert "*args" in source
    assert result.args == (1, 2, 3, 4)
    assert world.built == Counter({"root": 1})


def test_collection_parameter_receives_a_list_for_every_member_count() -> None:
    """Two members give a two-item list; a required collection with no members gets []."""
    built: Counter = Counter()
    spells = {name: _spell(name, built) for name in ("m1", "m2", "holder", "empty")}
    steps = (
        _step(("m1", 1), spells["m1"]),
        _step(("m2", 2), spells["m2"]),
        _step(("empty", 4), spells["empty"], ("items", ()), collections=("items",)),
        _step(("holder", None), spells["holder"], ("members", (("m1", 1), ("m2", 2))),
              ("empty", (("empty", 4),)), collections=("members",)),
    )
    topologies = {
        "holder": SpellLocalTopology("holder", (
            _socket("holder", "members", 0, collection=True), _socket("holder", "empty", 1),
        )),
        "empty": SpellLocalTopology("empty", (_socket("empty", "items", 0, collection=True),)),
    }
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="holder", root_instance_key=("holder", None), steps=steps, topology_for=topologies.get,
    )
    resolution = OverrideKeyResolver.resolve(graph, ())
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=resolution, root_instance_key=("holder", None),
        root_spell_id="holder", root_spell_name="holder", arity=0,
    )
    exec(compile(source, "<test>", "exec"), namespace)
    result = namespace[SitePlanLowering.PLAN_FUNCTION_NAME](None, {})
    assert [member.name for member in result.args[0]] == ["m1", "m2"]
    assert result.args[1].args == ([],)
    assert built == Counter({"m1": 1, "m2": 1, "empty": 1, "holder": 1})
    graph.cleanup()


def _shared_world(lock_hint: bool = False, existence: Existence = Existence.unique_per_conduit) -> Tuple[Any, ...]:
    """Root(s: S(x: X)) with S shared; returns (built, steps, topologies)."""
    built: Counter = Counter()
    spells = {"x": _spell("x", built), "s": _spell("s", built, existence), "root": _spell("root", built)}
    steps = (
        _step(("x", 2), spells["x"]),
        _step(("s", None), spells["s"], ("x", (("x", 2),)), lock_hint=lock_hint),
        _step(("root", 0), spells["root"], ("s", (("s", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "s", 0),)),
        "s": SpellLocalTopology("s", (_socket("s", "x", 0),)),
    }
    return built, spells, steps, topologies


def _shared_plan(steps: Tuple[SitePlanStep, ...], topologies: Dict[str, Any], keys: Tuple[str, ...]) -> Any:
    """Compile one plan over the shared world."""
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=("root", 0), steps=steps, topology_for=topologies.get,
    )
    resolution = OverrideKeyResolver.resolve(graph, keys)
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=resolution, root_instance_key=("root", 0),
        root_spell_id="root", root_spell_name="root", arity=0,
    )
    exec(compile(source, "<test>", "exec"), namespace)
    graph.cleanup()
    return namespace[SitePlanLowering.PLAN_FUNCTION_NAME]


def test_shared_step_publishes_on_miss_and_reuses_on_hit() -> None:
    """A stored shared instance is reused; a key on its own parameter then raises today's P2 error."""
    built, spells, steps, topologies = _shared_world()
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    first = _shared_plan(steps, topologies, ("s>x",))(meld, {"s>x": "given"})
    assert first.args[0].args[0] == "given"
    assert meld._conduit_creations._creations["s"] is first.args[0]
    with pytest.raises(MeldExecutionError, match="spell instance that already exists"):
        _shared_plan(steps, topologies, ("s>x",))(meld, {"s>x": "again"})
    assert built == Counter({"s": 1, "root": 1})


def test_supplied_shared_dependency_never_touches_its_store() -> None:
    """Supplying `s` builds only the root; S and X are neither built nor published."""
    built, spells, steps, topologies = _shared_world()
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    result = _shared_plan(steps, topologies, ("s",))(meld, {"s": "given"})
    assert result.args == ("given",)
    assert meld._conduit_creations._creations == {}
    assert built == Counter({"root": 1})


def test_unique_with_lock_hint_uses_the_owner_store_and_spell_lock() -> None:
    """A `unique` step publishes into its owner store under `Spell._lock`."""
    built, spells, steps, topologies = _shared_world(lock_hint=True, existence=Existence.unique)
    plan = _shared_plan(steps, topologies, ("s>x",))
    result = plan(SimpleNamespace(), {"s>x": 1})
    assert spells["s"]._owner_creations._creations["s"] is result.args[0]


def test_disposal_bearing_many_step_registers_in_the_innermost_scope() -> None:
    """A many step with disposal methods is appended to the spellspace store, else the conduit store."""
    built: Counter = Counter()
    spells = {"d": _spell("d", built, disposal=("close",)), "root": _spell("root", built)}
    steps = (
        _step(("d", 1), spells["d"]),
        _step(("root", None), spells["root"], ("d", (("d", 1),))),
    )
    topologies = {"root": SpellLocalTopology("root", (_socket("root", "d", 0), _socket("root", "limit", 1)))}
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=("root", None), steps=steps, topology_for=topologies.get,
    )
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=OverrideKeyResolver.resolve(graph, ("limit",)),
        root_instance_key=("root", None), root_spell_id="root", root_spell_name="root", arity=0,
    )
    exec(compile(source, "<test>", "exec"), namespace)
    plan = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
    conduit_store, space_store = FakeStore(), FakeStore()
    first = plan(SimpleNamespace(_spellspace_creations=None, _conduit_creations=conduit_store), {"limit": 1})
    second = plan(SimpleNamespace(_spellspace_creations=space_store, _conduit_creations=conduit_store), {"limit": 2})
    assert conduit_store.disposal_adds == [("d", first.args[0])]
    assert space_store.disposal_adds == [("d", second.args[0])]
    graph.cleanup()


def _compile_plan(steps: Tuple[SitePlanStep, ...], topologies: Dict[str, Any], root_key: Key,
                  keys: Tuple[str, ...] = ()) -> Callable[..., Any]:
    """Build the site graph, resolve `keys`, emit and compile one plan over `steps`."""
    graph = SitePlanLowering.build_site_graph(
        root_spell_id=root_key[0], root_instance_key=root_key, steps=steps, topology_for=topologies.get,
    )
    resolution = OverrideKeyResolver.resolve(graph, keys)
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=resolution, root_instance_key=root_key,
        root_spell_id=root_key[0], root_spell_name=root_key[0], arity=0,
    )
    exec(compile(source, "<test>", "exec"), namespace)
    graph.cleanup()
    return namespace[SitePlanLowering.PLAN_FUNCTION_NAME]


def test_warm_plan_skips_the_children_of_a_stored_shared_site() -> None:
    """With S stored, a warm meld builds neither S nor X, the many only S needs (B2)."""
    built: Counter = Counter()
    spells = {
        "x": _spell("x", built), "s": _spell("s", built, Existence.unique_per_conduit), "root": _spell("root", built),
    }
    steps = (
        _step(("x", 2), spells["x"]),
        _step(("s", None), spells["s"], ("x", (("x", 2),))),
        _step(("root", 0), spells["root"], ("s", (("s", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "s", 0), _socket("root", "limit", 1, optional=True))),
        "s": SpellLocalTopology("s", (_socket("s", "x", 0),)),
    }
    plan = _compile_plan(steps, topologies, ("root", 0), ("limit",))
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    first = plan(meld, {"limit": 1})
    second = plan(meld, {"limit": 2})
    assert second.args == (first.args[0], 2)
    assert built == Counter({"x": 1, "s": 1, "root": 2})


def _nested_world() -> Tuple[Counter, Tuple[SitePlanStep, ...], Dict[str, Any]]:
    """Root(t: T(p: P(s: S), q: Q(s: S))) with T and S shared, P and Q many."""
    built: Counter = Counter()
    shared = Existence.unique_per_conduit
    spells = {
        "s": _spell("s", built, shared), "p": _spell("p", built), "q": _spell("q", built),
        "t": _spell("t", built, shared), "root": _spell("root", built),
    }
    steps = (
        _step(("s", None), spells["s"]),
        _step(("p", 1), spells["p"], ("s", (("s", None),))),
        _step(("q", 2), spells["q"], ("s", (("s", None),))),
        _step(("t", None), spells["t"], ("p", (("p", 1),)), ("q", (("q", 2),))),
        _step(("root", 0), spells["root"], ("t", (("t", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "t", 0),)),
        "t": SpellLocalTopology("t", (_socket("t", "p", 0), _socket("t", "q", 1))),
        "p": SpellLocalTopology("p", (_socket("p", "s", 0),)),
        "q": SpellLocalTopology("q", (_socket("q", "s", 0),)),
    }
    return built, steps, topologies


def test_shared_site_needed_only_inside_one_miss_is_read_there() -> None:
    """S, needed only by T's children, is read inside T's miss: stored T skips it; a stored S is reused (L1)."""
    built, steps, topologies = _nested_world()
    plan = _compile_plan(steps, topologies, ("root", 0))
    store = FakeStore()
    meld = SimpleNamespace(_conduit_creations=store)
    first = plan(meld, {})
    p, q = first.args[0].args
    shared = store._creations["s"]
    assert p.args[0] is shared and q.args[0] is shared
    del store._creations["s"]
    plan(meld, {})
    assert built == Counter({"s": 1, "p": 1, "q": 1, "t": 1, "root": 2})
    store._creations["s"] = shared
    del store._creations["t"]
    third = plan(meld, {})
    assert third.args[0] is not first.args[0]
    assert all(child.args[0] is shared for child in third.args[0].args)
    assert built == Counter({"s": 1, "p": 2, "q": 2, "t": 2, "root": 3})


def test_sibling_misses_receive_one_shared_value_read_before_them() -> None:
    """S used by two shared siblings is read once at their common (top) context and passed into both misses."""
    built: Counter = Counter()
    shared = Existence.unique_per_conduit
    spells = {
        "s": _spell("s", built, shared), "p": _spell("p", built, shared), "q": _spell("q", built, shared),
        "root": _spell("root", built),
    }
    steps = (
        _step(("s", None), spells["s"]),
        _step(("p", None), spells["p"], ("s", (("s", None),))),
        _step(("q", None), spells["q"], ("s", (("s", None),))),
        _step(("root", 0), spells["root"], ("p", (("p", None),)), ("q", (("q", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "p", 0), _socket("root", "q", 1))),
        "p": SpellLocalTopology("p", (_socket("p", "s", 0),)),
        "q": SpellLocalTopology("q", (_socket("q", "s", 0),)),
    }
    plan = _compile_plan(steps, topologies, ("root", 0))
    store = FakeStore()
    meld = SimpleNamespace(_conduit_creations=store)
    first = plan(meld, {})
    p, q = first.args
    assert p.args[0] is q.args[0]
    del store._creations["p"]
    second = plan(meld, {})
    assert second.args[0] is not p and second.args[0].args[0] is p.args[0] and second.args[1] is q
    assert built == Counter({"s": 1, "p": 2, "q": 1, "root": 2})


def test_supplied_rule_under_a_stored_parent_is_never_skipped() -> None:
    """A rule on S under T stays at top level: P2 when S is stored, built and published when it is not."""
    built: Counter = Counter()
    shared = Existence.unique_per_conduit
    spells = {
        "x": _spell("x", built), "s": _spell("s", built, shared), "t": _spell("t", built, shared),
        "root": _spell("root", built),
    }
    steps = (
        _step(("x", 3), spells["x"]),
        _step(("s", None), spells["s"], ("x", (("x", 3),))),
        _step(("t", None), spells["t"], ("s", (("s", None),))),
        _step(("root", 0), spells["root"], ("t", (("t", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "t", 0),)),
        "t": SpellLocalTopology("t", (_socket("t", "s", 0),)),
        "s": SpellLocalTopology("s", (_socket("s", "x", 0),)),
    }
    plan = _compile_plan(steps, topologies, ("root", 0), ("t>s>x",))
    store = FakeStore()
    meld = SimpleNamespace(_conduit_creations=store)
    first = plan(meld, {"t>s>x": "given"})
    assert first.args[0].args[0].args == ("given",)
    with pytest.raises(MeldExecutionError, match="spell instance that already exists"):
        plan(meld, {"t>s>x": "again"})
    del store._creations["s"]
    second = plan(meld, {"t>s>x": "again"})
    assert second.args[0] is first.args[0]
    assert store._creations["s"].args == ("again",)
    assert built == Counter({"s": 2, "t": 1, "root": 2})


class _RecordingLock:
    """A context-manager build lock that records enter and exit in a shared event list."""

    def __init__(self, name: str, events: List[Tuple[str, str]]) -> None:
        """Keep the slot name and the event list."""
        self._name = name
        self._events = events

    def __enter__(self) -> _RecordingLock:
        """Record the acquire."""
        self._events.append(("acquire", self._name))
        return self

    def __exit__(self, *exc: Any) -> None:
        """Record the release; exceptions propagate."""
        self._events.append(("release", self._name))


class _RecordingStore(FakeStore):
    """A store whose slot guards record their use."""

    def __init__(self, events: List[Tuple[str, str]]) -> None:
        """Start empty with a shared event list."""
        super().__init__()
        self._events = events

    def slot_guard(self, spell_id: str) -> Any:
        """Return one recording lock per slot."""
        return self._slot_guards.setdefault(spell_id, _RecordingLock(spell_id, self._events))


def _logging_spell(name: str, events: List[Tuple[str, str]], existence: Existence) -> SimpleNamespace:
    """Build a fake spell whose constructor records its build in `events`."""
    spell = _spell(name, Counter(), existence)

    def construct(*args: Any, **kwargs: Any) -> SimpleNamespace:
        events.append(("build", name))
        return SimpleNamespace(name=name, args=args, kwargs=kwargs)

    spell.spell = construct
    return spell


def test_miss_takes_its_guard_only_after_its_children_and_warm_hits_take_no_lock() -> None:
    """S, built inside T's miss, is built and released before T's guard is taken; a warm meld takes no lock."""
    events: List[Tuple[str, str]] = []
    shared = Existence.unique_per_conduit
    spells = {
        "s": _logging_spell("s", events, shared), "t": _logging_spell("t", events, shared),
        "root": _logging_spell("root", events, Existence.many),
    }
    steps = (
        _step(("s", None), spells["s"]),
        _step(("t", None), spells["t"], ("s", (("s", None),))),
        _step(("root", 0), spells["root"], ("t", (("t", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "t", 0),)),
        "t": SpellLocalTopology("t", (_socket("t", "s", 0),)),
    }
    plan = _compile_plan(steps, topologies, ("root", 0))
    meld = SimpleNamespace(_conduit_creations=_RecordingStore(events))
    plan(meld, {})
    assert events == [
        ("acquire", "s"), ("build", "s"), ("release", "s"),
        ("acquire", "t"), ("build", "t"), ("release", "t"), ("build", "root"),
    ]
    events.clear()
    plan(meld, {})
    assert events == [("build", "root")]


def test_generic_step_inside_a_miss_reads_inner_and_outer_values() -> None:
    """A contract-payload step built inside S's miss gets its inner many and the outer shared Z by key."""
    built: Counter = Counter()
    shared = Existence.unique_per_conduit
    spells = {
        "y": _spell("y", built), "z": _spell("z", built, shared), "x": _spell("x", built),
        "s": _spell("s", built, shared), "root": _spell("root", built),
    }
    generic = SitePlanStep(
        instance_key=("x", 3), spell=spells["x"], existence=Existence.many,
        dependency_resolution_order=(("y", (("y", 4),)), ("z", (("z", None),))),
        collection_param_names=frozenset(), uses_positional_override=False, contract_positional_override=None,
        has_contract_payload=True, contract_payload={"c": "contract"}, use_spell_lock_hint=False,
    )
    steps = (
        _step(("y", 4), spells["y"]),
        _step(("z", None), spells["z"]),
        generic,
        _step(("s", None), spells["s"], ("x", (("x", 3),))),
        _step(("root", 0), spells["root"], ("s", (("s", None),)), ("z", (("z", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "s", 0), _socket("root", "z", 1))),
        "s": SpellLocalTopology("s", (_socket("s", "x", 0),)),
        "x": SpellLocalTopology("x", (_socket("x", "y", 0), _socket("x", "z", 1))),
    }
    plan = _compile_plan(steps, topologies, ("root", 0))
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    first = plan(meld, {})
    x = first.args[0].args[0]
    assert x.kwargs["y"].name == "y" and x.kwargs["c"] == "contract"
    assert x.kwargs["z"] is first.args[1]
    second = plan(meld, {})
    assert second.args == first.args
    assert built == Counter({"y": 1, "z": 1, "x": 1, "s": 1, "root": 2})


def test_disposal_bearing_many_inside_a_miss_registers_in_the_innermost_scope() -> None:
    """A disposal-bearing many built inside S's miss goes to the spellspace store, else the conduit store."""
    built: Counter = Counter()
    spells = {
        "d": _spell("d", built, disposal=("close",)), "s": _spell("s", built, Existence.unique_per_conduit),
        "root": _spell("root", built),
    }
    steps = (
        _step(("d", 2), spells["d"]),
        _step(("s", None), spells["s"], ("d", (("d", 2),))),
        _step(("root", 0), spells["root"], ("s", (("s", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "s", 0),)),
        "s": SpellLocalTopology("s", (_socket("s", "d", 0),)),
    }
    plan = _compile_plan(steps, topologies, ("root", 0))
    first_store, second_store, space_store = FakeStore(), FakeStore(), FakeStore()
    first_meld = SimpleNamespace(_spellspace_creations=None, _conduit_creations=first_store)
    first = plan(first_meld, {})
    plan(first_meld, {})
    second = plan(SimpleNamespace(_spellspace_creations=space_store, _conduit_creations=second_store), {})
    assert first_store.disposal_adds == [("d", first.args[0].args[0])]
    assert space_store.disposal_adds == [("d", second.args[0].args[0])]
    assert second_store.disposal_adds == []
    assert built == Counter({"d": 2, "s": 2, "root": 3})


def test_conflict_guard_accepts_identity_and_equal_scalars_only() -> None:
    """E1: same object or equal plain scalars pass; anything else raises the wrapped error."""
    marker = object()
    SitePlanRuntimeHelpers.conflict_guard(marker, marker, "s.x", "root", "Root")
    SitePlanRuntimeHelpers.conflict_guard(3, 3, "s.x", "root", "Root")
    with pytest.raises(MeldExecutionError, match="Failed to apply overrides") as caught:
        SitePlanRuntimeHelpers.conflict_guard([1], [1], "s.x", "root", "Root")
    assert "Conflicting overrides for socket s.x" in str(caught.value.__cause__)
    with pytest.raises(MeldExecutionError):
        SitePlanRuntimeHelpers.conflict_guard(1, True, "s.x", "root", "Root")


def test_existing_override_messages_distinguish_root_and_instance() -> None:
    """P2 keeps today's two messages."""
    spell = _spell("s", Counter())
    with pytest.raises(MeldExecutionError, match="root spell that already exists"):
        SitePlanRuntimeHelpers.raise_existing_override(spell, "s")
    with pytest.raises(MeldExecutionError, match="spell instance that already exists"):
        SitePlanRuntimeHelpers.raise_existing_override(spell, "root")


def test_masked_step_drops_overridden_dependencies_and_contract_values() -> None:
    """Masking removes supplied parameters from the dependency order and the contract payload."""
    step = SitePlanStep(
        instance_key=("r", None), spell=_spell("r", Counter()), existence=Existence.many,
        dependency_resolution_order=(("a", (("a", 1),)), ("b", (("b", 2),))),
        collection_param_names=frozenset(), uses_positional_override=True,
        contract_positional_override=(1,), has_contract_payload=True,
        contract_payload={"a": 1, "c": 2}, use_spell_lock_hint=False,
    )
    masked = step.masked(frozenset({"a"}), drop_contract_positional=True)
    assert [name for name, _ in masked.dependency_resolution_order] == ["b"]
    assert masked.contract_payload == {"c": 2}
    assert masked.contract_positional_override is None and masked.uses_positional_override is False
    masked.cleanup()
    masked.cleanup()
    assert masked.is_cleaned


def test_generic_construct_applies_supplied_values_last() -> None:
    """Supplied values win over dependency and contract operands; bad `__args__` raises today's error."""
    built: Counter = Counter()
    step = SitePlanStep(
        instance_key=("r", None), spell=_spell("r", built), existence=Existence.many,
        dependency_resolution_order=(("a", (("a", 1),)),), collection_param_names=frozenset(),
        uses_positional_override=False, contract_positional_override=None, has_contract_payload=True,
        contract_payload={"c": "contract"}, use_spell_lock_hint=False,
    )
    result = SitePlanRuntimeHelpers.construct_with_supplied_values(
        plan_step=step, instance_results={("a", 1): "dep"}, supplied_values={"c": "given", "__args__": [7]},
    )
    assert result.args == (7,) and result.kwargs == {"a": "dep", "c": "given"}
    with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
        SitePlanRuntimeHelpers.construct_with_supplied_values(
            plan_step=step, instance_results={("a", 1): "dep"}, supplied_values={"__args__": 7},
        )


def _count_emits(monkeypatch: pytest.MonkeyPatch) -> Counter:
    """Count plan emissions through the lowering entry."""
    calls: Counter = Counter()
    original = SitePlanLowering.emit.__func__

    def counting(cls: Any, **kwargs: Any) -> Any:
        calls["emit"] += 1
        return original(cls, **kwargs)

    monkeypatch.setattr(SitePlanLowering, "emit", classmethod(counting))
    return calls


def test_runtime_compiles_one_plan_per_key_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """The normal plan compiles at construction; same keys reuse one plan; a new key set compiles once."""
    calls = _count_emits(monkeypatch)
    world = World()
    runtime = world.runtime()
    assert calls["emit"] == 1
    for value in range(3):
        assert runtime.execute_with_overrides(None, {"limit": value}).args[2] == value
    runtime.execute_with_overrides(None, {"a": object()})
    assert calls["emit"] == 3
    runtime.cleanup()


def test_runtime_wraps_bad_keys_and_does_not_store_them(monkeypatch: pytest.MonkeyPatch) -> None:
    """A bad key raises today's wrapped error on every call and never reaches emission."""
    calls = _count_emits(monkeypatch)
    runtime = World().runtime()
    for _ in range(2):
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides") as caught:
            runtime.execute_with_overrides(None, {"nosuch": 1})
        assert "No sockets found for override path 'nosuch'" in str(caught.value.__cause__)
    assert calls["emit"] == 1
    runtime.cleanup()


def test_runtime_runs_the_normal_plan_without_winning_operands() -> None:
    """`None`, `{}` and empty positional payloads run the normal plan, which builds the whole graph (B8)."""
    world = World()
    runtime = world.runtime()
    for payload in (None, {}, {"__args__": []}, {"__args__": None}):
        result = runtime.execute_with_overrides(None, payload)
        assert [arg.name for arg in result.args] == ["a", "b"] and result.args[0].args[0].name == "x"
    assert runtime.execute_normal(None).args[1].name == "b"
    assert world.built == Counter({"x": 5, "a": 5, "b": 5, "root": 5})
    runtime.cleanup()


def test_runtime_compiles_per_arity_and_rejects_non_sequences() -> None:
    """Each `__args__` length gets its plan; a non-list payload raises today's error."""
    world = World()
    runtime = world.runtime()
    first = object()
    assert runtime.execute_with_overrides(None, {"__args__": [first]}).args[0] is first
    assert runtime.execute_with_overrides(None, {"__args__": (first, "b")}).args[:2] == (first, "b")
    with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
        runtime.execute_with_overrides(None, {"__args__": first})
    runtime.cleanup()


def test_runtime_evicts_the_oldest_key_set_at_the_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    """At the cap the first stored key set is dropped and recompiled on its next use."""
    monkeypatch.setattr(SitePlanOverrideRuntime, "MAX_PLANS", 2)
    calls = _count_emits(monkeypatch)
    runtime = World().runtime()
    for keys in (("limit",), ("b",), ("a",)):
        runtime.execute_with_overrides(None, {key: 1 for key in keys})
    runtime.execute_with_overrides(None, {"limit": 1})
    assert calls["emit"] == 5
    runtime.cleanup()


def test_runtime_cleanup_is_idempotent_and_refuses_new_compiles() -> None:
    """After cleanup a new key set cannot compile."""
    runtime = World().runtime()
    dispatcher = runtime.execute_with_overrides
    runtime.cleanup()
    runtime.cleanup()
    with pytest.raises(RuntimeError):
        dispatcher(None, {"limit": 1})


def test_runtime_requires_a_root_step() -> None:
    """A runtime over steps without the root instance key is refused."""
    world = World()
    with pytest.raises(RuntimeError, match="no step for root instance"):
        SitePlanOverrideRuntime(
            steps=world.steps[:3], root_spell=world.spells["root"], root_instance_key=("root", None),
        )


def test_normal_mode_emits_a_meld_only_plan_and_refuses_supplied_keys() -> None:
    """Normal mode gives `(meld) -> instance` for the empty key set; a key set that supplies anything is refused."""
    world = World()
    graph = world.graph()

    def emit(keys: Tuple[str, ...]) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
        return SitePlanLowering.emit(
            steps=world.steps, site_graph=graph, resolution=OverrideKeyResolver.resolve(graph, keys),
            root_instance_key=("root", None), root_spell_id="root", root_spell_name="root", arity=0,
            normal_mode=True,
        )

    source, namespace, _ = emit(())
    exec(compile(source, "<test>", "exec"), namespace)
    result = namespace[SitePlanLowering.PLAN_FUNCTION_NAME](None)
    assert [arg.name for arg in result.args] == ["a", "b"]
    with pytest.raises(RuntimeError, match="supplies nothing"):
        emit(("a",))
    graph.cleanup()


def test_normal_plan_skips_the_children_of_a_stored_shared_site() -> None:
    """The runtime's normal plan reuses stored S without building X again (B2 on normal melds)."""
    built, spells, steps, topologies = _shared_world()
    root = spells["root"]
    root._spellbook = SimpleNamespace(
        _spell_system_states=SimpleNamespace(get_local_topology_by_id=topologies.get)
    )
    runtime = SitePlanOverrideRuntime(steps=steps, root_spell=root, root_instance_key=("root", 0))
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    first = runtime.execute_normal(meld)
    second = runtime.execute_normal(meld)
    assert second is not first and second.args[0] is first.args[0]
    assert built == Counter({"x": 1, "s": 1, "root": 2})
    runtime.cleanup()


def test_runtime_site_graph_errors_are_not_override_errors() -> None:
    """A step list whose dependency has no step fails construction unwrapped, not as "Failed to apply overrides"."""
    world = World()
    root = world.spells["root"]
    root._spellbook = SimpleNamespace(
        _spell_system_states=SimpleNamespace(get_local_topology_by_id=world.topologies.get)
    )
    steps = tuple(step for step in world.steps if step.instance_key != ("b", 2))
    with pytest.raises(RuntimeError) as caught:
        SitePlanOverrideRuntime(steps=steps, root_spell=root, root_instance_key=("root", None))
    assert not isinstance(caught.value, MeldExecutionError)
