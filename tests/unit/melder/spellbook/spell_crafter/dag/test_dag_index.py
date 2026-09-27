import pytest

from typing import Sequence

from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry


def _path_id(registry: PathRegistry, path: Sequence[str]) -> int:
    current = registry.root_path_id
    for segment in path:
        current = registry.extend_path(current, segment)
    return current


@pytest.mark.parametrize(
    "segments,expected",
    [
        (["a"], ("a",)),
        (["a", "b"], ("a", "b")),
        (["root", "child", "leaf"], ("root", "child", "leaf")),
        ([" spaced ", "trim "], (" spaced ", "trim ")),
        ([], ()),
    ],
)
def test_path_registry_materialize_variants(segments, expected):
    registry = PathRegistry()
    path_id = _path_id(registry, segments)
    assert registry.materialize_path(path_id) == expected


def test_path_registry_format_path_reuses_cached_value(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = PathRegistry()
    path_id = _path_id(registry, ("a", "b"))

    assert registry.format_path(path_id) == "a>b"
    call_counter = {"count": 0}
    original_materialize = PathRegistry.materialize_path

    def _counting_materialize(self: PathRegistry, requested_path_id: int):
        call_counter["count"] += 1
        return original_materialize(self, requested_path_id)

    monkeypatch.setattr(PathRegistry, "materialize_path", _counting_materialize)
    assert registry.format_path(path_id) == "a>b"
    assert registry.format_path(path_id) == "a>b"
    assert call_counter["count"] == 0


def test_resolve_path_id_treats_tuple_and_list_equally():
    registry = PathRegistry()
    path_id = _path_id(registry, ("a", "b"))
    assert registry.resolve_path_id(["a", "b"]) == path_id
    assert registry.resolve_path_id(("a", "b")) == path_id


