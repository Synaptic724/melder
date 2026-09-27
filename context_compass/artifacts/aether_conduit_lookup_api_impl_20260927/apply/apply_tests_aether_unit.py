"""Step 4a of the aether_conduit_lookup_api lane: tests/unit/melder/aether/test_aether.py.

Migrates the private-helper and discovery tests to the *_root_* names, gives the Cloud stub a named
directory, and adds the resolver, retired-name, NAMED and LIVE contract tests.

Usage: python apply_tests_aether_unit.py <tree root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_util import replace_block

PATH = os.path.join(sys.argv[1], "tests/unit/melder/aether/test_aether.py")

IMPORT_OLD = '''from pathlib import Path
import pytest
'''
IMPORT_NEW = '''from pathlib import Path
from types import SimpleNamespace
import pytest
'''

STUB_INIT_OLD = '''        self._registry = {}
        self._conduit_clusters = {}
        self.frame_name = "default"
'''
STUB_INIT_NEW = '''        self._registry = {}
        self._conduit_clusters = {}
        self._named_conduits = {}
        self.frame_name = "default"
'''

STUB_GET_OLD = '''    def get_conduit_by_id(self, conduit_id: str):
        """Return one conduit by id from the backing frame."""
        conduit = self._frame_mock._conduits.get(conduit_id)
        if conduit is None:
            raise ValueError(f"Conduit with id {conduit_id} not found.")
        return conduit
'''
STUB_GET_NEW = '''    def get_conduit_by_id(self, conduit_id: str):
        """Return one conduit by id from the backing frame."""
        conduit = self._frame_mock._conduits.get(conduit_id)
        if conduit is None:
            raise ValueError(f"Conduit with id {conduit_id} not found.")
        return conduit

    def get_conduit_by_name(self, name: str):
        """Return one named scope from the stub's named directory, raising like ConduitCloud when missing."""
        conduit = self._named_conduits.get(name)
        if conduit is None:
            raise ValueError("Conduit with name {0} not found.".format(name))
        return conduit
'''

PRIVATE_OLD = '''def test_get_conduit_by_id(aether_with_mocks):
    """_get_conduit_by_id retrieves from frame dict."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    expected = MagicMock()
    frame_mock._conduits = {"target_id": expected}
    
    result = a._get_conduit_by_id("target_id")
    assert result is expected

def test_get_conduit_by_id_missing_raises(aether_with_mocks):
    """_get_conduit_by_id raises ValueError if missing."""
    a = aether_with_mocks
    a._default_frame._conduits = {}
    with pytest.raises(ValueError, match="not found"):
        a._get_conduit_by_id("missing")


def test_get_conduit_by_id_missing_custom_frame_raises(aether_with_mocks):
    """_get_conduit_by_id should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_conduit_by_id("missing", "missing_frame")

def test_get_conduit_by_name(aether_with_mocks):
    """_get_conduit_by_name resolves through the frame name registry."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    c1 = MagicMock()
    c1.name = "bob"
    c2 = MagicMock()
    c2.name = "alice"
    frame_mock._conduits = {"id1": c1, "id2": c2}
    frame_mock._conduit_ids_by_name = {"bob": "id1", "alice": "id2"}
    
    result = a._get_conduit_by_name("alice")
    assert result is c2

def test_get_conduit_by_name_missing_raises(aether_with_mocks):
    """_get_conduit_by_name raises ValueError if not found."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="not found"):
        a._get_conduit_by_name("nobody")


def test_get_conduit_by_name_missing_custom_frame_raises(aether_with_mocks):
    """_get_conduit_by_name should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_conduit_by_name("nobody", "missing_frame")
'''
PRIVATE_NEW = '''def test_get_root_conduit_by_id(aether_with_mocks):
    """_get_root_conduit_by_id retrieves from the frame's root registry."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    expected = MagicMock()
    frame_mock._conduits = {"target_id": expected}
    
    result = a._get_root_conduit_by_id("target_id")
    assert result is expected

