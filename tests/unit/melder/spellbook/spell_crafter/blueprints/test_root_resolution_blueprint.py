import pytest

from typing import Optional, Sequence

from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)


def _path_id(registry: PathRegistry, path: Sequence[str]) -> int:
    """Mint `path` in `registry` and return its id."""
    current = registry.root_path_id
    for segment in path:
        current = registry.extend_path(current, segment)
    return current


def _make_blueprint(
    *,
    root_id: str = "root",
    lineage_id: str = "lineage",
    ordered: tuple[str, ...] = ("a", "b", "root"),
    path_registry: Optional[PathRegistry] = None,
) -> RootResolutionBlueprint:
    """Build a blueprint over a two-dependency DAG."""
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("a")
    dag.add_node("b")
    dag.add_node("root")
    dag.add_dependency("a", "root")
    dag.add_dependency("b", "root")
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=lineage_id,
        dag=dag,
        ordered_node_ids=ordered,
        path_registry=path_registry,
    )


def test_init_requires_root_id_and_dag() -> None:
    """A blueprint needs a root id and a DAG."""
    with pytest.raises(ValueError):
        RootResolutionBlueprint(None, "lineage", DirectedAcyclicWorkGraph())
    with pytest.raises(ValueError):
        RootResolutionBlueprint("root", "lineage", None)


def test_properties_return_metadata_and_the_supplied_registry() -> None:
    """Accessors return the constructor's values; a supplied PathRegistry is owned as given."""
    registry = PathRegistry()
    path_id = _path_id(registry, ("p",))
    bp = _make_blueprint(path_registry=registry)
    assert bp.root_spell_id == "root"
    assert bp.root_lineage_id == "lineage"
    assert bp.dag is not None
    assert bp.ordered_node_ids == ["a", "b", "root"]
    assert bp.path_registry is registry
    assert bp.path_registry.resolve_path_id(("p",)) == path_id


def test_defaults_create_a_fresh_registry_per_blueprint() -> None:
    """Without a registry each blueprint owns its own, holding only the root path."""
    first = _make_blueprint()
    second = _make_blueprint()
    assert first.path_registry is not second.path_registry
    assert first.path_registry.resolve_path_id(()) == first.path_registry.root_path_id
    assert first.path_registry.resolve_path_id(("p",)) is None


def test_cleanup_idempotent_and_cleans_owned_children() -> None:
    """Cleanup is idempotent and cleans the DAG and the PathRegistry it owns."""
    bp = _make_blueprint()
    dag = bp.dag
    registry = bp.path_registry
    bp.cleanup()
    bp.cleanup()
    with pytest.raises(RuntimeError):
        _ = bp.root_spell_id
    assert dag.cleaned is True
    assert registry.cleaned is True


def test_accessors_raise_after_cleanup() -> None:
    """Every accessor refuses a cleaned blueprint."""
    bp = _make_blueprint()
    bp.cleanup()
    with pytest.raises(RuntimeError):
        _ = bp.dag
    with pytest.raises(RuntimeError):
        _ = bp.ordered_node_ids
    with pytest.raises(RuntimeError):
        _ = bp.path_registry


def test_ordered_node_ids_returns_copy() -> None:
    """Mutating the returned order does not change the blueprint."""
    bp = _make_blueprint()
    ids = bp.ordered_node_ids
    ids.append("mutate")
    assert bp.ordered_node_ids == ["a", "b", "root"]
