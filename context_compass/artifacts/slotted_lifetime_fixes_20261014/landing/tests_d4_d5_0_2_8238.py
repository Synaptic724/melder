"""D4/D5 tests (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, notch 0.2.8238): holder-owned many children.

Adds the lifetime integration module (purge and transfer move with holder-owned children) and the Creations unit
module (adoption and every reader of the holder record), teaches the lowering test stores the adoption verb and adds
emission tests, and moves the 0.2.8235 many-child tests from the child spell's bucket to the holder's record.
Run from anywhere: python <this file> <tree root>
"""
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edit_tool

ROOT = pathlib.Path(sys.argv[1])
LIFETIME = ROOT / "tests/integration/melder/conduit/test_conduit_integration_holder_children_lifetime.py"
CREATIONS_UNIT = ROOT / "tests/unit/melder/aether/conduit/creations/test_creations_holder_children.py"
LOWERING_UNIT = str(ROOT / "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py")
DOOR_UNIT = str(ROOT / "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py")
MANY_COMPONENT = str(ROOT / "tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py")
MANY_INTEGRATION = str(ROOT / "tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py")


def _copy_crlf(source: pathlib.Path, target: pathlib.Path) -> None:
    """Write `source` to `target` with CRLF line endings (the tree's convention)."""
    text = source.read_bytes().decode("utf-8").replace("\r\n", "\n")
    target.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


_copy_crlf(HERE / "test_conduit_integration_holder_children_lifetime_0_2_8238.py", LIFETIME)
_copy_crlf(HERE / "test_creations_holder_children_0_2_8238.py", CREATIONS_UNIT)

