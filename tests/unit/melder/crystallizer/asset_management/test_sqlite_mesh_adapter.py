"""
First-party SQLite mesh adapter contract suite
(patch sqlite_mesh_adapter_2026_07_12).

The adapter is the first concrete storage behind the callables-first
mesh: these suites prove it satisfies MeshInterfaceContract's handler
semantics THROUGH the real ExternalPersistenceManager (the runtime
consumer), that data survives adapter re-construction (the pod-restart
story), and that the strict/lenient laws and the Cleanable contract
hold. Core never imports the adapter; these tests import it exactly the
way a user would.
"""

import json
import sqlite3

import pytest

from melder.crystallizer.asset_management.adapters.sqlite_mesh_adapter import (
    SqliteMeshAdapter,
)
from melder.crystallizer.asset_management.external_persistence_manager import (
    ExternalPersistenceManager,
)
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.crystallizer.asset_management.mesh_interface_contract import (
    MeshInterfaceContract,
)
from melder.crystallizer.persistence.record_version import RecordVersion


def _adapter_backed_manager(database_path):
    """
    Build one real manager whose four handlers are the SQLite adapter's,
    registered through the normal fluents via register_with.

    Returns:
        tuple[ExternalPersistenceManager, SqliteMeshAdapter]: The live
        manager and its backing adapter (caller cleans both).
    """
    adapter = SqliteMeshAdapter(str(database_path))
    configuration = ExternalPersistenceManagerConfiguration()
    adapter.register_with(configuration)
    configuration.freeze()
    return ExternalPersistenceManager(configuration), adapter


def test_adapter_round_trips_every_contract_kind_through_the_manager(tmp_path):
    """
    Purpose:
        Prove the adapter serves the full mesh through the REAL manager:
        every contract unit kind stores, fetches, lists, and deletes.
    Contract:
        - store/fetch round-trips the stamped payload losslessly.
        - list partitions by kind; delete removes exactly the named unit.
    """
    manager, adapter = _adapter_backed_manager(tmp_path / "mesh.sqlite3")
    try:
        for kind in MeshInterfaceContract.unit_kinds():
            payload = RecordVersion.stamp({"kind_probe": kind, "n": 1})
            assert manager.store_unit(
                kind, "default", f"unit-{kind}", payload
            ) is True
            assert manager.fetch_unit(kind, f"unit-{kind}") == payload
            assert manager.list_units(kind, "default") == [f"unit-{kind}"]
        for kind in MeshInterfaceContract.unit_kinds():
            manager.delete_unit(kind, f"unit-{kind}")
            assert manager.list_units(kind, "default") == []
    finally:
        manager.cleanup()
        adapter.cleanup()


def test_adapter_data_survives_reconstruction_pod_restart_story(tmp_path):
    """
    Purpose:
        Prove durability across adapter instances: a fresh adapter on the
        same file serves units stored by a previous one (the pod-restart
        lane the mesh exists for).
    Contract:
        - A second adapter/manager pair sees the first pair's units.
    """
    database_path = tmp_path / "mesh.sqlite3"
    payload = RecordVersion.stamp({"survives": True, "rows": [1, 2, 3]})
    manager_one, adapter_one = _adapter_backed_manager(database_path)
    try:
        manager_one.store_unit("checkpoint", "default", "01CKPT", payload)
    finally:
        manager_one.cleanup()
        adapter_one.cleanup()

    manager_two, adapter_two = _adapter_backed_manager(database_path)
    try:
        assert manager_two.fetch_unit("checkpoint", "01CKPT") == payload
        assert manager_two.list_units("checkpoint", "default") == ["01CKPT"]
    finally:
        manager_two.cleanup()
        adapter_two.cleanup()


def test_adapter_store_replaces_latest_write_wins(tmp_path):
    """
    Purpose:
        Verify replace-on-store: re-shipping one (kind, unit_id) keeps
        exactly one row carrying the latest payload (the record's
        replace-on-emit precedent at the storage layer).
    """
    adapter = SqliteMeshAdapter(str(tmp_path / "mesh.sqlite3"))
    try:
        adapter.store_unit("emission", "default", "01EVT", {"v": 1})
        adapter.store_unit("emission", "default", "01EVT", {"v": 2})
        assert adapter.fetch_unit("emission", "01EVT") == {"v": 2}
        assert adapter.list_units("emission", "default") == ["01EVT"]
    finally:
        adapter.cleanup()