def test_get_root_conduit_by_id_missing_raises(aether_with_mocks):
    """_get_root_conduit_by_id raises ValueError naming the id and the searched frame."""
    a = aether_with_mocks
    a._default_frame._conduits = {}
    with pytest.raises(ValueError, match="Root conduit with id 'missing' not found in frame 'default'"):
        a._get_root_conduit_by_id("missing")


def test_get_root_conduit_by_id_missing_custom_frame_raises(aether_with_mocks):
    """_get_root_conduit_by_id should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_root_conduit_by_id("missing", "missing_frame")

def test_get_root_conduit_by_name(aether_with_mocks):
    """_get_root_conduit_by_name resolves through the frame's root name registry."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    c1 = MagicMock()
    c1.name = "bob"
    c2 = MagicMock()
    c2.name = "alice"
    frame_mock._conduits = {"id1": c1, "id2": c2}
    frame_mock._conduit_ids_by_name = {"bob": "id1", "alice": "id2"}
    
    result = a._get_root_conduit_by_name("alice")
    assert result is c2

def test_get_root_conduit_by_name_missing_raises(aether_with_mocks):
    """_get_root_conduit_by_name raises ValueError naming the name and the searched frame."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="Root conduit with name 'nobody' not found in frame 'default'"):
        a._get_root_conduit_by_name("nobody")


def test_get_root_conduit_by_name_missing_custom_frame_raises(aether_with_mocks):
    """_get_root_conduit_by_name should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_root_conduit_by_name("nobody", "missing_frame")
'''

DISCOVERY_OLD = '''def test_aether_conduit_discovery_helpers_expose_frame_inventory(
        aether_with_mocks,
) -> None:
    """
    Verify the generic conduit-discovery helpers expose root-frame inventory.

    Returns:
        None.
    """
'''
DISCOVERY_NEW = '''def test_aether_root_conduit_lookups_expose_frame_root_inventory(
        aether_with_mocks,
) -> None:
    """
    Verify the root-named lookups answer over the frame's root registry.

    Returns:
        None.
    """
'''

ASSERTS_OLD = '''    assert a.list_conduit_ids() == ("c1", "c2")
    assert a.list_conduit_names() == ("alpha", "beta")
    assert a.count_conduits() == 2
    assert a.has_conduit_id("c1") is True
    assert a.has_conduit_name("alpha") is True
    assert a.find_conduit_id_by_name("beta") == "c2"
    assert a.get_conduit_by_id("c1") is conduit_a
    assert a.get_conduit_by_name("beta") is conduit_b