lowering_edits = [
    (
        '''        self.disposal_adds: List[Tuple[str, Any]] = []

    def slot_guard(self, spell_id: str) -> threading.RLock:
        """Return one RLock per slot."""
''',
        '''        self.disposal_adds: List[Tuple[str, Any]] = []
        self.adoptions: List[Tuple[str, Any, Tuple[Tuple[str, Any], ...]]] = []

    def slot_guard(self, spell_id: str) -> threading.RLock:
        """Return one RLock per slot."""
''',
    ),
    (
        '''    def register_many(self, key: str, item: Any, disposal_methods: List[str]) -> None:
        """Record one disposal-bearing many instance registered through the hot verb (2026-10-01)."""
        self.disposal_adds.append((key, item))


def _factory(name: str, built: Counter) -> Callable[..., Any]:
''',
        '''    def register_many(self, key: str, item: Any, disposal_methods: List[str]) -> None:
        """Record one disposal-bearing many instance registered through the hot verb (2026-10-01)."""
        self.disposal_adds.append((key, item))

    def adopt_children(self, holder_key: str, holder: Any, children: Tuple[Tuple[str, Any], ...]) -> None:
        """Record one adoption an emitted miss made right after publishing its holder (0.2.8238)."""
        self.adoptions.append((holder_key, holder, children))


def _factory(name: str, built: Counter) -> Callable[..., Any]:
''',
    ),
    (
        '''    runs under a SpellSpace meld (many_child_follows_holder, 2026-10-14). Until 0.2.8235 the child went to the
    meld's innermost scope - the spellspace store here - whose exit disposed it while S kept it.
    """
''',
        '''    runs under a SpellSpace meld (many_child_follows_holder, 2026-10-14). Until 0.2.8235 the child went to the
    meld's innermost scope - the spellspace store here - whose exit disposed it while S kept it. Since 0.2.8238 S's
    miss also adopts the child into S's disposal record right after publishing S, once per publication: a warm meld
    adopts nothing.
    """
''',
    ),
    (
        '''    assert first_store.disposal_adds == [("d", first.args[0].args[0])]
    assert second_store.disposal_adds == [("d", second.args[0].args[0])]
    assert space_store.disposal_adds == []
    assert built == Counter({"d": 2, "s": 2, "root": 3})
''',
        '''    assert first_store.disposal_adds == [("d", first.args[0].args[0])]
    assert second_store.disposal_adds == [("d", second.args[0].args[0])]
    assert space_store.disposal_adds == []
    held_first, held_second = first.args[0], second.args[0]
    assert first_store.adoptions == [("s", held_first, (("d", held_first.args[0]),))]
    assert second_store.adoptions == [("s", held_second, (("d", held_second.args[0]),))]
    assert space_store.adoptions == []
    assert built == Counter({"d": 2, "s": 2, "root": 3})
''',
    ),
    (
        '''def test_per_conduit_site_read_is_unchanged_by_the_owner_store_constant() -> None:
    """The `meld.<store>` routes never bind a constant: the store is one attribute read on the parameter."""
    _built, _spells, steps, topologies = _shared_world()
    source, namespace = _shared_source(steps, topologies, ())

    assert "    c1 = meld._conduit_creations" in source
    assert "c1" not in namespace
''',
        '''def test_per_conduit_site_read_is_unchanged_by_the_owner_store_constant() -> None:
    """The `meld.<store>` routes never bind a constant: the store is one attribute read on the parameter."""
    _built, _spells, steps, topologies = _shared_world()
    source, namespace = _shared_source(steps, topologies, ())

    assert "    c1 = meld._conduit_creations" in source
    assert "c1" not in namespace


def _adoption_world() -> Tuple[Counter, Tuple[SitePlanStep, ...], Dict[str, Any]]:
    """
    Root(s: S(a: D1, b: N, c: D2, t: T), limit=1) with S and T `unique_per_conduit`, D1 and D2 disposal-bearing.

    Step indexes: D1 0, N 1, D2 2, T 3, S 4, root 5. N is a `many` without disposal methods and T a shared site
    nested in S's miss; neither is adopted.
    """
    built: Counter = Counter()
    shared = Existence.unique_per_conduit
    spells = {
        "d1": _spell("d1", built, disposal=("close",)), "n": _spell("n", built),
        "d2": _spell("d2", built, disposal=("close",)), "t": _spell("t", built, shared),
        "s": _spell("s", built, shared), "root": _spell("root", built),
    }
    steps = (
        _step(("d1", 1), spells["d1"]),
        _step(("n", 2), spells["n"]),
        _step(("d2", 3), spells["d2"]),
        _step(("t", None), spells["t"]),
        _step(
            ("s", None), spells["s"],
            ("a", (("d1", 1),)), ("b", (("n", 2),)), ("c", (("d2", 3),)), ("t", (("t", None),)),
        ),
        _step(("root", 0), spells["root"], ("s", (("s", None),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "s", 0), _socket("root", "limit", 1, optional=True))),
        "s": SpellLocalTopology(
            "s", (_socket("s", "a", 0), _socket("s", "b", 1), _socket("s", "c", 2), _socket("s", "t", 3)),
        ),
    }
    return built, steps, topologies


def _function_source(source: str, name: str) -> str:
    """Return the source of one emitted function (`_miss4`, `_site_plan_executor`, ...) up to the next def."""
    return source.split(f"def {name}(")[1].split("\\ndef ")[0]


@pytest.mark.parametrize("keys", [(), ("limit",)], ids=["normal-key-set", "override-key-set"])
def test_a_miss_adopts_exactly_the_disposal_bearing_children_it_registered(keys: Tuple[str, ...]) -> None:
    """
    S's miss adopts D1 and D2 - in step order, after publishing S and before returning it - and nothing else: N has
    no disposal methods, T adopts nothing of its own, and the plan body never adopts (0.2.8238). An override key set
    that supplies none of S's parameters emits the same adoption.
    """
    _built, steps, topologies = _adoption_world()
    source, _namespace = _shared_source(steps, topologies, keys)

    adoption_lines = [line.strip() for line in source.splitlines() if "adopt_children" in line]
    assert adoption_lines == ["c4.adopt_children(sid4, v4, ((sid0, v0), (sid2, v2)))"]
    miss = _function_source(source, "_miss4")
    assert miss.index("c4._creations[sid4] = v4") < miss.index("c4.adopt_children(") < miss.index("return v4")
    assert "adopt_children" not in _function_source(source, "_miss3")
    assert "adopt_children" not in _function_source(source, SitePlanLowering.PLAN_FUNCTION_NAME)


def test_a_miss_hands_its_built_children_to_the_store_once_per_publication() -> None:
    """Run the plan: the store receives S and its two disposal-bearing children once; a warm meld adopts nothing."""
    built, steps, topologies = _adoption_world()
    plan = _compile_plan(steps, topologies, ("root", 0))
    store = FakeStore()
    meld = SimpleNamespace(_conduit_creations=store)

    first = plan(meld, {})
    plan(meld, {})

    held = first.args[0]
    values = list(held.args) + list(held.kwargs.values())
    children = {value.name: value for value in values}
    assert store.adoptions == [("s", held, (("d1", children["d1"]), ("d2", children["d2"])))]
    assert built == Counter({"d1": 1, "n": 1, "d2": 1, "t": 1, "s": 1, "root": 2})
''',
    ),
]

