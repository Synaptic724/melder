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

    def runtime(self, inner: Optional[Callable[..., Any]] = None) -> SitePlanOverrideRuntime:
        """Build one override runtime over the steps."""
        root = self.spells["root"]
        root._spellbook = SimpleNamespace(
            _spell_system_states=SimpleNamespace(get_local_topology_by_id=self.topologies.get)
        )
        return SitePlanOverrideRuntime(
            steps=self.steps, root_spell=root, root_instance_key=("root", None),
            inner_no_overrides_executor=inner or (lambda meld: "normal"),
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
    """Repeated payloads with the same keys reuse one plan; a new key set compiles once."""
    calls = _count_emits(monkeypatch)
    world = World()
    runtime = world.runtime()
    for value in range(3):
        assert runtime.execute_with_overrides(None, {"limit": value}).args[2] == value
    runtime.execute_with_overrides(None, {"a": object()})
    assert calls["emit"] == 2
    runtime.cleanup()


def test_runtime_wraps_bad_keys_and_does_not_store_them(monkeypatch: pytest.MonkeyPatch) -> None:
    """A bad key raises today's wrapped error on every call and never reaches emission."""
    calls = _count_emits(monkeypatch)
    runtime = World().runtime()
    for _ in range(2):
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides") as caught:
            runtime.execute_with_overrides(None, {"nosuch": 1})
        assert "No sockets found for override path 'nosuch'" in str(caught.value.__cause__)
    assert calls["emit"] == 0
    runtime.cleanup()


def test_runtime_runs_the_inner_executor_without_winning_operands() -> None:
    """`None` and an empty positional payload run the normal executor (B8)."""
    runtime = World().runtime(inner=lambda meld: ("normal", meld))
    assert runtime.execute_with_overrides("m", None) == ("normal", "m")
    assert runtime.execute_with_overrides("m", {"__args__": []}) == ("normal", "m")
    assert runtime.execute_with_overrides("m", {"__args__": None}) == ("normal", "m")
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
    assert calls["emit"] == 4
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
            inner_no_overrides_executor=lambda meld: None,
        )
