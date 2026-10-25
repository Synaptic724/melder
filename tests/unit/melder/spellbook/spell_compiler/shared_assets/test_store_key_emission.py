"""
Unit tests - the emitted creation code files and reads store slots by `Spell.store_key`.

STORY-2026-10-25-creations_store_slots_by_binding. Where emitted code read or published a store slot by the spell_id
it now uses the store key, a constant of the emitted code, and the no-disposal slotted publish goes through
`Creations.register_slot`, so the store records the key on its spell_id's shelf. Every fake spell here has a store
key unlike its spell_id, so a position left on the spell_id reads or files the wrong slot; the stores are real.
"""
import threading
from collections import Counter
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Tuple

from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler import (
    compile_creation_context_instance_no_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.override_key_resolver import (
    OverrideKeyResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
    SitePlanLowering,
    SitePlanStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_no_overrides_codegen_creation_compiler import (
    compile_solo_no_overrides_codegen_creation_executor,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError

Key = Tuple[str, Optional[int]]


def _store() -> Creations:
    """A real store."""
    return Creations(owner_conduit_id="conduit-1", id="conduit-1")


def _factory(name: str, built: Counter) -> Callable[..., Any]:
    """A constructor that counts its builds."""

    def construct(*args: Any, **kwargs: Any) -> SimpleNamespace:
        built[name] += 1
        return SimpleNamespace(name=name, args=args, kwargs=kwargs)

    return construct


def _spell(spell_id: str, built: Counter, existence: Existence = Existence.many,
           disposal: Tuple[str, ...] = ()) -> SimpleNamespace:
    """A fake spell whose store key is `<spell_id>:binding`."""
    return SimpleNamespace(
        spell=_factory(spell_id, built),
        spell_id=spell_id,
        store_key=f"{spell_id}:binding",
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
        _owner_creations=_store(),
        _dynamic_environment=False,
        _spell_system_states=SimpleNamespace(get_local_topology=lambda spell_index: None),
    )


def _step(key: Key, spell: SimpleNamespace, *deps: Tuple[str, Tuple[Key, ...]]) -> SitePlanStep:
    """One step view."""
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


def _socket(spell_id: str, name: str, position: int) -> SpellSocketDescriptor:
    """One Phase-3 socket."""
    return SpellSocketDescriptor(
        spell_id=spell_id, param_name=name, position=position, socket_kind=SocketKind.NORMAL,
        is_collection=False, is_optional=False, target_spell_ids=(), parameter_kind="POSITIONAL_OR_KEYWORD",
    )


def _plan(steps: Tuple[SitePlanStep, ...], topologies: Dict[str, Any]) -> Tuple[Callable[..., Any], str,
                                                                                 Dict[str, Any]]:
    """Emit and compile the normal-key-set plan; return it, its source and its namespace."""
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=("root", 0), steps=steps, topology_for=topologies.get,
    )
    resolution = OverrideKeyResolver.resolve(graph, ())
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=resolution, root_instance_key=("root", 0),
        root_spell_id="root", root_spell_name="root", arity=0,
    )
    exec(compile(source, "<test>", "exec"), namespace)
    graph.cleanup()
    return namespace[SitePlanLowering.PLAN_FUNCTION_NAME], source, namespace


def test_a_shared_site_reads_and_publishes_under_its_store_key() -> None:
    """Root(s: S), S `unique_per_conduit` without disposal: the plan files S under its store key, once."""
    built: Counter = Counter()
    spells = {"s": _spell("s", built, Existence.unique_per_conduit), "root": _spell("root", built)}
    steps = (_step(("s", None), spells["s"]), _step(("root", 0), spells["root"], ("s", (("s", None),))))
    topologies = {"root": SpellLocalTopology("root", (_socket("root", "s", 0),))}
    plan, source, namespace = _plan(steps, topologies)
    assert namespace["sid0"] == "s:binding"
    assert "c0.register_slot(sid0, v0)" in source
    store = _store()
    meld = SimpleNamespace(_conduit_creations=store)
    first = plan(meld, {})
    second = plan(meld, {})
    assert store.get_creation("s:binding") is first.kwargs["s"] is second.kwargs["s"]
    assert store.get_creation("s") is None
    assert store.count_spell_creations("s") == 1
    assert built == Counter({"s": 1, "root": 2})


def test_a_disposal_bearing_many_registers_under_its_store_key() -> None:
    """A disposal-bearing `many` root registers each object under its store key, in one record."""
    built: Counter = Counter()
    root = _spell("root", built, Existence.many, ("close",))
    plan, source, namespace = _plan((_step(("root", 0), root),), {"root": SpellLocalTopology("root", ())})
    assert namespace["sid0"] == "root:binding"
    store = _store()
    meld = SimpleNamespace(_conduit_creations=store, _spellspace_creations=None)
    objects = [plan(meld, {}), plan(meld, {})]
    assert store.get_creation("root:binding") == objects
    assert store.get_creation("root") is None
    assert store.count_spell_creations("root") == 2


def test_a_door_reads_its_slot_by_store_key() -> None:
    """A `unique_per_conduit` door returns the object filed under the store key without building."""
    built: Counter = Counter()
    spell = _spell("door", built, Existence.unique_per_conduit)
    executor_calls: List[Any] = []
    door = compile_creation_context_instance_no_overrides_executor(
        resolve_route_key="unique_per_conduit",
        fast_transient_no_overrides_enabled=False,
        spell=spell,
        spell_id=spell.spell_id,
        no_overrides_executor=lambda meld: executor_calls.append(meld),
        spell_space_scope_error_type=SpellSpaceScopeError,
    )
    store = _store()
    stored = object()
    store.add_creation("door:binding", stored)
    assert door(SimpleNamespace(_conduit_creations=store)) is stored
    assert executor_calls == []


def test_solo_executors_file_under_the_store_key() -> None:
    """The solo templates publish a slotted object and register a disposal-bearing `many` under the store key."""
    built: Counter = Counter()
    slotted = _spell("slotted", built, Existence.unique_per_conduit)
    many = _spell("many", built, Existence.many, ("close",))
    store = _store()
    meld = SimpleNamespace(_conduit_creations=store, _spellspace_creations=None)
    slotted_executor = compile_solo_no_overrides_codegen_creation_executor(
        spell=slotted, solo_emit_key="unique_per_conduit", fast_transient_no_overrides_enabled=False,
    )
    many_executor = compile_solo_no_overrides_codegen_creation_executor(
        spell=many, solo_emit_key="many", fast_transient_no_overrides_enabled=False,
    )
    one = slotted_executor(meld)
    objects = [many_executor(meld), many_executor(meld)]
    assert store.get_creation("slotted:binding") is one
    assert store.get_creation("many:binding") == objects
    assert store.get_creation("slotted") is None and store.get_creation("many") is None