door_edits = [
    (
        '''    def add_creation(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                     disposal_methods: Optional[List[str]] = None) -> None:
        """Publish one singleton and record the disposal-bearing registration."""
        self._creations[key] = item
        self._events.append(("add_creation", key))


class ClusterFacade:
''',
        '''    def add_creation(self, key: str, item: Any, *, has_disposal_methods: bool = False,
                     disposal_methods: Optional[List[str]] = None) -> None:
        """Publish one singleton and record the disposal-bearing registration."""
        self._creations[key] = item
        self._events.append(("add_creation", key))

    def register_many(self, key: str, item: Any, disposal_methods: List[str]) -> None:
        """Record one disposal-bearing many registration (the hot verb emitted plans call)."""
        self._events.append(("register_many", key))

    def adopt_children(self, holder_key: str, holder: Any, children: Tuple[Tuple[str, Any], ...]) -> None:
        """Record one adoption an emitted miss made right after publishing its holder (0.2.8238)."""
        self._events.append(("adopt_children", holder_key))
        self.adoptions.append((holder_key, holder, children))


class ClusterFacade:
''',
    ),
    (
        '''        self._events: List[Event] = events
        self._creations: Dict[str, Any] = {}
        self._slot_guards: Dict[str, RecordingLock] = {}
''',
        '''        self._events: List[Event] = events
        self._creations: Dict[str, Any] = {}
        self._slot_guards: Dict[str, RecordingLock] = {}
        self.adoptions: List[Tuple[str, Any, Tuple[Tuple[str, Any], ...]]] = []
''',
    ),
    (
        '''def test_door_held_disposal_bearing_root_still_registers_through_add_creation() -> None:
    """A door-held root with disposal methods publishes through `add_creation` (cleaned-store refusal intact)."""
    world = World(Existence.unique_per_conduit, root_disposal=("close",))
    result = world.normal_plan("unique_per_conduit")(world.meld())
    assert world.events == CHILD_EVENTS + [("build", "root"), ("add_creation", "root")]
    assert world.conduit_store._creations["root"] is result
''',
        '''def test_door_held_disposal_bearing_root_still_registers_through_add_creation() -> None:
    """A door-held root with disposal methods publishes through `add_creation` (cleaned-store refusal intact)."""
    world = World(Existence.unique_per_conduit, root_disposal=("close",))
    result = world.normal_plan("unique_per_conduit")(world.meld())
    assert world.events == CHILD_EVENTS + [("build", "root"), ("add_creation", "root")]
    assert world.conduit_store._creations["root"] is result


def test_door_held_root_adopts_its_many_child_after_publishing_without_a_guard() -> None:
    """
    The door-held root's miss takes no guard, and its disposal-bearing many child is registered before the root is
    built and adopted right after the root is published (slotted_lifetime_ownership, 0.2.8238).
    """
    events: List[Event] = []
    store = RecordingStore(events)
    child = logging_spell("d", events, Existence.many, disposal=("close",))
    root = logging_spell("root", events, Existence.unique_per_conduit, disposal=("close",))
    steps = (plan_step(("d", 1), child), plan_step(("root", None), root, ("d", (("d", 1),))))
    topologies = {"root": SpellLocalTopology("root", (socket("root", "d", 0),))}
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=("root", None), steps=steps, topology_for=topologies.get,
    )
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=OverrideKeyResolver.resolve(graph, ()),
        root_instance_key=("root", None), root_spell_id="root", root_spell_name="root", arity=0,
        normal_mode=True, door_route_key="unique_per_conduit",
    )
    graph.cleanup()
    assert "with " not in source.split(f"def {SitePlanLowering.PLAN_FUNCTION_NAME}(")[0]
    exec(compile(source, "<test>", "exec"), namespace)
    plan = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]

    result = plan(SimpleNamespace(_conduit_creations=store, _spellspace_creations=None))

    assert events == [
        ("build", "d"), ("register_many", "d"), ("build", "root"), ("add_creation", "root"),
        ("adopt_children", "root"),
    ]
    built_child = next(value for value in list(result.args) + list(result.kwargs.values()) if value.name == "d")
    assert store.adoptions == [("root", result, (("d", built_child),))]
''',
    ),
]

