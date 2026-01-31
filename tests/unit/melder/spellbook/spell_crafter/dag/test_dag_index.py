import pytest

from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _ref(node: str, name: str, path):
    return SocketRef(node, name, tuple(path), SocketKind.NORMAL)


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
def test_path_key_variants(segments, expected):
    assert DagIndex._path_key(segments) == expected


@pytest.mark.parametrize(
    "path",
    [
        ("missing",),
        ("a", "b"),
        (),
    ],
)
def test_get_by_exact_path_missing_returns_empty(path):
    index = DagIndex()
    assert index.get_by_exact_path(path) == []


@pytest.mark.parametrize("name", ["missing", "shared", ""])
def test_get_by_name_missing_returns_empty(name):
    index = DagIndex()
    assert index.get_by_name(name) == []


def test_getters_return_copies_not_internal_lists():
    index = DagIndex()
    ref = _ref("n1", "p", ("p",))
    index.add_socket(ref)

    by_name = index.get_by_name("p")
    by_name.append(_ref("n2", "p", ("other",)))

    again = index.get_by_name("p")
    assert again == [ref]
    assert index.get_by_exact_path(("p",)) == [ref]


def test_multiple_sockets_by_name_and_path_separation():
    index = DagIndex()
    first = _ref("n1", "shared", ("a",))
    second = _ref("n2", "shared", ("b",))
    index.add_socket(first)
    index.add_socket(second)

    assert index.get_by_exact_path(("a",)) == [first]
    assert index.get_by_exact_path(("b",)) == [second]
    assert set(index.get_by_name("shared")) == {first, second}


def test_add_socket_same_reference_duplicates_in_lookup_lists():
    index = DagIndex()
    ref = _ref("n1", "p", ("p",))
    index.add_socket(ref)
    index.add_socket(ref)

    # get_by_* preserve duplicates; iter_all_sockets dedupes
    assert index.get_by_exact_path(("p",)) == [ref, ref]
    assert index.get_by_name("p") == [ref, ref]
    assert list(index.iter_all_sockets()) == [ref]


def test_add_socket_order_preserved_by_path_and_name():
    index = DagIndex()
    first = _ref("n1", "p", ("p",))
    second = _ref("n2", "p", ("p",))
    index.add_socket(first)
    index.add_socket(second)

    assert index.get_by_exact_path(("p",)) == [first, second]
    assert index.get_by_name("p") == [first, second]


def test_add_socket_allows_empty_path_segments():
    index = DagIndex()
    ref = _ref("n1", "root", tuple())
    index.add_socket(ref)
    assert index.get_by_exact_path(tuple()) == [ref]
    assert index.get_by_name("root") == [ref]


def test_cleanup_idempotent_and_blocks_further_usage():
    index = DagIndex()
    index.add_socket(_ref("n1", "p", ("p",)))

    index.cleanup()
    index.cleanup()

    assert index.cleaned is True
    assert index._by_exact_path is None
    with pytest.raises(AttributeError):
        index.get_by_name("p")


def test_iter_all_sockets_unique_across_entries():
    index = DagIndex()
    first = _ref("n1", "p1", ("x",))
    second = _ref("n2", "p2", ("x",))
    index.add_socket(first)
    index.add_socket(second)

    assert set(index.iter_all_sockets()) == {first, second}


def test_iter_all_sockets_handles_shared_name_and_path_overlap():
    index = DagIndex()
    a1 = _ref("a1", "shared", ("x",))
    a2 = _ref("a2", "shared", ("x",))
    b1 = _ref("b1", "other", ("x",))
    for ref in (a1, a2, b1):
        index.add_socket(ref)
    assert set(index.iter_all_sockets()) == {a1, a2, b1}


def test_iter_all_sockets_empty_on_fresh_index():
    assert list(DagIndex().iter_all_sockets()) == []


def test_get_by_exact_path_does_not_mutate_internal_store():
    index = DagIndex()
    ref = _ref("n1", "p", ("p",))
    index.add_socket(ref)
    result = index.get_by_exact_path(("p",))
    result.clear()
    assert index.get_by_exact_path(("p",)) == [ref]


def test_get_by_name_does_not_mutate_internal_store():
    index = DagIndex()
    ref = _ref("n1", "p", ("p",))
    index.add_socket(ref)
    result = index.get_by_name("p")
    result.clear()
    assert index.get_by_name("p") == [ref]


def test_add_socket_after_cleanup_raises_due_to_cleared_maps():
    index = DagIndex()
    index.cleanup()
    with pytest.raises(AttributeError):
        index.add_socket(_ref("n1", "p", ("p",)))


def test_get_after_cleanup_raises_attribute_error():
    index = DagIndex()
    index.add_socket(_ref("n1", "p", ("p",)))
    index.cleanup()
    with pytest.raises(AttributeError):
        index.get_by_exact_path(("p",))
    with pytest.raises(AttributeError):
        index.iter_all_sockets().__iter__().__next__()


def test_path_key_treats_tuple_and_list_equally():
    assert DagIndex._path_key(["a", "b"]) == DagIndex._path_key(("a", "b"))


@pytest.mark.parametrize(
    "paths,names,expected_count",
    [
        ([("a",)], ["p"], 1),
        ([("a",), ("a",)], ["p", "p"], 2),
        ([("a",), ("b",)], ["p", "p"], 2),
        ([("a",), ("a", "b")], ["x", "y"], 2),
    ],
)
def test_iter_all_sockets_counts_unique_refs(paths, names, expected_count):
    index = DagIndex()
    for i, (path, name) in enumerate(zip(paths, names)):
        index.add_socket(_ref(f"n{i}", name, path))
    assert len(list(index.iter_all_sockets())) == expected_count


def test_get_by_exact_path_with_repeated_segments():
    index = DagIndex()
    ref = _ref("n1", "p", ("a", "a", "b"))
    index.add_socket(ref)
    assert index.get_by_exact_path(("a", "a", "b")) == [ref]
    assert index.get_by_exact_path(("a", "b")) == []


def test_get_by_name_is_case_sensitive():
    index = DagIndex()
    lower = _ref("n1", "name", ("p",))
    upper = _ref("n2", "Name", ("p2",))
    index.add_socket(lower)
    index.add_socket(upper)
    assert index.get_by_name("name") == [lower]
    assert index.get_by_name("Name") == [upper]


def test_iter_all_sockets_after_get_calls_still_dedupes():
    index = DagIndex()
    ref = _ref("n1", "p", ("p",))
    index.add_socket(ref)
    # call getters first
    index.get_by_exact_path(("p",))
    index.get_by_name("p")
    assert list(index.iter_all_sockets()) == [ref]


def test_get_by_exact_path_returns_all_matching_sockets_same_path():
    index = DagIndex()
    a = _ref("n1", "a", ("shared",))
    b = _ref("n2", "b", ("shared",))
    index.add_socket(a)
    index.add_socket(b)
    assert index.get_by_exact_path(("shared",)) == [a, b]


def test_add_socket_supports_longer_paths():
    index = DagIndex()
    ref = _ref("n1", "deep", ("a", "b", "c"))
    index.add_socket(ref)
    assert index.get_by_exact_path(("a", "b", "c")) == [ref]
    assert index.get_by_name("deep") == [ref]