def test_adapter_lists_partition_by_kind_and_profile_in_ulid_order(tmp_path):
    """
    Purpose:
        Verify list_units honors BOTH partitions (kind + profile) and
        returns lexicographic order (ULID order = age; retention passes
        delete oldest-first from this ordering).
    """
    adapter = SqliteMeshAdapter(str(tmp_path / "mesh.sqlite3"))
    try:
        adapter.store_unit("checkpoint", "default", "01B", {"n": 2})
        adapter.store_unit("checkpoint", "default", "01A", {"n": 1})
        adapter.store_unit("checkpoint", "other", "01C", {"n": 3})
        adapter.store_unit("formation", "default", "01D", {"n": 4})
        assert adapter.list_units("checkpoint", "default") == ["01A", "01B"]
        assert adapter.list_units("checkpoint", "other") == ["01C"]
        assert adapter.list_units("formation", "default") == ["01D"]
        assert adapter.list_units("checkpoint", "missing") == []
    finally:
        adapter.cleanup()


def test_adapter_fetch_miss_is_none_and_delete_miss_is_strict(tmp_path):
    """
    Purpose:
        Verify the contract's asymmetric miss semantics: fetch answers a
        plain None, while delete raises (retention must not lie).
    """
    adapter = SqliteMeshAdapter(str(tmp_path / "mesh.sqlite3"))
    try:
        assert adapter.fetch_unit("checkpoint", "missing") is None
        with pytest.raises(KeyError, match="strict"):
            adapter.delete_unit("checkpoint", "missing")
    finally:
        adapter.cleanup()


def test_adapter_payload_json_fidelity_with_version_stamp(tmp_path):
    """
    Purpose:
        Verify nested stamped payloads cross the storage boundary
        losslessly and the stored column is real JSON text (the contract
        payload column law), inspected directly via sqlite3.
    """
    database_path = tmp_path / "mesh.sqlite3"
    adapter = SqliteMeshAdapter(str(database_path))
    try:
        payload = RecordVersion.stamp(
            {"nested": {"deep": [1, 2, {"x": None}]}, "flag": True}
        )
        adapter.store_unit("index_graft", "default", "01IDX", payload)
        assert adapter.fetch_unit("index_graft", "01IDX") == payload

        connection = sqlite3.connect(str(database_path))
        try:
            stored_text = connection.execute(
                "SELECT payload FROM melder_mesh_units "
                "WHERE unit_id = '01IDX'"
            ).fetchone()[0]
        finally:
            connection.close()
        assert json.loads(stored_text) == payload
    finally:
        adapter.cleanup()


def test_adapter_constructor_refuses_bad_identity_inputs(tmp_path):
    """
    Purpose:
        Verify the teach-grade construction gates: empty path and
        non-identifier table names refuse (the identifier pattern is the
        injection guard - identifiers cannot be parameterized).
    """
    with pytest.raises(ValueError, match="database_path"):
        SqliteMeshAdapter("   ")
    with pytest.raises(ValueError, match="identifier"):
        SqliteMeshAdapter(
            str(tmp_path / "mesh.sqlite3"),
            table_name="bad-name; DROP TABLE",
        )


def test_adapter_cleanup_contract_and_describe(tmp_path):
    """
    Purpose:
        Verify the Cleanable contract: describe() answers while live,
        cleanup is idempotent, verbs refuse after cleanup, and the
        database FILE survives (it is the user's asset).
    """
    database_path = tmp_path / "mesh.sqlite3"
    adapter = SqliteMeshAdapter(str(database_path))
    adapter.store_unit("checkpoint", "default", "01CKPT", {"v": 1})
    described = adapter.describe()
    assert described["adapter"] == "sqlite_mesh_adapter"
    assert described["table_name"] == "melder_mesh_units"
    assert described[RecordVersion.KEY] == RecordVersion.CURRENT

    adapter.cleanup()
    adapter.cleanup()
    with pytest.raises(RuntimeError):
        adapter.fetch_unit("checkpoint", "01CKPT")

    survivor = SqliteMeshAdapter(str(database_path))
    try:
        assert survivor.fetch_unit("checkpoint", "01CKPT") == {"v": 1}
    finally:
        survivor.cleanup()


def test_adapter_register_with_wires_all_four_fluents(tmp_path):
    """
    Purpose:
        Verify register_with is exactly the public-fluent registration:
        the configuration reports every handler present, and the
        manager's delete lane (STRICT) surfaces the adapter's KeyError.
    """
    adapter = SqliteMeshAdapter(str(tmp_path / "mesh.sqlite3"))
    configuration = ExternalPersistenceManagerConfiguration()
    returned = adapter.register_with(configuration)
    assert returned is configuration
    configuration.freeze()
    manager = ExternalPersistenceManager(configuration)
    try:
        manager.store_unit("formation", "default", "form-1", {"v": 1})
        assert manager.fetch_unit("formation", "form-1") == {"v": 1}
        with pytest.raises(KeyError, match="strict"):
            manager.delete_unit("formation", "missing-unit")
    finally:
        manager.cleanup()
        adapter.cleanup()
