"""Unit contracts for PathRegistry member paths (collection members get their own child paths)."""

from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry


def test_member_paths_are_distinct_ids_with_the_same_text() -> None:
    """Two members of one collection parameter get two ids that format to the parameter name."""
    registry = PathRegistry()
    root = registry.root_path_id

    socket = registry.extend_path(root, "members")
    first = registry.extend_path(root, "members", member="a")
    second = registry.extend_path(root, "members", member="b")

    assert len({socket, first, second}) == 3
    assert registry.format_path(first) == registry.format_path(second) == registry.format_path(socket) == "members"
    assert registry.parent_id(first) == registry.parent_id(second) == root
    assert registry.depth(first) == registry.depth(second) == 1


def test_member_path_interning_is_stable() -> None:
    """The same (parent, segment, member) triple always returns the same id."""
    registry = PathRegistry()
    root = registry.root_path_id

    assert registry.extend_path(root, "members", member="a") == registry.extend_path(root, "members", member="a")
    assert registry.extend_path(root, "leaf") == registry.extend_path(root, "leaf", member=None)


def test_children_of_different_members_stay_distinct() -> None:
    """The same parameter below two members is two paths with one text."""
    registry = PathRegistry()
    root = registry.root_path_id
    first = registry.extend_path(root, "members", member="a")
    second = registry.extend_path(root, "members", member="b")

    first_leaf = registry.extend_path(first, "leaf")
    second_leaf = registry.extend_path(second, "leaf")

    assert first_leaf != second_leaf
    assert registry.materialize_path(first_leaf) == registry.materialize_path(second_leaf) == ("members", "leaf")
    assert registry.parent_id(first_leaf) == first
    assert registry.parent_id(second_leaf) == second


def test_resolve_path_id_follows_member_less_edges_only() -> None:
    """Name resolution finds the socket path, not a member path."""
    registry = PathRegistry()
    root = registry.root_path_id
    socket = registry.extend_path(root, "members")
    member = registry.extend_path(root, "members", member="a")
    registry.extend_path(member, "leaf")

    assert registry.resolve_path_id(("members",)) == socket
    assert registry.resolve_path_id(("members", "leaf")) is None


def test_clone_keeps_member_ids() -> None:
    """A cloned registry answers member lookups with the same ids."""
    registry = PathRegistry()
    root = registry.root_path_id
    member = registry.extend_path(root, "members", member="a")

    cloned = registry.clone()

    assert cloned.extend_path(root, "members", member="a") == member
    assert cloned.format_path(member) == "members"
