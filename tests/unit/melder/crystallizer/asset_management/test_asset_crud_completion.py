"""
Unit tests for the asset CRUD completion lane (2026-07-11): the
self-describing MeshInterfaceContract and the two new cache delete
verbs (single checkpoint evict + formation delete).

All cache tests redirect the cache root to a pytest tmp_path - the real
root under src/melder/__melder_cache__ is never touched.
"""
import pytest

from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
from melder.crystallizer.asset_management.mesh_interface_contract import (
    MeshInterfaceContract,
)
from melder.crystallizer.persistence.record_version import RecordVersion


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """
    Redirect the cache root to an isolated temporary directory.

    Returns:
        Path: The redirected root.
    """
    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def test_contract_describe_is_stamped_and_complete():
    """
    Contract:
        describe() carries the RecordVersion stamp, all four unit kinds
        in declaration order, the four identity columns, and one shape
        row per kind.
    """
    payload = MeshInterfaceContract.describe()
    assert payload[RecordVersion.KEY] == RecordVersion.CURRENT
    assert payload["unit_kinds"] == [
        "checkpoint", "formation", "index_graft", "emission",
    ]
    assert set(payload["identity_columns"]) == {
        "kind", "profile_name", "unit_id", "payload",
    }
    assert set(payload["payload_shapes"]) == set(payload["unit_kinds"])


def test_contract_shape_rows_mirror_real_producers():
    """
    Contract:
        Each kind's key inventory names record_version plus the keys its
        REAL producer emits (checkpoint = to_cached_item, formation =
        capture_formation_record, emission = the tap envelope).
    """
    shapes = MeshInterfaceContract.describe()["payload_shapes"]
    assert "captured_payloads" in shapes["checkpoint"]["keys"]
    assert "journal_segment" in shapes["checkpoint"]["keys"]
    assert "payloads" in shapes["formation"]["keys"]
    assert "scope" in shapes["formation"]["keys"]
    assert shapes["index_graft"]["keys"][1] == "graft_kind"
    assert shapes["emission"]["keys"] == [
        "record_version", "crystal_kind", "payload",
    ]
    for row in shapes.values():
        assert row["keys"][0] == "record_version"


def test_contract_handler_signatures_name_registration_fluents():
    """
    Contract:
        Every handler row carries its registration fluent name and arg
        order, so a user can register callables from the emitted
        contract alone (the interface-layer promise).
    """
    signatures = MeshInterfaceContract.describe()["handler_signatures"]
    assert signatures["store_unit"]["register_as"] == "with_store_handler"
    assert signatures["store_unit"]["args"] == [
        "kind", "profile_name", "unit_id", "payload",
    ]
    assert signatures["fetch_unit"]["args"] == ["kind", "unit_id"]
    assert signatures["list_units"]["args"] == ["kind", "profile_name"]
    assert signatures["delete_unit"]["register_as"] == "with_delete_handler"


def test_contract_describe_returns_detached_copies():
    """
    Contract:
        Mutating one describe() result never leaks into the class-level
        authority or later calls.
    """
    first = MeshInterfaceContract.describe()
    first["unit_kinds"].append("bogus")
    first["identity_columns"]["kind"] = "mutated"
    second = MeshInterfaceContract.describe()
    assert "bogus" not in second["unit_kinds"]
    assert second["identity_columns"]["kind"] != "mutated"


def test_delete_cached_item_removes_only_the_target(cache_root):
    """
    Contract:
        delete_cached_item unlinks exactly the named id (profile-scoped
        layout) and leaves neighbours loadable.
    """
    cache = CrystallizerCache()
    cache.store_cached_item("default", "01AAA", {"checkpoint_id": "01AAA"})
    cache.store_cached_item("default", "01BBB", {"checkpoint_id": "01BBB"})
    deleted_path = cache.delete_cached_item("01AAA")
    assert "01AAA" in deleted_path
    assert cache.list_cached_item_ids() == ["01BBB"]
    assert cache.load_cached_item("01BBB")["checkpoint_id"] == "01BBB"
    cache.cleanup()


def test_delete_cached_item_miss_raises_teach_grade_keyerror(cache_root):
    """
    Contract:
        A miss raises KeyError naming the id and the recovery verb;
        nothing is deleted.
    """
    cache = CrystallizerCache()
    with pytest.raises(KeyError, match="01ZZZ"):
        cache.delete_cached_item("01ZZZ")
    cache.cleanup()


def test_delete_formation_removes_the_named_file_only(cache_root):
    """
    Contract:
        delete_formation unlinks <profile>/__formations__/<name>.json
        and leaves sibling formations listable.
    """
    cache = CrystallizerCache()
    cache.store_formation("default", "alpha", {"formation_name": "alpha"})
    cache.store_formation("default", "beta", {"formation_name": "beta"})
    deleted_path = cache.delete_formation("default", "alpha")
    assert "alpha.json" in deleted_path
    assert cache.list_formation_names("default") == ["beta"]
    cache.cleanup()


def test_delete_formation_miss_raises_teach_grade_keyerror(cache_root):
    """
    Contract:
        A missing formation raises KeyError naming formation + profile;
        the profile's other formations are untouched.
    """
    cache = CrystallizerCache()
    cache.store_formation("default", "keeper", {"formation_name": "keeper"})
    with pytest.raises(KeyError, match="ghost"):
        cache.delete_formation("default", "ghost")
    assert cache.list_formation_names("default") == ["keeper"]
    cache.cleanup()
