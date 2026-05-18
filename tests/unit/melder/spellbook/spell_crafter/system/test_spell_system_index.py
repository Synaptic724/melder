import pytest

from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_types.spell_types import SpellType


def _node(spell_id="s1", lineage_id="l1", deps=None, **kw):
    return SpellSystemNode(spell_id, lineage_id, dependencies=deps, **kw)


def test_get_node_validates_spell_id():
    index = SpellSystemIndex()
    with pytest.raises(ValueError):
        index.get_node(None)  # type: ignore[arg-type]


def test_upsert_and_get_node_roundtrip():
    index = SpellSystemIndex()
    node = _node()
    index.upsert_node(node)
    assert index.get_node("s1") is node
    assert index.nodes["s1"] is node


def test_upsert_validates_input():
    index = SpellSystemIndex()
    with pytest.raises(ValueError):
        index.upsert_node(None)  # type: ignore[arg-type]


def test_ensure_node_creates_and_merges_dependencies():
    index = SpellSystemIndex()
    created = index.ensure_node("s1", "l1", dependencies=["a"], is_root=True)
    assert created.dependencies == {"a"}
    assert created.is_root is True

    merged = index.ensure_node("s1", "l1", dependencies=["b"], is_root=False)
    # merged into existing
    assert merged is created
    assert merged.dependencies == {"a", "b"}
    assert merged.is_root is True  # original root flag preserved


def test_ensure_node_updates_metadata_when_present():
    index = SpellSystemIndex()
    created = index.ensure_node("s1", "l1")
    updated = index.ensure_node(
        "s1",
        "l1",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        conduit_id="cid",
        ward_id="wid",
        is_root=True,
    )
    assert updated is created
    assert created.existence is Existence.unique
    assert created.spell_type is SpellType.SPELL
    assert created.conduit_id == "cid"
    assert created.ward_id == "wid"
    assert created.is_root is True


def test_ensure_node_validates_ids():
    index = SpellSystemIndex()
    with pytest.raises(ValueError):
        index.ensure_node(None, "l1")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        index.ensure_node("s1", None)  # type: ignore[arg-type]


def test_iter_nodes_returns_copy():
    index = SpellSystemIndex()
    n = _node("s1", "l1")
    index.upsert_node(n)
    nodes_list = index.iter_nodes()
    assert nodes_list == [n]
    nodes_list.append(_node("s2", "l2"))
    # internal state unchanged
    assert list(index.nodes.values()) == [n]


def test_cleanup_cascades_and_blocks_access():
    index = SpellSystemIndex()
    n1 = _node("s1", "l1")
    index.upsert_node(n1)
    index.cleanup()
    assert not hasattr(index, '_nodes')
    assert n1._cleaned is True
    index.cleanup()  # idempotent
    with pytest.raises(RuntimeError):
        _ = index.nodes
    with pytest.raises(RuntimeError):
        index.upsert_node(_node())


def test_get_node_returns_none_when_missing():
    index = SpellSystemIndex()
    assert index.get_node("missing") is None


def test_upsert_replaces_existing_instance():
    index = SpellSystemIndex()
    n1 = _node("s1", "l1")
    n2 = _node("s1", "l1")
    index.upsert_node(n1)
    index.upsert_node(n2)
    assert index.nodes["s1"] is n2


def test_iter_nodes_empty_when_no_nodes():
    index = SpellSystemIndex()
    assert index.iter_nodes() == []


def test_nodes_property_returns_live_mapping():
    index = SpellSystemIndex()
    n1 = _node("s1", "l1")
    index.upsert_node(n1)
    mapping = index.nodes
    mapping["extra"] = n1  # mutate directly
    assert "extra" in index.nodes


def test_ensure_node_merges_multiple_metadata_updates():
    index = SpellSystemIndex()
    node = index.ensure_node("s1", "l1")
    index.ensure_node("s1", "l1", conduit_id="cidA")
    index.ensure_node("s1", "l1", ward_id="widA")
    index.ensure_node("s1", "l1", is_root=True)
    assert node.conduit_id == "cidA"
    assert node.ward_id == "widA"
    assert node.is_root is True
