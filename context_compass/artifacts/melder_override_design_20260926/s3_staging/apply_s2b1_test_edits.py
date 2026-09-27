"""S2b-1 tests: nested shared misses in key-set plans - anchored edits.

Usage: python apply_s2b1_test_edits.py <tree_root> [--check]

Adds unit contracts to test_site_plan_lowering.py (stored shared sites skip their children, placement at the lowest
common context, sibling misses receive an outer shared value, a pinned supplied rule keeps P2 under a stored parent,
a miss builds its children before taking its guard and warm hits take no lock, generic steps inside a miss,
innermost-scope disposal inside a miss) and one component contract to
test_spellbook_component_override_key_set_plans.py (a warm override meld skips the many child of a stored shared
site). Each anchor must match exactly once or nothing is written.
Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

UNIT = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"
COMPONENT = "tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py"

UNIT_ANCHOR = '''

def test_conflict_guard_accepts_identity_and_equal_scalars_only() -> None:
'''
UNIT_NEW = '''

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
''' + UNIT_ANCHOR

KEEPER_ANCHOR = '''

@pytest.fixture
def book() -> Iterator[Spellbook]:
'''
KEEPER_NEW = '''

class Keeper:
    """Root over one shared store and a plain parameter."""

    def __init__(self, store: Store, limit: int = 3) -> None:
        """Count the build and keep the operands."""
        BUILT["Keeper"] += 1
        self.store = store
        self.limit = limit
''' + KEEPER_ANCHOR

COMPONENT_ANCHOR = '''

@FAMILIES
def test_bad_key_keeps_todays_text_and_is_retried(book: Spellbook, family: str) -> None:
'''
COMPONENT_NEW = '''

@CACHED
def test_warm_override_meld_skips_the_children_of_a_stored_shared_site(book: Spellbook, cached: bool) -> None:
    """With Store stored, an override meld builds only the root: Leaf, which only Store needs, is skipped (B2)."""
    conduit = _conjure(
        book, [(Leaf, Existence.many), (Store, Existence.unique_per_conduit), (Keeper, Existence.many)], Keeper, cached,
    )
    BUILT.clear()
    first = conduit.meld(Keeper, override={"limit": 1})
    second = conduit.meld(Keeper, override={"limit": 2})
    assert second.store is first.store and (first.limit, second.limit) == (1, 2)
    assert BUILT == Counter({"Leaf": 1, "Store": 1, "Keeper": 2})
''' + COMPONENT_ANCHOR

EDITS = {
    UNIT: [("replace", UNIT_ANCHOR, UNIT_NEW)],
    COMPONENT: [("replace", KEEPER_ANCHOR, KEEPER_NEW), ("replace", COMPONENT_ANCHOR, COMPONENT_NEW)],
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
