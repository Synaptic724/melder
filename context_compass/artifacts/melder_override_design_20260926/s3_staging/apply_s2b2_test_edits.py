"""S2b-2 tests: the runtime's normal plan is the normal lane - anchored edits.

Usage: python apply_s2b2_test_edits.py <tree_root> [--check]

test_site_plan_lowering.py: the runtime takes no inner executor (it compiles its normal plan at construction, which
the emit counts now include); payloads without a winning key run that plan; new contracts for normal-mode emission,
normal-plan B2 and unwrapped site-graph errors. test_spellbook_component_override_key_set_plans.py: a warm normal meld
skips the many child of a stored shared site, fresh and cached. test_generalized_cache_strategy_experiment.py: the
reload assertion checks the executor code cache the plans compile through. Each anchor must match exactly once or
nothing is written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

UNIT = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"
COMPONENT = "tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py"
EXPERIMENT = "tests/experimentation/test_generalized_cache_strategy_experiment.py"

EXP_IMPORT_OLD = '''from melder.aether.spellbook.spell_compiler.executor_factory_cache import (
    executor_factory_cache_size,
)
'''
EXP_IMPORT_NEW = '''from melder.aether.spellbook.spell_compiler.executor_code_cache import (
    executor_code_cache_stats,
)
from melder.aether.spellbook.spell_compiler.executor_factory_cache import (
    executor_factory_cache_size,
)
'''
EXP_ASSERT_OLD = '''        assert reloaded_overridden.leaf is live_plain.leaf

        assert executor_factory_cache_size() >= 1
'''
EXP_ASSERT_NEW = '''        assert reloaded_overridden.leaf is live_plain.leaf

        # Since S2b-2 (2026-09-26) both lanes run on the site-plan runtime, whose
        # plans are compiled once per source through the executor code cache.
        assert executor_code_cache_stats()["entries"] >= 1
'''

WORLD_OLD = '''    def runtime(self, inner: Optional[Callable[..., Any]] = None) -> SitePlanOverrideRuntime:
        """Build one override runtime over the steps."""
        root = self.spells["root"]
        root._spellbook = SimpleNamespace(
            _spell_system_states=SimpleNamespace(get_local_topology_by_id=self.topologies.get)
        )
        return SitePlanOverrideRuntime(
            steps=self.steps, root_spell=root, root_instance_key=("root", None),
            inner_no_overrides_executor=inner or (lambda meld: "normal"),
        )
'''
WORLD_NEW = '''    def runtime(self) -> SitePlanOverrideRuntime:
        """Build one site-plan runtime over the steps (it compiles its normal plan)."""
        root = self.spells["root"]
        root._spellbook = SimpleNamespace(
            _spell_system_states=SimpleNamespace(get_local_topology_by_id=self.topologies.get)
        )
        return SitePlanOverrideRuntime(
            steps=self.steps, root_spell=root, root_instance_key=("root", None),
        )
'''

PER_KEY_OLD = '''    """Repeated payloads with the same keys reuse one plan; a new key set compiles once."""
    calls = _count_emits(monkeypatch)
    world = World()
    runtime = world.runtime()
    for value in range(3):
        assert runtime.execute_with_overrides(None, {"limit": value}).args[2] == value
    runtime.execute_with_overrides(None, {"a": object()})
    assert calls["emit"] == 2
'''
PER_KEY_NEW = '''    """The normal plan compiles at construction; same keys reuse one plan; a new key set compiles once."""
    calls = _count_emits(monkeypatch)
    world = World()
    runtime = world.runtime()
    assert calls["emit"] == 1
    for value in range(3):
        assert runtime.execute_with_overrides(None, {"limit": value}).args[2] == value
    runtime.execute_with_overrides(None, {"a": object()})
    assert calls["emit"] == 3
'''

BAD_KEYS_OLD = '''        assert "No sockets found for override path 'nosuch'" in str(caught.value.__cause__)
    assert calls["emit"] == 0
'''
BAD_KEYS_NEW = '''        assert "No sockets found for override path 'nosuch'" in str(caught.value.__cause__)
    assert calls["emit"] == 1
'''

INNER_OLD = '''def test_runtime_runs_the_inner_executor_without_winning_operands() -> None:
    """`None` and an empty positional payload run the normal executor (B8)."""
    runtime = World().runtime(inner=lambda meld: ("normal", meld))
    assert runtime.execute_with_overrides("m", None) == ("normal", "m")
    assert runtime.execute_with_overrides("m", {"__args__": []}) == ("normal", "m")
    assert runtime.execute_with_overrides("m", {"__args__": None}) == ("normal", "m")
    runtime.cleanup()
'''
INNER_NEW = '''def test_runtime_runs_the_normal_plan_without_winning_operands() -> None:
    """`None`, `{}` and empty positional payloads run the normal plan, which builds the whole graph (B8)."""
    world = World()
    runtime = world.runtime()
    for payload in (None, {}, {"__args__": []}, {"__args__": None}):
        result = runtime.execute_with_overrides(None, payload)
        assert [arg.name for arg in result.args] == ["a", "b"] and result.args[0].args[0].name == "x"
    assert runtime.execute_normal(None).args[1].name == "b"
    assert world.built == Counter({"x": 5, "a": 5, "b": 5, "root": 5})
    runtime.cleanup()
'''

EVICT_OLD = '''    runtime.execute_with_overrides(None, {"limit": 1})
    assert calls["emit"] == 4
'''
EVICT_NEW = '''    runtime.execute_with_overrides(None, {"limit": 1})
    assert calls["emit"] == 5
'''

ROOT_OLD = '''def test_runtime_requires_a_root_step() -> None:
    """A runtime over steps without the root instance key is refused."""
    world = World()
    with pytest.raises(RuntimeError, match="no step for root instance"):
        SitePlanOverrideRuntime(
            steps=world.steps[:3], root_spell=world.spells["root"], root_instance_key=("root", None),
            inner_no_overrides_executor=lambda meld: None,
        )
'''
ROOT_NEW = '''def test_runtime_requires_a_root_step() -> None:
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
'''

COMPONENT_ANCHOR = '''

@FAMILIES
def test_bad_key_keeps_todays_text_and_is_retried(book: Spellbook, family: str) -> None:
'''
COMPONENT_NEW = '''

@CACHED
def test_warm_normal_meld_skips_the_children_of_a_stored_shared_site(book: Spellbook, cached: bool) -> None:
    """With Store stored, a normal meld builds only the root: Leaf, which only Store needs, is skipped (S2b-2)."""
    conduit = _conjure(
        book, [(Leaf, Existence.many), (Store, Existence.unique_per_conduit), (Keeper, Existence.many)], Keeper, cached,
    )
    BUILT.clear()
    first = conduit.meld(Keeper)
    second = conduit.meld(Keeper)
    assert second is not first and second.store is first.store
    assert BUILT == Counter({"Leaf": 1, "Store": 1, "Keeper": 2})
''' + COMPONENT_ANCHOR

EDITS = {
    UNIT: [
        ("replace", WORLD_OLD, WORLD_NEW),
        ("replace", PER_KEY_OLD, PER_KEY_NEW),
        ("replace", BAD_KEYS_OLD, BAD_KEYS_NEW),
        ("replace", INNER_OLD, INNER_NEW),
        ("replace", EVICT_OLD, EVICT_NEW),
        ("replace", ROOT_OLD, ROOT_NEW),
    ],
    COMPONENT: [("replace", COMPONENT_ANCHOR, COMPONENT_NEW)],
    EXPERIMENT: [("replace", EXP_IMPORT_OLD, EXP_IMPORT_NEW), ("replace", EXP_ASSERT_OLD, EXP_ASSERT_NEW)],
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
        if "inner_no_overrides_executor" in data:
            raise SystemExit(f"{rel}: stale inner executor argument left")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
