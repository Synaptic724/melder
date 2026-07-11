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
    cache.store_cached_item(
        "01AAA", {"checkpoint_id": "01AAA", "profile_name": "default"}
    )
    cache.store_cached_item(
        "01BBB", {"checkpoint_id": "01BBB", "profile_name": "default"}
    )
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


# --- Delta 3/4 coverage: system verbs over a dict-backed mesh ---------

import json

from melder.crystallizer.asset_management.asset_management_system import (
    AssetManagementSystem,
)
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.crystallizer.persistence.persistence_system import PersistenceSystem


def _dict_backed_configuration(rows):
    """
    Build a frozen handler configuration over one in-memory row store.

    Returns:
        ExternalPersistenceManagerConfiguration: Frozen, quartet-wired.
    """
    def store(kind, profile_name, unit_id, payload):
        rows[(kind, unit_id)] = (profile_name, json.dumps(payload))

    def fetch(kind, unit_id):
        row = rows.get((kind, unit_id))
        return json.loads(row[1]) if row is not None else None

    def list_units(kind, profile_name):
        return [
            unit_id
            for (row_kind, unit_id), (row_profile, _p) in rows.items()
            if row_kind == kind and row_profile == profile_name
        ]

    def delete(kind, unit_id):
        del rows[(kind, unit_id)]

    configuration = ExternalPersistenceManagerConfiguration()
    configuration.with_store_handler(store)
    configuration.with_fetch_handler(fetch)
    configuration.with_list_units_handler(list_units)
    configuration.with_delete_handler(delete)
    configuration.freeze()
    return configuration


@pytest.fixture()
def asset_system(cache_root):
    """
    One AssetManagementSystem over a bare record + dict-backed mesh.

    Returns:
        tuple: (system, rows) - the system plus its in-memory "DB".
    """
    rows = {}
    system = AssetManagementSystem(PersistenceSystem())
    system.configure_external_persistence_manager(
        _dict_backed_configuration(rows)
    )
    yield system, rows
    system.cleanup()


def test_graft_store_fetch_list_round_trip(asset_system):
    """
    Contract:
        A graft record ships under kind "index_graft" keyed by its own
        index_id, lists for its profile, and fetches back EQUAL through
        the version gate.
    """
    system, rows = asset_system
    record = RecordVersion.stamp({
        "graft_kind": "spell_index",
        "index_id": "01IDX",
        "index_payload": {},
        "members": {},
        "members_without_custody": [],
    })
    assert system.store_index_graft("default", record) == "01IDX"
    assert ("index_graft", "01IDX") in rows
    assert system.list_index_grafts("default") == ["01IDX"]
    assert system.fetch_index_graft("01IDX") == record


def test_store_index_graft_without_index_id_refuses(asset_system):
    """
    Contract:
        A record with no index_id raises ValueError naming the capture
        verb; nothing ships.
    """
    system, rows = asset_system
    with pytest.raises(ValueError, match="index_id"):
        system.store_index_graft("default", {"graft_kind": "spell_index"})
    assert rows == {}


def test_fetch_index_graft_gates_newer_major(asset_system):
    """
    Contract:
        A stored graft stamped with a NEWER record_version MAJOR refuses
        at fetch (reader gate law), telling the user to upgrade.
    """
    system, rows = asset_system
    rows[("index_graft", "01NEW")] = (
        "default",
        json.dumps({RecordVersion.KEY: "99.0.0", "index_id": "01NEW"}),
    )
    # check_readable's contract is ValueError (the reader-gate law; same
    # as from_cached_item) - the first draft asserted RuntimeError from
    # a wrong docstring on fetch_index_graft, fixed together.
    with pytest.raises(ValueError, match="99.0.0"):
        system.fetch_index_graft("01NEW")


def test_fetch_index_graft_miss_raises_keyerror(asset_system):
    """
    Contract:
        Fetching an absent graft is a loud KeyError naming the recovery
        verb, never a silent None.
    """
    system, _rows = asset_system
    with pytest.raises(KeyError, match="01GONE"):
        system.fetch_index_graft("01GONE")


def test_delete_formation_local_and_strict_remote_leg(asset_system):
    """
    Contract:
        include_remote=False deletes the cache file only;
        include_remote=True also drives the STRICT delete lane and
        reports remote_deleted=True.
    """
    system, rows = asset_system
    cache = CrystallizerCache()
    cache.store_formation("default", "alpha", {"formation_name": "alpha"})
    cache.store_formation("default", "beta", {"formation_name": "beta"})
    rows[("formation", "beta")] = ("default", json.dumps({"x": 1}))

    local_only = system.delete_formation("default", "alpha")
    assert local_only["remote_deleted"] is False

    both = system.delete_formation("default", "beta", include_remote=True)
    assert both["remote_deleted"] is True
    assert ("formation", "beta") not in rows
    assert cache.list_formation_names("default") == []
    cache.cleanup()


def test_delete_cached_checkpoint_passthrough(asset_system):
    """
    Contract:
        The system verb evicts exactly the named cached checkpoint via
        the cache's single-item delete.
    """
    system, _rows = asset_system
    cache = CrystallizerCache()
    cache.store_cached_item(
        "01CKP", {"checkpoint_id": "01CKP", "profile_name": "default"}
    )
    deleted_path = system.delete_cached_checkpoint("01CKP")
    assert "01CKP" in deleted_path
    assert cache.list_cached_item_ids() == []
    cache.cleanup()