component_edits = [
    (
        '''from melder.aether.conduit.creations.creations import Creations
''',
        '''from melder.aether.conduit.creations.creations import Creations, HolderDisposalEntry
''',
    ),
    (
        '''    - Ownership: the child is recorded in the store of the holder's owner, not in the melding scope's store.
''',
        '''    - Ownership: the child is recorded in the store of the holder's owner, not in the melding scope's store. Since
      0.2.8238 it is recorded with the holder itself (its `HolderDisposalEntry`) and leaves its spell's `many` bucket.
''',
    ),
    (
        '''def _recorded(store: Creations, child_id: str) -> List[Any]:
    """
    Return the Child objects one store records for disposal (its live `many` bucket for Child's spell id).

    Args:
        store: A conduit's or a spellspace's creations store.
        child_id: Child's spell id.

    Returns:
        List[Any]: A copy of the bucket; empty when the store records no Child.
    """
    return list(store._creations.get(child_id) or [])
''',
        '''def _bucket(store: Creations, child_id: str) -> List[Any]:
    """
    Return a copy of one store's live `many` bucket for Child's spell id (empty when it keeps none).

    Since 0.2.8238 a child built for a holder leaves this bucket once the holder is published (the holder's record
    adopts it), so the bucket holds only children that no holder owns.

    Args:
        store: A conduit's or a spellspace's creations store.
        child_id: Child's spell id.

    Returns:
        List[Any]: A copy of the bucket.
    """
    return list(store._creations.get(child_id) or [])


def _adopted(store: Creations, holder_id: str) -> List[Any]:
    """
    Return the children one store records with a holder, in build order (0.2.8238).

    Args:
        store: A conduit's or a spellspace's creations store.
        holder_id: The holder's spell id.

    Returns:
        List[Any]: The children of the holder's `HolderDisposalEntry`; empty when the store keeps no such record.
    """
    record = store._disposable_creations.get(holder_id)
    if not isinstance(record, HolderDisposalEntry):
        return []
    return [child for child, _methods in record.children]
''',
    ),
    (
        '''            assert _recorded(owner_store, child_id) == [child], "the holder's owner must record its child"
            if owner_store is not melding_store:
                assert child not in _recorded(melding_store, child_id), "the melding lesser must not record the child"
''',
        '''            assert _adopted(owner_store, holder_id) == [child], "the holder's owner must record its child"
            if owner_store is not melding_store:
                assert child not in _bucket(melding_store, child_id), "the melding lesser must not record the child"
''',
    ),
    (
        '''                assert _recorded(owner_store, child_id) == [child], "the holder's owner must record its child"
                if owner_store is not melding_store:
                    assert child not in _recorded(melding_store, child_id), (
''',
        '''                assert _adopted(owner_store, holder_id) == [child], "the holder's owner must record its child"
                if owner_store is not melding_store:
                    assert child not in _bucket(melding_store, child_id), (
''',
    ),
    (
        '''        assert _recorded(root._creations, child_id) == [held.child], "the root owns the unique holder's child"
        assert held.child not in _recorded(lesser._creations, child_id), "the lesser must not record the child"
''',
        '''        assert _adopted(root._creations, holder_id) == [held.child], "the root owns the unique holder's child"
        assert held.child not in _bucket(lesser._creations, child_id), "the lesser must not record the child"
''',
    ),
    (
        '''        assert _recorded(root._creations, child_id) == [first.child], "the root owns the unique holder's child"
''',
        '''        assert _adopted(root._creations, holder_id) == [first.child], "the root owns the unique holder's child"
''',
    ),
    (
        '''    book, child_id = _book(specialize=True)
    book.bind(spell=UniqueHolder, existence=Existence.unique, permissions="create")
''',
        '''    book, child_id = _book(specialize=True)
    holder_id = book.bind(spell=UniqueHolder, existence=Existence.unique, permissions="create")
''',
    ),
    (
        '''        assert _recorded(root._creations, child_id) == [held.child], "the root records only the holder's own child"
''',
        '''        assert _adopted(root._creations, holder_id) == [held.child], "the root records only the holder's own child"
        assert _bucket(root._creations, child_id) == [], "no stray child is recorded in the child spell's bucket"
''',
    ),
]

integration_edits = [
    (
        '''from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
''',
        '''from collections.abc import Iterator
from typing import Any, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import Creations, HolderDisposalEntry
''',
    ),
    (
        '''    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration
''',
        '''    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _adopted(store: Creations, holder_id: str) -> List[Any]:
    """
    Return the children one store records with a holder, in build order.

    Since 0.2.8238 a holder's `many` children leave their spell's bucket once the holder is published and live in
    the holder's disposal record (`HolderDisposalEntry`).

    Args:
        store: The creations store that holds the holder.
        holder_id: The holder's spell id.

    Returns:
        List[Any]: The adopted children; empty when the store keeps no record for the holder.
    """
    record = store._disposable_creations.get(holder_id)
    if not isinstance(record, HolderDisposalEntry):
        return []
    return [child for child, _methods in record.children]
''',
    ),
    (
        '''        assert list(owner._creations._creations.get(child_id) or []) == [first.child], (
''',
        '''        assert _adopted(owner._creations, holder_id) == [first.child], (
''',
    ),
    (
        '''        assert list(team_store._creations.get(child_id) or []) == [first.child], (
''',
        '''        assert _adopted(team_store, holder_id) == [first.child], (
''',
    ),
]

print("lowering", edit_tool.apply(LOWERING_UNIT, lowering_edits))
print("door", edit_tool.apply(DOOR_UNIT, door_edits))
print("component", edit_tool.apply(MANY_COMPONENT, component_edits))
print("integration", edit_tool.apply(MANY_INTEGRATION, integration_edits))
print("new", LIFETIME.name, CREATIONS_UNIT.name)