def test_aether_conduit_discovery_helpers_validate_custom_frame(
        aether_with_mocks,
) -> None:
    """
    Verify the generic conduit-discovery helpers fail clearly for missing frames.

    Returns:
        None.
    """
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a.list_conduit_ids("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.list_conduit_names("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.find_conduit_id_by_name("alpha", "missing_frame")
'''
ASSERTS_NEW = '''    assert a.list_root_conduit_ids() == ("c1", "c2")
    assert a.list_root_conduit_names() == ("alpha", "beta")
    assert a.count_root_conduits() == 2
    assert a.has_root_conduit_id("c1") is True
    assert a.has_root_conduit_id("c3") is False
    assert a.has_root_conduit_name("alpha") is True
    assert a.has_root_conduit_name("gamma") is False
    assert a.find_root_conduit_id_by_name("beta") == "c2"
    assert a.find_root_conduit_id_by_name("gamma") is None
    assert a.get_root_conduit_by_id("c1") is conduit_a
    assert a.get_root_conduit_by_name("beta") is conduit_b


def test_aether_root_conduit_lookups_validate_custom_frame(
        aether_with_mocks,
) -> None:
    """
    Verify the root-named lookups fail clearly for missing frames.

    Returns:
        None.
    """
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a.list_root_conduit_ids("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.list_root_conduit_names("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.count_root_conduits("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.has_root_conduit_id("c1", "missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.has_root_conduit_name("alpha", "missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.find_root_conduit_id_by_name("alpha", "missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.get_root_conduit_by_name("alpha", "missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.get_root_conduit_by_id("c1", "missing_frame")


@pytest.mark.parametrize("bad_frame", [None, 7, ["default"]], ids=["none", "int", "list"])
@pytest.mark.parametrize(
    ("method_name", "leading_args"),
    [
        ("list_root_conduit_ids", ()),
        ("list_root_conduit_names", ()),
        ("count_root_conduits", ()),
        ("has_root_conduit_id", ("c1",)),
        ("has_root_conduit_name", ("alpha",)),
        ("find_root_conduit_id_by_name", ("alpha",)),
        ("get_root_conduit_by_name", ("alpha",)),
        ("get_root_conduit_by_id", ("c1",)),
        ("get_conduit_by_name", ("alpha",)),
        ("get_conduit_by_id", ("c1",)),
    ],
)
def test_conduit_lookups_reject_non_string_frame_names(
        aether_with_mocks,
        method_name: str,
        leading_args: tuple,
        bad_frame: object,
) -> None:
    """
    Verify all ten conduit lookups raise TypeError naming themselves for a non-string frame.

    Returns:
        None.
    """
    lookup = getattr(aether_with_mocks, method_name)
    expected = (
        f"{method_name}: aetheric_frame_name must be a frame name string such as 'default'; "
        f"got {type(bad_frame).__name__}."
    )

    with pytest.raises(TypeError) as excinfo:
        lookup(*leading_args, bad_frame)

    assert str(excinfo.value) == expected


@pytest.mark.parametrize(
    "retired_name",
    [
        "list_conduit_ids",
        "list_conduit_names",
        "count_conduits",
        "has_conduit_id",
        "has_conduit_name",
        "find_conduit_id_by_name",
        "_get_conduit_by_name",
        "_get_conduit_by_id",
    ],
)
def test_retired_root_lookup_names_are_not_exposed(retired_name: str) -> None:
    """
    Verify the hard rename left no alias: the retired root-only names are gone from Aether.

    Returns:
        None.
    """
    assert not hasattr(Aether, retired_name)


def test_get_conduit_by_name_returns_named_scopes_from_the_frame_cloud(aether_with_mocks) -> None:
    """
    Verify get_conduit_by_name answers over the frame Cloud's named directory: roots and lessers alike.

    Returns:
        None.
    """
    a = aether_with_mocks
    root = MagicMock()
    lesser = MagicMock()
    a._default_frame._conduits = {"c1": root}
    a._default_frame._conduit_ids_by_name = {"alpha": "c1"}
    a._default_frame._conduit_cloud._named_conduits.update({"alpha": root, "group": lesser})

    assert a.get_conduit_by_name("alpha") is root
    assert a.get_conduit_by_name("group") is lesser
    assert a.get_conduit_by_name("group", "default") is lesser


def test_get_conduit_by_name_missing_names_the_frame(aether_with_mocks) -> None:
    """
    Verify a missing name raises ValueError naming the searched frame, without chaining the Cloud's error.

    Returns:
        None.
    """
    a = aether_with_mocks

    with pytest.raises(ValueError, match="Conduit with name 'nobody' not found in frame 'default'") as excinfo:
        a.get_conduit_by_name("nobody")

    assert excinfo.value.__cause__ is None
    assert excinfo.value.__suppress_context__ is True


def test_get_conduit_by_name_missing_custom_frame_raises(aether_with_mocks) -> None:
    """
    Verify get_conduit_by_name keeps the frame error for a custom frame that does not exist.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="Aetheric frame 'missing_frame' does not exist."):
        aether_with_mocks.get_conduit_by_name("alpha", "missing_frame")


def test_get_conduit_by_id_returns_a_root_from_the_frame_registry(aether_with_mocks) -> None:
    """
    Verify a root id is answered from the frame's root registry.

    Returns:
        None.
    """
    a = aether_with_mocks
    root = SimpleNamespace(_conduit_ward=None)
    a._default_frame._conduits = {"c1": root}

    assert a.get_conduit_by_id("c1") is root


def test_get_conduit_by_id_returns_a_lesser_found_under_any_root(aether_with_mocks) -> None:
    """
    Verify an id missing from the root registry is searched through every root's ward.

    Returns:
        None.
    """
    a = aether_with_mocks
    lesser = object()
    empty_ward = SimpleNamespace(_get_lesser_conduit=lambda conduit_id: None)
    holding_ward = SimpleNamespace(
        _get_lesser_conduit=lambda conduit_id: lesser if conduit_id == "lesser-1" else None
    )
    a._default_frame._conduits = {
        "r1": SimpleNamespace(_conduit_ward=empty_ward),
        "r2": SimpleNamespace(_conduit_ward=holding_ward),
    }

    assert a.get_conduit_by_id("lesser-1") is lesser


def test_get_conduit_by_id_skips_roots_whose_ward_is_gone(aether_with_mocks) -> None:
    """
    Verify a root whose ward hard teardown deleted, or whose ward is None, is skipped rather than fatal.

    Returns:
        None.
    """
    a = aether_with_mocks
    lesser = object()
    a._default_frame._conduits = {
        "torn-down": SimpleNamespace(),
        "leaf": SimpleNamespace(_conduit_ward=None),
        "holder": SimpleNamespace(
            _conduit_ward=SimpleNamespace(_get_lesser_conduit=lambda conduit_id: lesser),
        ),
    }

    assert a.get_conduit_by_id("lesser-1") is lesser


def test_get_conduit_by_id_walks_a_snapshot_of_the_root_registry(aether_with_mocks) -> None:
    """
    Verify a root-registry change during the walk (a concurrent conjure or cleanup) cannot break the lookup.

    The first root's ward removes the second root from the live registry, as a concurrent cleanup would;
    iterating the live dict instead of a snapshot would raise "dictionary changed size during iteration".

    Returns:
        None.
    """
    a = aether_with_mocks
    lesser = object()
    roots: dict = {}

    def remove_second_root(conduit_id: str) -> None:
        """Drop the second root from the live registry mid-walk and report no match."""
        roots.pop("r2", None)
        return None

    roots["r1"] = SimpleNamespace(_conduit_ward=SimpleNamespace(_get_lesser_conduit=remove_second_root))
    roots["r2"] = SimpleNamespace(_conduit_ward=SimpleNamespace(_get_lesser_conduit=lambda conduit_id: lesser))
    a._default_frame._conduits = roots

    assert a.get_conduit_by_id("lesser-1") is lesser
    assert "r2" not in roots


def test_get_conduit_by_id_missing_names_the_frame(aether_with_mocks) -> None:
    """
    Verify an id no live conduit carries raises ValueError naming the searched frame.

    Returns:
        None.
    """
    a = aether_with_mocks
    a._default_frame._conduits = {
        "r1": SimpleNamespace(_conduit_ward=SimpleNamespace(_get_lesser_conduit=lambda conduit_id: None)),
    }

    with pytest.raises(ValueError, match="Conduit with id 'ghost' not found in frame 'default'"):
        a.get_conduit_by_id("ghost")


def test_get_conduit_by_id_missing_custom_frame_raises(aether_with_mocks) -> None:
    """
    Verify get_conduit_by_id keeps the frame error for a custom frame that does not exist.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="Aetheric frame 'missing_frame' does not exist."):
        aether_with_mocks.get_conduit_by_id("c1", "missing_frame")
'''

print("import:", replace_block(PATH, IMPORT_OLD, IMPORT_NEW))
print("stub init:", replace_block(PATH, STUB_INIT_OLD, STUB_INIT_NEW))
print("stub get:", replace_block(PATH, STUB_GET_OLD, STUB_GET_NEW))
print("private:", replace_block(PATH, PRIVATE_OLD, PRIVATE_NEW))
print("discovery:", replace_block(PATH, DISCOVERY_OLD, DISCOVERY_NEW))
print("asserts:", replace_block(PATH, ASSERTS_OLD, ASSERTS_NEW))