def test_describe_external_interface_joins_live_presence(asset_system):
    """
    Contract:
        The emitted contract carries the static table PLUS this world's
        live manager presence; a manager-less system reports None.
    """
    system, _rows = asset_system
    described = system.describe_external_interface()
    assert described[RecordVersion.KEY] == RecordVersion.CURRENT
    assert described["unit_kinds"] == [
        "checkpoint", "formation", "index_graft", "emission",
    ]
    assert described["live_manager"] is not None

    bare = AssetManagementSystem(PersistenceSystem())
    assert bare.describe_external_interface()["live_manager"] is None
    bare.cleanup()


def test_delete_formation_remote_leg_refuses_without_manager(cache_root):
    """
    Contract:
        include_remote=True on a manager-less system raises a
        teach-grade RuntimeError naming the configure verb - AFTER the
        local delete already ran (local leg always executes first).
    """
    system = AssetManagementSystem(PersistenceSystem())
    cache = CrystallizerCache()
    cache.store_formation("default", "alpha", {"formation_name": "alpha"})
    with pytest.raises(RuntimeError, match="configure_external"):
        system.delete_formation("default", "alpha", include_remote=True)
    # The local leg ran before the refusal: the file is gone.
    assert cache.list_formation_names("default") == []
    cache.cleanup()
    system.cleanup()


def test_delete_formation_remote_leg_is_strict(cache_root):
    """
    Contract:
        A raising delete handler PROPAGATES (deletes are strict - a
        half-run trim must not lie); the local file is already gone.
        Setup goes through the PUBLIC registration surface only.
    """
    def broken_delete(kind, unit_id):
        raise ConnectionError("remote down")

    configuration = ExternalPersistenceManagerConfiguration()
    configuration.with_store_handler(lambda k, p, u, pay: None)
    configuration.with_fetch_handler(lambda k, u: None)
    configuration.with_list_units_handler(lambda k, p: [])
    configuration.with_delete_handler(broken_delete)
    configuration.freeze()
    system = AssetManagementSystem(PersistenceSystem())
    system.configure_external_persistence_manager(configuration)

    cache = CrystallizerCache()
    cache.store_formation("default", "gamma", {"formation_name": "gamma"})
    with pytest.raises(ConnectionError):
        system.delete_formation("default", "gamma", include_remote=True)
    assert cache.list_formation_names("default") == []
    cache.cleanup()
    system.cleanup()


def test_store_index_graft_refuses_without_store_lane(cache_root):
    """
    Contract:
        A manager-less system refuses graft storage loudly, naming the
        registration fluent; nothing partial happens.
    """
    system = AssetManagementSystem(PersistenceSystem())
    with pytest.raises(RuntimeError, match="with_store_handler"):
        system.store_index_graft("default", {"index_id": "01IDX"})
    system.cleanup()


def test_list_index_grafts_partitions_by_profile(asset_system):
    """
    Contract:
        Grafts list per recording profile: two profiles' grafts never
        bleed into each other's listings (the profile_name identity
        column is real).
    """
    system, _rows = asset_system
    record_a = RecordVersion.stamp({"index_id": "01AAA"})
    record_b = RecordVersion.stamp({"index_id": "01BBB"})
    system.store_index_graft("profile_a", record_a)
    system.store_index_graft("profile_b", record_b)
    assert system.list_index_grafts("profile_a") == ["01AAA"]
    assert system.list_index_grafts("profile_b") == ["01BBB"]


def test_delete_cached_item_handles_legacy_flat_layout(cache_root):
    """
    Contract:
        A pre-layout flat cache file (root/{id}.json, no profile
        folder) is deletable through the same verb - the legacy branch
        mirrors load_cached_item's tolerance.
    """
    import json as json_module
    cache_root.mkdir(parents=True)
    (cache_root / "01LEGACY.json").write_text(
        json_module.dumps({"checkpoint_id": "01LEGACY"}), encoding="utf-8"
    )
    cache = CrystallizerCache()
    deleted_path = cache.delete_cached_item("01LEGACY")
    assert "01LEGACY" in deleted_path
    assert cache.list_cached_item_ids() == []
    cache.cleanup()


def test_bootstrap_formation_reload_fluent_contract():
    """
    Contract:
        with_formation_reload is fluent (returns self), rejects
        non-bool input, and refuses after cleanup - the mesh-aware boot
        knob behaves exactly like its with_pull_remote sibling. The
        report-key behavior itself rides the pod-death integration
        lane on the owner's tree run.
    """
    from melder.crystallizer.crystal_loader_system.bootstrap_loader import (
        CrystallizerBootstrap,
    )
    builder = CrystallizerBootstrap()
    assert builder.with_formation_reload(False) is builder
    assert builder.with_formation_reload(True) is builder
    with pytest.raises(TypeError, match="formation_reload"):
        builder.with_formation_reload("yes")
    builder.cleanup()
    fresh = CrystallizerBootstrap()
    fresh.cleanup()
    with pytest.raises(RuntimeError):
        fresh.with_formation_reload(True)
