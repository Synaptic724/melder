import pytest

from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_types.spell_types import SpellType


def test_ctor_rejects_missing_ids():
    with pytest.raises(ValueError):
        SpellSystemNode(None, "lineage")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        SpellSystemNode("sid", None)  # type: ignore[arg-type]


def test_ctor_normalizes_dependencies_and_metadata():
    node = SpellSystemNode(
        "sid",
        "lid",
        dependencies=["a", "b"],
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        conduit_id="cid",
        ward_id="wid",
        is_root=True,
    )
    assert node.dependencies == {"a", "b"}
    assert node.existence is Existence.unique
    assert node.spell_type is SpellType.SPELL
    assert node.conduit_id == "cid"
    assert node.ward_id == "wid"
    assert node.is_root is True


def test_dependencies_returns_copy():
    node = SpellSystemNode("sid", "lid", dependencies=["x"])
    deps = node.dependencies
    deps.add("y")
    assert "y" not in node.dependencies


def test_add_dependency_validates():
    node = SpellSystemNode("sid", "lid")
    node.add_dependency("a")
    assert node.dependencies == {"a"}
    with pytest.raises(ValueError):
        node.add_dependency(None)  # type: ignore[arg-type]


def test_add_dependencies_unions_and_skips_none():
    node = SpellSystemNode("sid", "lid", dependencies=["a"])
    node.add_dependencies(["a", "b", None])
    assert node.dependencies == {"a", "b"}
    with pytest.raises(ValueError):
        node.add_dependencies(None)  # type: ignore[arg-type]


def test_cleanup_clears_and_blocks_access():
    node = SpellSystemNode("sid", "lid", dependencies=["a"], is_root=True)
    node.cleanup()
    assert node._dependencies is None  # noqa: SLF001
    assert node.is_root is False
    # idempotent
    node.cleanup()
    with pytest.raises(RuntimeError):
        _ = node.spell_id
    with pytest.raises(RuntimeError):
        node.add_dependency("x")


def test_lineage_and_spell_id_accessors_return_values():
    node = SpellSystemNode("sid", "lid")
    assert node.spell_id == "sid"
    assert node.lineage_id == "lid"


def test_dependencies_initially_empty():
    node = SpellSystemNode("sid", "lid")
    assert node.dependencies == set()


def test_dependencies_does_not_share_internal_set():
    deps = ["a"]
    node = SpellSystemNode("sid", "lid", dependencies=deps)
    deps.append("b")
    assert node.dependencies == {"a"}


def test_add_dependencies_accepts_iterables():
    node = SpellSystemNode("sid", "lid")
    node.add_dependencies({"x", "y"})
    assert node.dependencies == {"x", "y"}


def test_metadata_can_be_overwritten_manually():
    node = SpellSystemNode("sid", "lid")
    node.existence = Existence.many
    node.spell_type = SpellType.METHOD
    node.conduit_id = "cid2"
    node.ward_id = "wid2"
    node.is_root = True
    assert node.existence is Existence.many
    assert node.spell_type is SpellType.METHOD
    assert node.conduit_id == "cid2"
    assert node.ward_id == "wid2"
    assert node.is_root is True
